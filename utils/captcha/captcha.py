__credit__ = "himangshu147-git"
__author__ = "https://github.com/himangshu147-git"

import random
import string
from PIL import Image, ImageDraw, ImageFont
import io

def generate_captcha():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_captcha_image(text):
    font = ImageFont.truetype(r"D:\himangshu\Projects\geeek\utils\captcha\roboto-bold.ttf", 30)

    letter_widths = [font.getbbox(letter)[2] for letter in text]
    max_height = max(font.size for _ in text)
    image = Image.new("RGB", (203, max_height), "white")
    draw = ImageDraw.Draw(image)
    
    max_letter_spacing = 5
    min_letter_spacing = 1
    cloudiness_intensity = 0.03
    salt_pepper_density = 0.1
    salt_pepper_intensity = 0.1
    num_lines = 6
    # line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) 
    num_spots = 50
    spot_size = 3
    width, height = image.size
    pixels = image.load()
    num_pixels = int(width * height * salt_pepper_density)
    x = 0
    
    for i, letter in enumerate(text):
        angle = random.randint(-45, 45)
        letter_image = Image.new("RGBA", (letter_widths[i], max_height), (255, 255, 255, 0))
        letter_draw = ImageDraw.Draw(letter_image)
        letter_draw.text((0, 0), letter, font=font, fill=(random.randint(0, 90), random.randint(0, 90), random.randint(0, 90)))
        rotated_letter_image = letter_image.rotate(angle, resample=Image.BILINEAR, expand=True)
        letter_width, letter_height = rotated_letter_image.size
        y = (max_height - letter_height) // 2
        image.paste(rotated_letter_image, (x, y), mask=rotated_letter_image)
        x += letter_width + random.randint(min_letter_spacing, max_letter_spacing)

    for x in range(width):
        for y in range(height):
            noise = random.randint(-50, 50)
            r, g, b = pixels[x, y]
            r += noise
            g += noise
            b += noise
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pixels[x, y] = (r, g, b)

    for _ in range(int(width * height * cloudiness_intensity)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        gray_value = random.randint(0, 255)
        draw.point((x, y), fill=(gray_value, gray_value, gray_value))

    for _ in range(num_pixels):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if random.random() < 0.5:
            draw.point((x, y), fill=(255, 255, 255))
        else:
            noise = random.randint(0, int(255 * salt_pepper_intensity))
            draw.point((x, y), fill=(noise, noise, noise))

    for _ in range(num_lines):
        line_color = (random.randint(0, 25), random.randint(0, 25), random.randint(0, 25))
        start_x = random.randint(0, width - 1)
        start_y = random.randint(0, height - 1)
        end_x = random.randint(0, width - 1)
        end_y = random.randint(0, height - 1)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=line_color, width=0)

    for _ in range(num_spots):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        spot_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        spot_bbox = (x - spot_size // 2, y - spot_size // 2, x + spot_size // 2, y + spot_size // 2)
        draw.ellipse(spot_bbox, fill=spot_color)

    return image, text


def generate():
    image, text = generate_captcha_image(generate_captcha())
    byte_stream = io.BytesIO()
    image.save(byte_stream, format="PNG")
    byte_stream.seek(0)
    image_bytes = byte_stream.getvalue()
    return image_bytes, text

# def image():
#     image = generate_captcha_image(generate_captcha())
#     byte_stream = io.BytesIO()
#     image[0].save(r"D:\himangshu\Projects\geeek\utils\captcha\c.png", format="PNG")

# image()