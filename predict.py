from pathlib import Path
from ultralytics import YOLO

def predict():
    base_dir = Path(__file__).resolve().parent
    model_paths = [
        base_dir / "weights" / "best.pt",
        base_dir / "runs" / "classify" / "runs" / "train" / "yolov11_bisindo_cls" / "weights" / "best.pt",
        base_dir / "yolo11n-cls.pt"
    ]

    model_path = None
    for p in model_paths:
        if p.exists():
            model_path = p
            break

    if not model_path:
        print("[!] Model tidak ditemukan!")
        return

    print(f"[+] Memuat model dari: {model_path}")
    model = YOLO(str(model_path))

    # Ambil sampel dari dataset test klasifikasi
    test_dir = base_dir / "dataset" / "test"
    sample_images = list(test_dir.rglob("*.jpg")) + list(test_dir.rglob("*.png"))

    if not sample_images:
        print(f"[-] Tidak ada gambar uji di folder: {test_dir}")
        return

    sample_image = sample_images[0]
    expected_class = sample_image.parent.name
    print(f"[+] Menjalankan klasifikasi pada sampel: {sample_image.name} (Kelas Asli: {expected_class.upper()})")

    results = model.predict(source=str(sample_image), save=True, project="runs/predict", name="exp", exist_ok=True)
    res = results[0]
    top1_idx = int(res.probs.top1)
    top1_name = model.names[top1_idx]
    top1_conf = float(res.probs.top1conf)

    print("\n" + "="*40)
    print(f"🎯 Hasil Prediksi: Huruf '{top1_name.upper()}'")
    print(f"📊 Tingkat Keyakinan (Confidence): {top1_conf*100:.2f}%")
    print(f"📂 Hasil visualisasi disimpan di: runs/predict/exp")
    print("="*40 + "\n")

if __name__ == "__main__":
    predict()

