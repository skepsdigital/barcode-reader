from flask import Flask, request, jsonify
from pyzbar.pyzbar import decode
from PIL import Image
import io
import requests
import PyPDF2
import io # Para manipular dados binários em memória
import os

app = Flask(__name__)

# Configurações para o upload de arquivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cria a pasta de uploads se ela não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extractPdfText(caminho_pdf):
    """
    Extrai todo o texto de um arquivo PDF usando a biblioteca PyPDF2.
    """
    texto_completo = ""
    try:
        with open(caminho_pdf, 'rb') as arquivo_pdf:
            leitor_pdf = PyPDF2.PdfReader(arquivo_pdf)
            num_paginas = len(leitor_pdf.pages)

            for pagina_num in range(num_paginas):
                pagina = leitor_pdf.pages[pagina_num]
                texto_extraido = pagina.extract_text()
                if texto_extraido: # Garante que só adiciona se houver texto
                    texto_completo += texto_extraido + "\n"
        return texto_completo
    except Exception as e:
        # Logar o erro para depuração
        app.logger.error(f"Erro ao extrair texto do PDF {caminho_pdf}: {e}")
        return None


@app.route('/decode_barcode_from_url', methods=['POST'])
def decode_barcode_from_url():
    data = request.get_json()
    if 'url' not in data:
        return jsonify({ "success": False, "error": "No image URL provided"}), 400

    image_url = data['url']
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(image_url, headers=headers)
    if response.status_code != 200:
        return jsonify({ "success": False, "error": "Failed to download image"}), 400

    image = Image.open(io.BytesIO(response.content))
    barcodes = decode(image)

    if not barcodes:
        return jsonify({ "success": False, "error": "No barcode found"}), 404

    decoded_barcodes = []
    for barcode in barcodes:
        decoded_barcodes.append({
            "type": barcode.type,
            "data": barcode.data.decode()
        })

    return jsonify({ "success": True, "barcodes": decoded_barcodes})

@app.route('/decode_barcode', methods=['POST'])
def decode_barcode():
    if 'image' not in request.files:
        return jsonify({ "success": False, "error": "No image file provided"}), 400

    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))
    barcodes = decode(image)

    if not barcodes:
        return jsonify({ "success": False, "error": "No barcode found"}), 404

    decoded_barcodes = []
    for barcode in barcodes:
        decoded_barcodes.append({
            "type": barcode.type,
            "data": barcode.data.decode()
        })

    return jsonify({ "success": False, "barcodes": decoded_barcodes})

@app.route('/status', methods=['POST', 'GET'])
def status():
    return jsonify({"live": "ok"})

@app.route('/decode_pdf', methods=['POST'])
def upload_pdf():
    """
    Endpoint para receber um arquivo PDF, extrair seu texto e retorná-lo.
    """
    # 1. Verifica se a requisição contém um arquivo
    if 'file' not in request.files:
        return jsonify({ "success": False, "error": "Nome do arquivo inválido. Envie o arquivo PDF no campo *file* do formulário."}), 400

    file = request.files['file']

    # 2. Verifica se o nome do arquivo está vazio
    if file.filename == '':
        return jsonify({ "success": False, "error": "Nome do arquivo inválido. Envie o arquivo PDF no campo *file* do formulário."}), 400

    # 3. Verifica se o tipo do arquivo é permitido (PDF)
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            # Salva o arquivo temporariamente
            file.save(filepath)

            # Extrai o texto do PDF
            texto_extraido = extractPdfText(filepath)

            # Remove o arquivo temporário após a extração
            os.remove(filepath)

            if texto_extraido is not None:
                return jsonify({"success": True, "text": texto_extraido}), 200
            else:
                return jsonify({"success": False, "error": "Não foi possível extrair texto do PDF."}), 500

        except Exception as e:
            # Garante que o arquivo seja removido mesmo em caso de erro
            if os.path.exists(filepath):
                os.remove(filepath)
            app.logger.error(f"Erro inesperado no endpoint /upload-pdf: {e}")
            return jsonify({"success": False, "error": f"Ocorreu um erro interno: {e}"}), 500
    else:
        return jsonify({"success": False, "error": "Tipo de arquivo não permitido. Apenas PDFs são aceitos."}), 400


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
