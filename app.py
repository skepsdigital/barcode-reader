from flask import Flask, request, jsonify
from pyzbar.pyzbar import decode
from PIL import Image
import io
import requests

app = Flask(__name__)

@app.route('/decode_barcode_from_url', methods=['POST'])
def decode_barcode_from_url():
    data = request.get_json()
    if 'url' not in data:
        return jsonify({"error": "No image URL provided"}), 400

    image_url = data['url']
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(image_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to download image"}), 400

    image = Image.open(io.BytesIO(response.content))
    barcodes = decode(image)

    if not barcodes:
        return jsonify({"error": "No barcode found"}), 404

    decoded_barcodes = []
    for barcode in barcodes:
        decoded_barcodes.append({
            "type": barcode.type,
            "data": barcode.data.decode()
        })

    return jsonify({"barcodes": decoded_barcodes})

@app.route('/decode_barcode', methods=['POST'])
def decode_barcode():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    barcodes = decode(image)

    if not barcodes:
        return jsonify({"error": "No barcode found"}), 404

    decoded_barcodes = []
    for barcode in barcodes:
        decoded_barcodes.append({
            "type": barcode.type,
            "data": barcode.data.decode()
        })

    return jsonify({"barcodes": decoded_barcodes})

@app.route('/status', methods=['POST', 'GET'])
def status():
    return jsonify({"live": "ok"})

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
