import time
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

def run_webcam():
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

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[-] Gagal membuka webcam (Kamera 0). Pastikan webcam terhubung dan tidak sedang digunakan aplikasi lain.")
        return

    print("\n[+] Webcam aktif!")
    print("    - Tekan 'q' untuk keluar")
    print("    - Tekan 's' untuk menyimpan screenshot hasil deteksi\n")

    prev_time = time.time()
    fps = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[-] Gagal membaca frame webcam.")
            break

        # Mirror frame agar terasa alami seperti cermin
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Tentukan kotak area fokus di tengah layar (Square)
        box_size = int(min(h, w) * 0.65)
        x1 = (w - box_size) // 2
        y1 = (h - box_size) // 2
        x2 = x1 + box_size
        y2 = y1 + box_size

        # Crop area tangan untuk inferensi model (224x224)
        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            results = model(roi_rgb, imgsz=224, verbose=False)
            res = results[0]
            top1_idx = int(res.probs.top1)
            pred_letter = model.names[top1_idx].upper()
            confidence = float(res.probs.top1conf) * 100
        else:
            pred_letter = "?"
            confidence = 0.0

        # Hitung FPS
        curr_time = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / (curr_time - prev_time + 1e-6))
        prev_time = curr_time

        # Gambar Kotak Area Fokus Tangan
        box_color = (0, 220, 100) if confidence >= 60 else (0, 165, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
        cv2.putText(frame, "Posisikan Tangan Disini", (x1 + 10, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        # Gambar Panel Header Hasil di bagian atas
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 85), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Tampilkan Huruf Terdeteksi & Confidence
        label_text = f"Huruf: {pred_letter}"
        conf_text = f"Keyakinan: {confidence:.1f}%"
        fps_text = f"FPS: {fps:.1f}"

        text_color = (0, 255, 120) if confidence >= 60 else (0, 200, 255)
        cv2.putText(frame, label_text, (20, 55), cv2.FONT_HERSHEY_DUPLEX, 1.4, text_color, 3)
        cv2.putText(frame, conf_text, (280, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2)
        cv2.putText(frame, fps_text, (w - 140, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)

        # Tampilkan instruksi di bagian bawah layar
        cv2.putText(frame, "Tekan 'q' untuk Keluar | 's' untuk Simpan Screenshot", 
                    (20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("BISINDO Hand Sign Recognition - YOLOv11", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            screenshot_path = base_dir / f"screenshot_{pred_letter}_{int(time.time())}.jpg"
            cv2.imwrite(str(screenshot_path), frame)
            print(f"[+] Screenshot tersimpan: {screenshot_path.name}")

    cap.release()
    cv2.destroyAllWindows()
    print("[+] Sesi webcam selesai.")

if __name__ == "__main__":
    run_webcam()

