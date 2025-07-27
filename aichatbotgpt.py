# AI Chatbot dengan Streamlit - Full Features
import streamlit as st
import requests
import json
import base64
import tempfile
import os
import fitz  # PyMuPDF untuk baca PDF
from io import BytesIO
from PIL import Image
import speech_recognition as sr

# --- KONFIGURASI DASAR ---
st.set_page_config(
    page_title="AI Chatbot All-in-One",
    page_icon="🤖",
    layout="wide"
)

# --- HEADER ---
st.markdown("""
<h1 style='text-align: center; 
           color: #4da6ff;
           font-family: Arial Black, Gadget, sans-serif;
           letter-spacing: 2px;
           font-size: 42px;'>
🤖 WELCOME TO CHATBOT ALL IN 🤖
</h1>
""", unsafe_allow_html=True)

# --- CSS KUSTOM UNTUK WARNA ---
custom_css = """
<style>
body {
    background-color: #fdf6ee;
    color: #1e1e1e;
}
[data-testid="stSidebar"] {
    background-color: #cce6ff;
    color: black;
}
.stButton>button {
    background-color: #4da6ff;
    color: white;
    border-radius: 8px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- INISIALISASI SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_count" not in st.session_state:
    st.session_state.user_count = 0
if "reset_done" not in st.session_state:
    st.session_state.reset_done = False
if "initialized" not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    st.session_state.initialized = True
    # Tidak menambah user_count di sini

# --- PENGATURAN API & MODEL ---
st.sidebar.title("⚙️ Pengaturan")
api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

MODEL_LIST = {
    "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
    "Llama 3 8B (Free)": "meta-llama/llama-3-8b-instruct:free",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "Google Gemini Pro": "google/gemini-pro"
}
selected_model_name = st.sidebar.selectbox("Pilih Model", list(MODEL_LIST.keys()))
model_id = MODEL_LIST[selected_model_name]

# --- FUNGSI PANGGILAN API ---
def get_ai_response(messages, model, api_key):
    try:
        r = requests.post(
            url = "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            data=json.dumps({
                "model": model,
                "messages": messages,
            })
        )
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# --- ANALISIS PDF ---
def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# --- ANALISIS GAMBAR ---
def analyze_image(image_file):
    img = Image.open(image_file)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"Gambar berhasil diunggah dan diproses. [Ukuran: {img.size}]"

# --- AREA CHAT UTAMA ---
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": "Halo! Ada yang bisa saya bantu hari ini?"})

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tulis pertanyaan Anda..."):
    st.session_state.user_count += 1  # Count akses saat user kirim chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Sedang berpikir..."):
            response = get_ai_response(
                messages=st.session_state.messages,
                model=model_id,
                api_key=api_key
            )
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- SIDEBAR FITUR ---
if st.sidebar.button("Reset Chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown(f"**👥 Total Akses: {st.session_state.user_count}**")

# --- ANALISIS GAMBAR ---
st.sidebar.subheader("🖼️ Analisis Gambar")
image_file = st.sidebar.file_uploader("Unggah gambar (JPG/PNG)", type=["jpg", "jpeg", "png"])
if image_file:
    st.session_state.user_count += 1
    st.sidebar.image(image_file, caption="Gambar yang Diupload", use_container_width=True)
    st.sidebar.success(analyze_image(image_file))

# --- ANALISIS PDF ---
st.sidebar.subheader("📄 Analisis PDF")
pdf_file = st.sidebar.file_uploader("Unggah PDF", type="pdf")
if pdf_file:
    st.session_state.user_count += 1
    pdf_text = extract_text_from_pdf(pdf_file)
    st.sidebar.text_area("Isi PDF", pdf_text[:1000], height=200)
    st.session_state.messages.append({"role": "user", "content": f"Baca dan analisis dokumen berikut:\n{pdf_text[:1000]}"})

# --- JOBSEEKER ---
st.sidebar.subheader("🔍 Jobseeker Tool")
job_options = [
    "Data Analyst", "Marketing", "Supply Chain", "HSE", "Finance", "HRD", "Business Analyst",
    "Quality Control", "Procurement", "IT Support"
]
job_selected = st.sidebar.selectbox("Pilih bidang pekerjaan:", job_options)
suggestions = {
    "Marketing": ["Marketing Executive di Tokopedia", "Digital Marketing di Bukalapak", "Marketing Analyst di Traveloka"],
    "HSE": ["HSE Officer di Pertamina", "Safety Inspector di Chevron", "HSE Supervisor di Adaro"],
    "Supply Chain": ["Supply Chain Analyst di Unilever", "Logistics Planner di Nestle", "SCM Specialist di Danone"],
    "Data Analyst": ["Data Analyst di Google", "BI Analyst di Gojek", "Junior Data Analyst di Shopee"],
    "Finance": ["Finance Staff di Astra", "Financial Analyst di Mandiri", "Junior Accountant di Deloitte"],
    "HRD": ["HR Generalist di BCA", "Recruiter di Traveloka", "People Ops di Ruangguru"],
    "Business Analyst": ["BA Intern di BRI", "Business Analyst di Telkom", "Strategic Planner di OVO"],
    "Quality Control": ["QC Staff di Indofood", "QA/QC Inspector di Wings", "Quality Specialist di GarudaFood"],
    "Procurement": ["Procurement Staff di Pertamina", "Purchasing Analyst di Telkomsel", "Procurement Officer di PLN"],
    "IT Support": ["IT Support di Shopee", "Helpdesk Engineer di Gojek", "Junior IT Specialist di Traveloka"]
}
st.sidebar.success(f"Rekomendasi pekerjaan untuk: {job_selected}")
for job in suggestions[job_selected]:
    st.sidebar.markdown(f"- {job}")

# --- LOGISTIK ---
st.sidebar.subheader("🚚 Logistik Pintar")
asal = st.sidebar.selectbox("Kota Asal", ["Jakarta"])
tujuan = st.sidebar.selectbox("Kota Tujuan", ["Semarang", "Surabaya", "Bali (Denpasar)"])
rute_map = {
    "Semarang": ("450 km", "± 6–7 jam"),
    "Surabaya": ("780 km", "± 10–12 jam"),
    "Bali (Denpasar)": ("1.200 km", "± 18–20 jam via Surabaya – Banyuwangi – Gilimanuk")
}
if st.sidebar.button("Cari Rute Tercepat & Estimasi BBM"):
    st.session_state.user_count += 1
    if tujuan in rute_map:
        jarak, durasi = rute_map[tujuan]
        st.sidebar.info(f"Jarak: {jarak}\nDurasi: {durasi}\nEstimasi BBM hemat hingga 15%.")
    else:
        st.sidebar.warning("Rute tidak tersedia.")

# --- VOICE AGENT ---
st.sidebar.subheader("🎙️ Voice Agent")
if st.sidebar.button("Rekam Suara"):
    st.session_state.user_count += 1
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.sidebar.write("Silakan bicara...")
        audio = r.listen(source, timeout=5)
        try:
            text = r.recognize_google(audio, language='id-ID')
            st.sidebar.success(f"Teks hasil suara: {text}")
            st.session_state.messages.append({"role": "user", "content": text})

            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(text)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Sedang berpikir..."):
                    response = get_ai_response(
                        messages=st.session_state.messages,
                        model=model_id,
                        api_key=api_key
                    )
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
        except:
            st.sidebar.error("Gagal mengenali suara.")
