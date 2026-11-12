# 🤟 BISINDO Sign Language Recognition System (YOLOv11 Nano)

Sistem pengenalan Bahasa Isyarat Indonesia (BISINDO) untuk 26 alfabet (A - Z) berbasis Computer Vision menggunakan model **Ultralytics YOLOv11 Classification (`yolo11n-cls`)**.

Dilengkapi dengan aplikasi web interaktif (Flask & Streamlit) dengan fitur deteksi kamera real-time, upload gambar, **Word Builder (Rangkai Kata)**, dan **Text-to-Speech (TTS) Bahasa Indonesia**.

---

## 👥 Tim Pengembang
- **Radithya** ([@Radithyaaf](https://github.com/Radithyaaf))
- **Taufik** ([@attaufik](https://github.com/attaufik))

*Praktikum Machine Learning — D3 Teknik Informatika*

---

## 📊 Ringkasan Model & Kinerja
- **Arsitektur**: YOLOv11 Nano Classifier (`yolo11n-cls`)
- **Total Parameter**: 1.564.410 (~1,56M)
- **Ukuran File Model**: 3,25 MB (`weights/best.pt`)
- **Top-1 Accuracy**: **98,0%** (0.9799)
- **Top-5 Accuracy**: **99,8%** (0.9983)
- **Validation Loss**: **0,0557**
- **Kecepatan Inferensi**: ~6,5 ms per frame (Akselerasi GPU CUDA RTX 3050)
- **Jumlah Kelas**: 26 Kelas Alfabet (`A` s.d. `Z`)

---

## 📁 Struktur Direktori

```text
BISINDO.v1i.yolov11/
├── app.py                      # Backend Web Full-Stack (Flask REST API)
├── app_streamlit.py            # Alternatif Web App (Streamlit)
├── webcam_desktop.py           # GUI Desktop Webcam (OpenCV)
├── predict.py                  # Script Pengujian Mandiri CLI
├── train.py                    # Script Training YOLOv11 Classification
├── generate_report.py          # Script Pembuat Laporan PDF Proyek
├── BISINDO_Project_Report.pdf  # Dokumentasi Lengkap Proyek (PDF)
├── requirements.txt            # Daftar Dependensi Python
├── templates/
│   └── index.html              # Frontend Web Modern (Tailwind CSS + Lucide Icons)
├── weights/
│   └── best.pt                 # Bobot Model Terbaik (Tersedia langsung)
├── runs/                       # Grafik Hasil Evaluasi & Metrik Training
└── dataset/                    # Folder Dataset (Unduh via Roboflow jika ingin melatih ulang)
```

---

## 📦 Instalasi & Persiapan

1. **Clone repositori**:
   ```bash
   git clone https://github.com/Radithyaaf/bisindo-yolov11.git
   cd bisindo-yolov11
   ```

2. **Buat dan aktifkan virtual environment (opsional namun disarankan)**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

*(Catatan: Model siap pakai `weights/best.pt` sudah tersedia langsung di dalam repositori, sehingga Anda bisa langsung menjalankan aplikasi web tanpa perlu melatih ulang model).*

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Web App Interaktif (Flask - Rekomendasi Utama)
Fitur lengkap:
- 📹 **Kamera Realtime** di browser dengan panduan kotak fokus.
- 🔤 **Word Builder**: Menyusun kata dari huruf yang dideteksi secara otomatis.
- 🔊 **Text-to-Speech (TTS)**: Pelafalan huruf dan membaca kata utuh dalam Bahasa Indonesia.
- 🖼️ **Upload Gambar**: Prediksi gambar dengan visualisasi probabilitas Top-5.
- 📖 **Panduan Alfabet**: Galeri isyarat 26 huruf + opsi upload foto referensi kustom.
- 📈 **Evaluasi Model**: Tampilan grafik training (Confusion Matrix, Loss, Akurasi).

```bash
python app.py
```
Akses di browser: **`http://127.0.0.1:5000`**

---

### 2. Alternatif Web App (Streamlit)
```bash
streamlit run app_streamlit.py
```
Akses di browser: **`http://localhost:8501`**

---

### 3. Desktop Webcam (OpenCV GUI)
```bash
python webcam_desktop.py
```
- Arahkan tangan ke dalam area kotak di tengah layar.
- Tekan **`s`** untuk mengambil screenshot.
- Tekan **`q`** untuk keluar.

---

### 4. Generate Laporan PDF
Untuk menghasilkan file laporan dokumentasi teknis dalam format PDF:
```bash
python generate_report.py
```
File output: `BISINDO_Project_Report.pdf`

---

## 📚 Informasi Dataset
Dataset bersumber dari **Roboflow Universe**:
- **Proyek**: BISINDO (`sijewi-jjr8b / bisindo-wb1lk`)
- **Lisensi**: CC BY 4.0
- **Total Gambar**: 51.312 gambar setelah augmentasi 3×
- **Distribusi Split**:
  - Train: 44.591 gambar
  - Valid: 5.825 gambar
  - Test: 896 gambar
- **Pre-processing**: Resize 224×224 piksel, Auto-orientation.
