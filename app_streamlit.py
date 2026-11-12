import io
import time
from pathlib import Path
from PIL import Image
import streamlit as st
from ultralytics import YOLO

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="BISINDO Recognition - YOLOv11",
    page_icon="🤟",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATHS = [
    BASE_DIR / "weights" / "best.pt",
    BASE_DIR / "runs" / "classify" / "runs" / "train" / "yolov11_bisindo_cls" / "weights" / "best.pt",
    BASE_DIR / "yolo11n-cls.pt"
]

@st.cache_resource
def load_yolo_model():
    for p in MODEL_PATHS:
        if p.exists():
            return YOLO(str(p)), str(p)
    return YOLO("yolo11n-cls.pt"), "yolo11n-cls.pt (fallback)"

model, model_path = load_yolo_model()

# Header
st.title("🤟 Deteksi Bahasa Isyarat BISINDO - YOLOv11")
st.caption(f"Model: `{Path(model_path).name}` &bull; 26 Kelas Huruf Alfabet (A - Z)")

# Sidebar Navigasi
mode = st.sidebar.radio("Pilih Mode Deteksi:", ["📷 Kamera Realtime (Snapshot)", "📤 Upload Gambar", "📖 Panduan Alfabet A-Z", "📊 Evaluasi Model"])
conf_threshold = st.sidebar.slider("Tingkat Ambang Keyakinan (Confidence Threshold %):", 10, 100, 50) / 100.0

def predict_image(pil_img):
    t0 = time.time()
    results = model(pil_img, imgsz=224, verbose=False)
    infer_time = (time.time() - t0) * 1000

    res = results[0]
    top1_idx = int(res.probs.top1)
    top1_name = model.names[top1_idx]
    top1_conf = float(res.probs.top1conf)

    top5_indices = res.probs.top5
    top5_confs = res.probs.top5conf.tolist()
    top5 = [{"Huruf": model.names[int(idx)].upper(), "Confidence (%)": round(c * 100, 2)} for idx, c in zip(top5_indices, top5_confs)]

    return top1_name, top1_conf, top5, infer_time

# 1. Mode Kamera Realtime
if mode == "📷 Kamera Realtime (Snapshot)":
    st.subheader("📷 Deteksi Menggunakan Kamera")
    st.write("Arahkan tangan membentuk gestur BISINDO di depan kamera lalu ambil foto:")
    
    col_cam, col_res = st.columns([3, 2])
    with col_cam:
        cam_image = st.camera_input("Kamera")
        
    with col_res:
        if cam_image is not None:
            pil_img = Image.open(cam_image)
            top1_name, top1_conf, top5, infer_time = predict_image(pil_img)

            st.write("### Hasil Deteksi:")
            if top1_conf >= conf_threshold:
                st.success(f"## Huruf: **{top1_name.upper()}**")
            else:
                st.warning(f"## Huruf: **{top1_name.upper()}** (Keyakinan Rendah)")

            st.metric("Confidence Score", f"{top1_conf * 100:.2f}%", f"{infer_time:.1f} ms")
            
            st.write("#### 5 Prediksi Tertinggi:")
            for item in top5:
                st.write(f"**{item['Huruf']}**: {item['Confidence (%)']}%")
                st.progress(item['Confidence (%)'] / 100.0)
        else:
            st.info("Nyalakan kamera dan tekan tombol ambil gambar untuk menganalisis isyarat tangan.")

# 2. Mode Upload Gambar
elif mode == "📤 Upload Gambar":
    st.subheader("📤 Unggah Gambar Isyarat Tangan")
    uploaded_file = st.file_uploader("Pilih file gambar (JPG, PNG, WEBP):", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        col_img, col_res = st.columns([1, 1])
        pil_img = Image.open(uploaded_file)
        
        with col_img:
            st.image(pil_img, caption="Gambar yang Diunggah", use_container_width=True)

        with col_res:
            top1_name, top1_conf, top5, infer_time = predict_image(pil_img)
            st.write("### Hasil Analisis:")
            st.success(f"# Huruf: **{top1_name.upper()}**")
            st.metric("Tingkat Keyakinan", f"{top1_conf * 100:.2f}%", f"Latency: {infer_time:.1f} ms")

            st.write("#### Top 5 Distribusi Probabilitas:")
            for item in top5:
                st.write(f"**Huruf {item['Huruf']}**: {item['Confidence (%)']}%")
                st.progress(item['Confidence (%)'] / 100.0)

# 3. Panduan Alfabet
elif mode == "📖 Panduan Alfabet A-Z":
    st.subheader("📖 Referensi Bentuk Isyarat Tangan BISINDO (A - Z)")
    test_dir = BASE_DIR / "dataset" / "test"
    if test_dir.exists():
        classes = sorted([d for d in test_dir.iterdir() if d.is_dir()])
        cols = st.columns(6)
        for idx, c in enumerate(classes):
            imgs = list(c.glob("*.jpg")) + list(c.glob("*.png"))
            with cols[idx % 6]:
                if imgs:
                    st.image(str(imgs[0]), caption=f"Huruf {c.name.upper()}", use_container_width=True)
                else:
                    st.write(f"Huruf {c.name.upper()}")

# 4. Evaluasi Model
elif mode == "📊 Evaluasi Model":
    st.subheader("📊 Metrik & Grafik Evaluasi Model")
    possible_runs = [
        BASE_DIR / "runs" / "classify" / "runs" / "classify" / "yolov11_bisindo_cls_v2",
        BASE_DIR / "runs" / "classify" / "runs" / "train" / "yolov11_bisindo_cls"
    ]
    runs_dir = next((p for p in possible_runs if p.exists()), possible_runs[0])
    if runs_dir.exists():
        results_png = runs_dir / "results.png"
        cm_png = runs_dir / "confusion_matrix_normalized.png"
        val_pred = runs_dir / "val_batch0_pred.jpg"

        if results_png.exists():
            st.write("#### Grafik Loss & Akurasi Training (50 Epochs):")
            st.image(str(results_png), use_container_width=True)

        if cm_png.exists():
            st.write("#### Normalized Confusion Matrix:")
            st.image(str(cm_png), use_container_width=True)

        if val_pred.exists():
            st.write("#### Sampel Prediksi Batch Validasi:")
            st.image(str(val_pred), use_container_width=True)
    else:
        st.warning("Folder hasil training tidak ditemukan.")

