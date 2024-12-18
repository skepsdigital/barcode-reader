from flask import Flask, request, jsonify
from pyzbar.pyzbar import decode
from PIL import Image
import io

app = Flask(__name__)

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