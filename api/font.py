from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw, ImageFont
import os
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        unicode_str = query_components.get('unicode', ['0'])[0]

        try:
            char_code = int(unicode_str)
            character = chr(char_code)
        except ValueError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid Unicode"}).encode())
            return

        font_path = os.path.join(os.path.dirname(__file__), 'font_data.ttf')
        try:
            font = ImageFont.truetype(font_path, 16)
        except IOError:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Font file not found"}).encode())
            return
            
        image = Image.new('1', (16, 16), color=0)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), character, font=font, fill=1)

        bitmap_columns = []
        for x in range(16):
            column_byte = 0
            for y in range(16):
                if image.getpixel((x, y)) > 0:
                    column_byte |= (1 << y)
            bitmap_columns.append(column_byte)
        
        response_data = {
            "character": character,
            "unicode": char_code,
            "bitmap": bitmap_columns
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
        return