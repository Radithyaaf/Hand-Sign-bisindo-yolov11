from pathlib import Path
import torch
from ultralytics import YOLO

def train():
    # Path ke folder dataset (untuk klasifikasi tidak pakai data.yaml)
    base_dir = Path(__file__).resolve().parent
    dataset_dir = base_dir / "dataset"

    if not dataset_dir.exists():
        print(f"[-] Folder dataset tidak ditemukan di: {dataset_dir}")
        print("Silakan pastikan Anda telah mengekstrak dataset ke dalam folder 'dataset/'.")
        return

    # Tentukan perangkat (GPU / CPU)
    device = "0" if torch.cuda.is_available() else "cpu"
    print(f"[+] Menggunakan perangkat: {device} ({'GPU CUDA' if device != 'cpu' else 'CPU'})")

    # Inisialisasi model YOLOv11 KHUSUS KLASIFIKASI (akhiran -cls)
    model = YOLO("yolo11n-cls.pt")

    print(f"[+] Memulai pelatihan model YOLOv11 Klasifikasi menggunakan dataset di folder: {dataset_dir}")
    results = model.train(
        data=str(dataset_dir),
        epochs=50,          # Sesuaikan jumlah epoch sesuai kebutuhan
        imgsz=224,          # Sesuai dengan hasil preprocessing di Roboflow (224x224)
        batch=16,           # Ukuran batch (RTX 3050 Anda cukup kuat untuk batch 16 atau 32 pada ukuran ini)
        device=device,
        workers=2,          # Number of worker threads
        project="runs/classify",
        name="yolov11_bisindo_cls_v2",
        exist_ok=True
    )

    print("[+] Pelatihan selesai!")
    trained_best = Path(results.save_dir) / "weights" / "best.pt"
    print(f"[+] Model terbaik tersimpan di: {trained_best}")

    # Salin otomatis ke folder weights/best.pt agar langsung dipakai web interface
    target_weights = base_dir / "weights" / "best.pt"
    if trained_best.exists():
        import shutil
        target_weights.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(trained_best, target_weights)
        print(f"[+] Model berhasil disalin ke: {target_weights}")

if __name__ == "__main__":
    train()
    