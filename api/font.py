from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageDraw, ImageFont
import os
import json

# 這是在 Vercel 環境中處理請求的標準方法
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # --- 1. 解析 URL 中的參數 ---
        query_components = parse_qs(urlparse(self.path).query)
        unicode_str = query_components.get('unicode', ['0'])[0]

        try:
            char_code = int(unicode_str)
            character = chr(char_code)
        except ValueError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid Unicode code point"}).encode())
            return

        # --- 2. 載入字型檔並繪製點陣圖 ---
        # 假設 font_data.ttf 與此 py 檔案在同一個 /api 資料夾中
        font_path = os.path.join(os.path.dirname(__file__), 'font_data.ttf')
        try:
            font = ImageFont.truetype(font_path, 16)
        except IOError:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Font file not found on server"}).encode())
            return
            
        image = Image.new('1', (16, 16), color=0)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), character, font=font, fill=1)

        # --- 3. 將圖片轉換為垂直點陣資料 ---
        bitmap_columns = []
        for x in range(16):
            column_byte = 0
            for y in range(16):
                if image.getpixel((x, y)) > 0:
                    # LSB (最低位元) 代表最頂端的像素 (y=0)
                    column_byte |= (1 << y)
            bitmap_columns.append(column_byte)
        
        # --- 4. 準備並回傳 JSON 結果 ---
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