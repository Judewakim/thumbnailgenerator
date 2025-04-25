from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import boto3
import os
import io

s3 = boto3.client('s3')

# Font path and size for text overlay is detailed in a Lambda layer
FONT_PATH = "/opt/impactall.ttf" 
FONT_SIZE = 64

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']
    
    try:
        # Get metadata (for custom text)
        head = s3.head_object(Bucket=bucket, Key=key)
        text = head.get("Metadata", {}).get("text", "Your Title Here")

        # Download image
        original_image = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
        try:
            image = Image.open(io.BytesIO(original_image)).convert("RGB")
        
        except UnidentifiedImageError:
            return {
                'statusCode': 400,
                'body': 'The uploaded file is not a valid image.'
            }
    
        # Resize to 1280x720
        image.thumbnail((1280, 720))

        # Creates a black canvas that is always 1280xx720
        canvas = Image.new('RGB', (1280, 720), (0, 0, 0)) 
        # Paste the resized image on the center of the black canvas
        canvas.paste(image, ((1280 - image.width) // 2, (720 - image.height) // 2))

        # ImageDraw.Draw lets you draw shapes, lines, or text onto a Pillow image
        draw = ImageDraw.Draw(canvas)

        # Apply translucent black overlay for contrast 
        # (later will improve this logic to make it dynamic)
        overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 100))
        canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay)

        # Load font
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        # Text placement
        text_position = (50, 600)
        draw = ImageDraw.Draw(canvas)
        draw.text(text_position, text, font=font, fill='white')

        # Save final output
        output = io.BytesIO()
        canvas.convert("RGB").save(output, format='JPEG')
        output.seek(0)
        
        # Upload to processed bucket
        processed_key = f"processed-{key}"
        processed_bucket = 'something-processed-related'
        s3.upload_fileobj(output, processed_bucket, processed_key, ExtraArgs={'ContentType': 'image/jpeg'})
        
        # Generate presigned URL
        url = s3.generate_presigned_url('get_object', Params={
            'Bucket': processed_bucket,
            'Key': processed_key
        }, ExpiresIn=3600)

        return {
            'statusCode': 200,
            'body': url
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }