import mysql.connector

connection  = mysql.connector.connect(host="localhost",user="root",password="",database="demo")

if connection.is_connected():
    print("connected")
else: 
    print("not connected")


import cv2
import easyocr
import pandas as pd
import os

USE_GPU = True  

image_path = "./Images/image17.png"
output_excel_file = "./Images/extracted_text17.xlsx"

if not os.path.exists(image_path):
    print(f"❌ Error: Image file not found at {image_path}")
    exit()

image = cv2.imread(image_path)
height, width, _ = image.shape  
reader = easyocr.Reader(["en"], gpu=USE_GPU)


text_results = reader.readtext(image)

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

print(f"\n✅ Text extracted and saved in: {output_excel_file}")