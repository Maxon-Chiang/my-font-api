from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# 載入位於專案根目錄的字型檔
# os.path.realpath('') 會取得專案根目錄的路徑
font_path = os.path.join(os.path.dirname(__file__), 'font.ttf')
# 設定字型大小為 16px
font = ImageFont.truetype(font_path, 16)

@app.route('/api/font', methods=['GET'])
def get_font_bitmap():
    # 從 URL 參數中取得 unicode，例如 ?unicode=24859
    unicode_str = request.args.get('unicode', default='0', type=str)
    
    try:
        char_code = int(unicode_str)
        character = chr(char_code)
    except ValueError:
        return jsonify({"error": "Invalid Unicode code point"}), 400

    # 在記憶體中建立一個 16x16 的黑色畫布
    image = Image.new('1', (16, 16), color=0)
    draw = ImageDraw.Draw(image)

    # 將文字畫在畫布上
    # anchor='lt' 表示從左上角開始繪製
    draw.text((0, 0), character, font=font, fill=1)

    # --- 將圖片轉換為我們需要的「垂直」點陣資料 ---
    bitmap_columns = []
    # 遍歷 16 個垂直行 (column)
    for x in range(16):
        column_byte = 0
        # 遍歷行中的 16 個像素 (pixel)
        for y in range(16):
            pixel = image.getpixel((x, y))
            if pixel > 0:
                # 如果該點是亮的，就在對應的位元上設為 1
                # LSB (最低位元) 代表最頂端的像素 (y=0)
                column_byte |= (1 << y)
        bitmap_columns.append(column_byte)
    
    # 允許所有來源的請求 (CORS)，這樣 ESP8266 才能存取
    response = jsonify({
        "character": character,
        "unicode": char_code,
        "bitmap": bitmap_columns
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response

# 這段是為了在本機測試，部署到 Vercel 時它不會被執行
if __name__ == '__main__':
    app.run(debug=True)