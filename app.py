from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import requests
from ultralytics import YOLO

app = Flask(__name__)
UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Tạo thư mục nếu chưa có
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# YOLOv8n - tự tải yolov8n.pt nếu chưa có
model = YOLO('yolov8n.pt')

# Telegram bot token và chat ID
BOT_TOKEN = '7699455070:AAEb0lEsOrQq9pnL_r3wEgDbqpXWk-mrwU0'
CHAT_ID = '7428847722'

def detect_person(image_path):
    results = model(image_path)
    for r in results:
        if 'person' in r.names.values():
            for c in r.boxes.cls:
                if int(c) == list(r.names.keys())[list(r.names.values()).index('person')]:
                    return True
    return False

def send_to_telegram(image_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"photo": photo})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No file part", 400
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    # Chạy YOLOv8n nhận diện
    if detect_person(save_path):
        send_to_telegram(save_path)

    return "OK", 200

@app.route('/latest')
def latest_image():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    if files:
        return send_from_directory(UPLOAD_FOLDER, files[0])
    else:
        return "No image", 404

if __name__ == '__main__':
    app.run(debug=True)
