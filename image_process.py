from PIL import Image
import io

def compress_image(image_data, max_size_in_kb=1024):
    max_size = max_size_in_kb * 1024
    image = Image.open(io.BytesIO(image_data))

    if image.mode == "RGBA":
        image = image.convert("RGB")

    original_width, original_height = image.size

    def new_size(width, height, max_demension):
        max_width, max_height = max_demension
        if width <= max_width and height <= max_height:
            return width, height
        aspect_ratio = width / height
        if width > height:
            new_width = max_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)
        return new_width, new_height
    
    new_width, new_height = new_size(original_width, original_height, max_demension=(1024, 1024))

    if new_width != original_width or new_height != original_height:
        image = image.resize((new_width, new_height), Image.LANCZOS)
    
    quality = 95
    output_stream = io.BytesIO()

    while True:
        image.save(output_stream, format='JPEG', quality=quality)
        if output_stream.tell() <= max_size:
            break
        quality -= 5
        output_stream.seek(0)
        output_stream.truncate()
    
    compressed_data = output_stream.getvalue()
    output_stream.close()
    return compressed_data

def process_image(image_data):
    max_size = 1024 * 1024

    if len(image_data) > max_size:
        compressed_data = compress_image(image_data, max_size_in_kb=1024)
        return compressed_data
    else:
        return image_data