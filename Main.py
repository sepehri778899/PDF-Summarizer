import os
import openai
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import PyPDF2
import io
import re

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Read system rules from file
def read_system_rules():
    try:
        with open('system_rules.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "You are a helpful assistant that summarizes text concisely."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form.get('text', '')
    system_rules = read_system_rules()
    
    # Detect if input is Persian
    def has_persian(text):
        persian_pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(persian_pattern.search(text))
    
    # Set language instruction based on input
    is_persian = has_persian(text)
    language_instruction = "Please provide the summary in Persian." if is_persian else "Please provide the summary in English."
    
    client = openai.OpenAI(
        base_url="https://llama3-3-70b.lepton.run/api/v1/",
        api_key="vd9CiNg116pUHlY6xls5UHKwqaTL0xnA"
    )

    completion = client.chat.completions.create(
        model="llama3.3-70b",
        messages=[
            {"role": "system", "content": system_rules},
            {"role": "system", "content": language_instruction},
            {"role": "user", "content": f"Please summarize the following text:\n\n{text}"},
        ],
        max_tokens=128,
        stream=False,
    )
    
    summary = completion.choices[0].message.content
    return jsonify({'summary': summary})

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '' or not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='192.168.100.9', debug=True, port=5000)
