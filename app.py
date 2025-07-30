from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import tempfile

app = Flask(__name__)
app.secret_key = 'secret-key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return redirect(url_for('upload_key'))

@app.route('/upload-key', methods=['GET', 'POST'])
def upload_key():
    if request.method == 'POST':
        answer_key = request.form['answer_key'].replace("\n", "\n").strip().splitlines()
        key_dict = {}
        for line in answer_key:
            if '.' in line:
                q, a = line.split('.')
                key_dict[int(q.strip())] = a.strip().upper()
        session['answer_key'] = key_dict
        return redirect(url_for('upload_omr'))
    return render_template('upload_key.html')

@app.route('/upload-omr', methods=['GET', 'POST'])
def upload_omr():
    if request.method == 'POST':
        if 'omr_sheet' not in request.files:
            return "No file part"
        file = request.files['omr_sheet']
        if file.filename == '':
            return "No selected file"
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['uploaded_file'] = filename
        return redirect(url_for('result'))
    return render_template('upload_omr.html')

@app.route('/result')
def result():
    answer_key = session.get('answer_key')
    uploaded_file = session.get('uploaded_file')
    if not answer_key or not uploaded_file:
        return "Missing data"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)

    # Simulated OMR processing: all answers are A for simplicity
    student_answers = {i: 'A' for i in answer_key.keys()}
    score = sum(1 for q, a in answer_key.items() if student_answers.get(q) == a)

    return render_template('result.html', filename=uploaded_file, score=score)

if __name__ == '__main__':
    app.run(debug=True)
