from flask import Flask, request, jsonify, render_template, send_file
import cv2
import easyocr
import numpy as np
import pandas as pd
import os
import base64

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

reader = easyocr.Reader(["en","hi"], gpu=True)

output_excel_file = os.path.join(UPLOAD_FOLDER, "extracted_text.xlsx")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" in request.files:
        image_file = request.files["image"]
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)
        image = cv2.imread(image_path)
    else:
        data = request.json.get("image")
        if not data:
            return jsonify({"error": "No image data received"}), 400

        header, encoded = data.split(",", 1)
        image_data = base64.b64decode(encoded)

        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Perform OCR
    text_results = reader.readtext(image)

    # Sort text by row
    text_results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))

    row_data = {}
    for bbox, text, _ in text_results:
        (x1, y1) = bbox[0]  
        row_key = int(y1 // 20)  

        if row_key not in row_data:
            row_data[row_key] = []

        row_data[row_key].append((x1, text))

    for row in row_data:
        row_data[row].sort()

    structured_rows = []
    for row in sorted(row_data.keys()):
        structured_rows.append([word[1] for word in row_data[row]])

    max_columns = max(len(row) for row in structured_rows)

    for row in structured_rows:
        while len(row) < max_columns:
            row.append("")

    df = pd.DataFrame(structured_rows)
    df.to_excel(output_excel_file, index=False, header=False)

    extracted_text = "\n".join([" ".join(row) for row in structured_rows])
    
    return jsonify({"message": "Text extracted successfully", "text": extracted_text, "download_link": "/download_excel"})

@app.route("/download_excel")
def download_excel():
    return send_file(output_excel_file, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

