from flask import Flask, request, render_template, send_from_directory
from ultralytics import YOLO
import os
from PIL import Image

app = Flask(__name__)

# Load model
model = YOLO("models/Hamasawi_segmentation_model.pt")

# Folder untuk upload dan hasil
UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(RESULT_FOLDER):
    os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "File tidak ditemukan!"
        
        file = request.files["file"]
        if file.filename == "":
            return "Nama file kosong!"

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Jalankan inferensi
        results = model(filepath)

        # Simpan hasil deteksi visual
        result_path = os.path.join(RESULT_FOLDER, file.filename)
        for r in results:
            im_array = r.plot()
            im = Image.fromarray(im_array[..., ::-1])  # BGR to RGB
            im.save(result_path)

        # Tentukan kelas hasil 
        class_mapping = {
            0: "Hama",
            1: "Sehat"
        }

        detected_class = "Tidak Dikenali"
        detected_hama = None

        if results and results[0].boxes.cls.numel() > 0:
            detected_class_id = int(results[0].boxes.cls[0])
            detected_class = class_mapping.get(detected_class_id, "Tidak Dikenali")

            if detected_class == "Hama":
                detected_hama = "Ngengat Berlian atau Ulat Grayak"

        return render_template(
            "index.html",
            original=filepath,
            result=result_path,
            detected_class=detected_class,
            detected_hama=detected_hama,
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
