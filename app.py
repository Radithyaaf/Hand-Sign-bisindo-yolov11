import io
import time
import base64
from pathlib import Path
from PIL import Image
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from ultralytics import YOLO

app = Flask(__name__)

# Base path dan model path
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATHS = [
    BASE_DIR / "weights" / "best.pt",
    BASE_DIR / "runs" / "classify" / "runs" / "classify" / "yolov11_bisindo_cls_v2" / "weights" / "best.pt",
    BASE_DIR / "runs" / "classify" / "yolov11_bisindo_cls_v2" / "weights" / "best.pt",
    BASE_DIR / "runs" / "classify" / "runs" / "train" / "yolov11_bisindo_cls" / "weights" / "best.pt",
    BASE_DIR / "runs" / "train" / "yolov11_bisindo_cls" / "weights" / "best.pt"
]

model = None
model_path_used = None

for path in MODEL_PATHS:
    if path.exists():
        print(f"[+] Memuat model dari: {path}")
        model = YOLO(str(path))
        model_path_used = str(path)
        break

if model is None:
    fallback = "yolo11n-cls.pt"
    print(f"[!] Model custom belum ditemukan. Menggunakan fallback: {fallback}")
    model = YOLO(fallback)
    model_path_used = fallback

# Training artifacts directory (cari run terbaru jika ada)
POSSIBLE_RUNS = [
    BASE_DIR / "runs" / "classify" / "runs" / "classify" / "yolov11_bisindo_cls_v2",
    BASE_DIR / "runs" / "classify" / "yolov11_bisindo_cls_v2",
    BASE_DIR / "runs" / "classify" / "runs" / "train" / "yolov11_bisindo_cls",
    BASE_DIR / "runs" / "train" / "yolov11_bisindo_cls"
]
RUNS_DIR = next((p for p in POSSIBLE_RUNS if p.exists()), POSSIBLE_RUNS[0])
DATASET_TEST_DIR = BASE_DIR / "dataset" / "test"
CUSTOM_REF_DIR = BASE_DIR / "static" / "references"
CUSTOM_REF_DIR.mkdir(parents=True, exist_ok=True)

def predict_on_pil(pil_img):
    """Jalankan inferensi klasifikasi YOLOv11 pada PIL Image"""
    start_time = time.time()
    
    # Resize / convert RGB
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
        
    results = model(pil_img, imgsz=224, verbose=False)
    infer_time = (time.time() - start_time) * 1000  # ms
    
    res = results[0]
    top1_idx = int(res.probs.top1)
    top1_name = model.names[top1_idx]
    top1_conf = float(res.probs.top1conf)
    
    top5_indices = res.probs.top5
    top5_confs = res.probs.top5conf.tolist()
    
    top5 = []
    for idx, conf in zip(top5_indices, top5_confs):
        top5.append({
            "class": model.names[int(idx)],
            "confidence": round(float(conf) * 100, 2),
            "ratio": float(conf)
        })
        
    return {
        "top1": top1_name,
        "confidence": round(top1_conf * 100, 2),
        "confidence_ratio": round(top1_conf, 4),
        "top5": top5,
        "inference_time_ms": round(infer_time, 1)
    }

@app.route("/")
def index():
    return render_template("index.html", model_info={
        "path": model_path_used,
        "classes_count": len(model.names),
        "classes": list(model.names.values())
    })

@app.route("/api/predict_upload", methods=["POST"])
def predict_upload():
    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nama file kosong"}), 400
        
    try:
        image_bytes = file.read()
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        # Ekstrak base64 untuk preview
        buffered = io.BytesIO()
        pil_img.save(buffered, format="JPEG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        result = predict_on_pil(pil_img)
        result["image_preview"] = f"data:image/jpeg;base64,{img_b64}"
        result["filename"] = file.filename
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict_frame", methods=["POST"])
def predict_frame():
    """Endpoint untuk stream webcam dari client (canvas base64)"""
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "Format data tidak valid"}), 400
            
        img_data = data["image"]
        if "," in img_data:
            img_data = img_data.split(",")[1]
            
        decoded = base64.b64decode(img_data)
        pil_img = Image.open(io.BytesIO(decoded))
        
        result = predict_on_pil(pil_img)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/alphabet_reference")
