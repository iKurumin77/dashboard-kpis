from PIL import Image, ImageDraw, ImageFont
import os
os.makedirs(os.path.dirname(__file__), exist_ok=True)
# create base image
size = 256
img = Image.new('RGBA', (size, size), (15, 76, 129, 255))
d = ImageDraw.Draw(img)
# draw white circle
d.ellipse((24,24,size-24,size-24), fill=(255,255,255,230))
# draw letter
try:
    font = ImageFont.truetype('arial.ttf', 140)
except Exception:
    font = None
text = 'D'
if font:
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), text, font=font, fill=(15,76,129,255))
else:
    d.text((90,60), text, fill=(15,76,129,255))
# save as .ico with multiple sizes
icon_path = os.path.join(os.path.dirname(__file__), 'icono.ico')
img.save(icon_path, format='ICO', sizes=[(256,256),(128,128),(64,64),(32,32),(16,16)])
print('Wrote', icon_path)
