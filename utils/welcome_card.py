import io
import os

import discord
import html2image
import random
from PIL import Image

html = """
<!DOCTYPE html>
<html>
<head>
  <title>Discord Welcome Image</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #000000;
      color: #FFFFFF;
      text-align: center;
      padding-top: 0px;
    }}
    
    .container {{
      margin-bottom: 1px;
      max-width: 600px;
      max-height: 300px;
      margin: 0 auto;
      background-image: linear-gradient(45deg, {color1}, {color2}, {color3});
      border-radius: 8px;
      padding: 20px;
      box-sizing: border-box;
      display: flex;
      align-items: center;
    }}
    
    .avatar {{
      width: 150px;
      height: 150px;
      border-radius: 50%;
      margin-right: 20px;
    }}
    
    .message {{
      font-size: 18px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <img src="{avatar}" alt="User Avatar" class="avatar">
    <div class="message">
      <h2>Welcome to Pythonic</h2>
      <p>We're glad to have you here.</p>
      <p>Enjoy your stay and have fun!</p>
    </div>
  </div>
</body>
</html>
"""

async def welcome_card(member: discord.Member):
    number_of_colors = 3
    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]
    avatar_url = str(member.display_avatar.url)
    h2i = html2image.Html2Image()
    file = f"welcome_{member.id}.png"
    h2i.screenshot(
        html_str=html.format(member=member.name, avatar=avatar_url, color1=color[0], color2=color[1], color3=color[2]), 
        size=(600, 210),
        save_as=file
        )
    pil = Image.open(file)
    img_io = io.BytesIO()
    pil.save(img_io, format="PNG")
    img_io.seek(0)
    pil.close()
    os.remove(file)
    return img_io