def alphabet_reference():
    """Ambil daftar kelas A-Z beserta URL contoh gambarnya (memprioritaskan custom reference)"""
    items = []
    classes = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    
    for c in classes:
        # 1. Cek apakah ada custom reference di static/references/
        custom_img = None
        for ext in [".jpg", ".png", ".jpeg", ".webp"]:
            candidate = CUSTOM_REF_DIR / f"{c}{ext}"
            if candidate.exists():
                custom_img = candidate
                break

        if custom_img:
            items.append({
                "class": c,
                "has_sample": True,
                "is_custom": True,
                "sample_url": f"/static/references/{custom_img.name}?t={int(custom_img.stat().st_mtime)}"
            })
        else:
            # 2. Ambil dari dataset test (filter gambar gestur yang bagus, hindari background jauh)
            class_dir = DATASET_TEST_DIR / c
            if class_dir.exists():
                img_list = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
                # Pilih gambar yang berawalan sesuai nama huruf (misal A-139, B-xxx) daripada timestamp camera
                hand_imgs = [im for im in img_list if im.name.startswith(f"{c}-") or im.name.startswith(f"{c.lower()}-")]
                selected = hand_imgs[0] if hand_imgs else (img_list[0] if img_list else None)
                items.append({
                    "class": c,
                    "has_sample": selected is not None,
                    "is_custom": False,
                    "sample_url": f"/dataset_sample/{c}/{selected.name}" if selected else None
                })
            else:
                items.append({
                    "class": c,
                    "has_sample": False,
                    "is_custom": False,
                    "sample_url": None
                })
    return jsonify({"alphabet": items})

@app.route("/api/upload_custom_reference", methods=["POST"])
def upload_custom_reference():
    """Endpoint untuk upload foto referensi kustom per huruf A-Z"""
    if "file" not in request.files or "class" not in request.form:
        return jsonify({"error": "Data file atau kelas tidak lengkap"}), 400
        
    file = request.files["file"]
    class_name = request.form["class"].upper().strip()
    if not class_name or len(class_name) != 1 or not class_name.isalpha():
        return jsonify({"error": "Nama kelas huruf tidak valid (harus 1 huruf A-Z)"}), 400
        
    try:
        CUSTOM_REF_DIR.mkdir(parents=True, exist_ok=True)
        # Hapus file lama jika ada ekstensi berbeda
        for ext in [".jpg", ".png", ".jpeg", ".webp"]:
            old = CUSTOM_REF_DIR / f"{class_name}{ext}"
            if old.exists():
                old.unlink()
                
        pil_img = Image.open(file.stream)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        target_path = CUSTOM_REF_DIR / f"{class_name}.jpg"
        pil_img.save(target_path, format="JPEG", quality=95)
        
        return jsonify({
            "success": True,
            "class": class_name,
            "sample_url": f"/static/references/{class_name}.jpg?t={int(time.time())}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset_custom_reference", methods=["POST"])
def reset_custom_reference():
    """Reset foto referensi kembali ke default dataset"""
    data = request.get_json() or {}
    class_name = data.get("class", "").upper().strip()
    if class_name:
        for ext in [".jpg", ".png", ".jpeg", ".webp"]:
            old = CUSTOM_REF_DIR / f"{class_name}{ext}"
            if old.exists():
                old.unlink()
        return jsonify({"success": True, "class": class_name})
    return jsonify({"error": "Kelas tidak valid"}), 400

@app.route("/dataset_sample/<class_name>/<filename>")
def dataset_sample(class_name, filename):
    folder = DATASET_TEST_DIR / class_name
    return send_from_directory(folder, filename)

@app.route("/training_metrics/<filename>")
def training_metrics(filename):
    if RUNS_DIR.exists():
        return send_from_directory(RUNS_DIR, filename)
    return jsonify({"error": "Folder training tidak ditemukan"}), 404

@app.route("/api/metrics_list")
def metrics_list():
    """Daftar grafik metrik training yang tersedia"""
    available_files = []
    targets = [
        "results.png",
        "confusion_matrix.png",
        "confusion_matrix_normalized.png",
        "val_batch0_pred.jpg",
        "val_batch1_pred.jpg",
        "train_batch0.jpg"
    ]
    if RUNS_DIR.exists():
        for target in targets:
            if (RUNS_DIR / target).exists():
                available_files.append(target)
    return jsonify({"metrics": available_files})

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 APLIKASI WEB DETEKSI BISINDO DENGAN YOLOV11 BERJALAN")
    print("📍 Buka browser di URL: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)

