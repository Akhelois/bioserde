import streamlit as st

st.set_page_config(
    page_title="🏭 Bioserde Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #262730;
    }
    
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #262730;
    }
    
    .stButton > button {
        background-color: #ffffff;
        color: #262730;
        border: 1px solid #cccccc;
    }
    
    .stButton > button:hover {
        background-color: #f0f2f6;
        border: 1px solid #1f77b4;
    }
    
    .stMetric {
        background-color: #ffffff;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background-color: #f8f9fa !important;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #e3f2fd !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #f1f8e9 !important;
    }
</style>
""", unsafe_allow_html=True)

import random
import time
import os
from dotenv import load_dotenv
import serial
import json
from openai import AzureOpenAI
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from azure.iot.device import IoTHubDeviceClient, Message
import serial.tools.list_ports

load_dotenv()
iot_client = None

@st.cache_resource
def init_arduino_and_iot():
    global iot_client
    
    arduino = None
    try:
        available_ports = serial.tools.list_ports.comports()
        
        if not available_ports:
            print("❌ Tidak ada port serial yang tersedia")
        else:
            print("🔍 Mencari Arduino di port yang tersedia:")
            for port in available_ports:
                print(f"  - {port.device}: {port.description}")
            
            possible_ports = []
            for port in available_ports:
                if any(keyword in port.description.lower() for keyword in 
                       ['arduino', 'ch340', 'cp210', 'ftdi', 'usb-serial', 'com']):
                    possible_ports.append(port.device)
            
            if not possible_ports:
                possible_ports = [port.device for port in available_ports]
            
            for port_name in possible_ports:
                try:
                    print(f"🔌 Mencoba connect ke {port_name}...")
                    arduino = serial.Serial(port_name, 9600, timeout=2)
                    time.sleep(2)
                    
                    arduino.flushInput()
                    test_read = arduino.readline().decode('utf-8').strip()
                    
                    print(f"✅ Berhasil connect ke Arduino di {port_name}")
                    if test_read:
                        print(f"📡 Test data: {test_read}")
                    break
                    
                except Exception as e:
                    print(f"❌ Failed pada {port_name}: {str(e)}")
                    continue
    
    except Exception as e:
        print(f"❌ Error dalam pencarian Arduino: {str(e)}")
    
    try:
        CONNECTION_STRING = "HostName=318Hub.azure-devices.net;DeviceId=bioserde;SharedAccessKey=ml0XIrouzxoP/zmDGex1lHNjcCj76+cD/aRwKc+r9no="
        iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        print("🌐 Connecting to Azure IoT Hub...")
        iot_client.connect()
        print("✅ Connected to Azure IoT Hub")
    except Exception as azure_error:
        print(f"⚠️ Azure IoT Hub connection failed: {azure_error}")
        iot_client = None
    
    return arduino, iot_client

def send_to_iot_hub(sensor_data, status, issues):
    global iot_client
    
    if iot_client is None:
        try:
            CONNECTION_STRING = "HostName=318Hub.azure-devices.net;DeviceId=bioserde;SharedAccessKey=ml0XIrouzxoP/zmDGex1lHNjcCj76+cD/aRwKc+r9no="
            iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
            iot_client.connect()
            print("🔄 IoT Hub reconnected")
        except Exception as e:
            print(f"⚠️ IoT Hub reconnection failed: {e}")
            return False
    
    try:
        message_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "deviceId": "bioserde",
            "temperature": sensor_data["temperature"],
            "ph": sensor_data["ph"],
            "methane": sensor_data["methane"],
            "status": status,
            "issues": issues,
            "source": sensor_data["source"]
        }
        
        message_json = json.dumps(message_data)
        message = Message(message_json)
        
        message.custom_properties["messageType"] = "telemetry"
        message.custom_properties["deviceId"] = "bioserde"
        message.custom_properties["status"] = status
        
        iot_client.send_message(message)
        print(f"📤 Data berhasil dikirim ke IoT Hub: {message_json}")
        return True
        
    except Exception as e:
        print(f"❌ Gagal kirim ke IoT Hub: {str(e)}")
        iot_client = None
        return False
    
arduino_connection, iot_client = init_arduino_and_iot()

def read_arduino_data():
    if arduino_connection is None:
        return {
            "temperature": random.uniform(30, 45),
            "ph": random.uniform(6.0, 8.5),
            "methane": random.uniform(80, 350),
            "source": "simulation"
        }
    
    try:
        arduino_connection.flushInput()
        line = arduino_connection.readline().decode('utf-8').strip()
        
        if line and ',' in line:
            values = line.split(',')
            if len(values) >= 3:
                temp = float(values[0])
                raw_ph = float(values[1])
                methane = float(values[2])
                
                ph = 7.0 + (raw_ph - 2.5) * 2
                ph = max(0, min(14, ph))
                
                return {
                    "temperature": temp,
                    "ph": ph,
                    "methane": methane,
                    "source": "arduino"
                }
        
        return {
            "temperature": 35.0,
            "ph": 7.0,
            "methane": 200.0,
            "source": "default"
        }
        
    except Exception as e:
        print(f"❌ Error reading Arduino: {e}")
        return {
            "temperature": random.uniform(30, 45),
            "ph": random.uniform(6.0, 8.5),
            "methane": random.uniform(80, 350),
            "source": "error_fallback"
        }

@st.cache_resource
def init_client():
    endpoint = os.getenv("ENDPOINT_URL")
    deployment = os.getenv("DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_API_KEY")
    
    if not all([endpoint, deployment, api_key]):
        st.error("⚠️ Environment variables tidak lengkap! Periksa file .env")
        st.stop()
    
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2025-01-01-preview",
    )
    return client, deployment

client, deployment = init_client()

BIOGAS_EXPERT_PROMPT = """Kamu adalah asisten AI yang membantu pemilik biogas rumahan atau UMKM. Kamu akan menjelaskan kondisi sistem biogas dengan bahasa yang mudah dipahami dan memberikan panduan praktis.

Tugasmu:
- Menjelaskan kondisi sistem biogas dengan bahasa sederhana
- Memberikan saran praktis yang bisa dilakukan user sendiri
- Mengingatkan tentang keselamatan jika diperlukan
- Menjelaskan mengapa sesuatu terjadi dengan analogi sehari-hari
- Memberikan langkah-langkah yang mudah diikuti
- Menyarankan kapan perlu memanggil teknisi jika masalah serius

Selalu gunakan:
- Bahasa Indonesia yang mudah dipahami
- Emoji untuk memperjelas pesan
- Penjelasan seperti berbicara dengan teman
- Contoh konkret dan praktis
- Peringatan keselamatan jika perlu

Ingat: User adalah orang awam yang ingin sistemnya bekerja dengan baik, bukan ahli teknis."""

OPTIMAL_RANGES = {
    "temperature": {"min": 35, "max": 40, "critical_min": 25, "critical_max": 50},
    "ph": {"min": 6.8, "max": 7.2, "critical_min": 6.0, "critical_max": 8.5},
    "methane": {"min": 150, "max": 300, "critical_min": 50, "critical_max": 500}
}

def analyze_sensor_data(temp, ph, methane):
    issues = []
    status = "optimal"
    
    if temp < OPTIMAL_RANGES["temperature"]["critical_min"] or temp > OPTIMAL_RANGES["temperature"]["critical_max"]:
        issues.append(f"🚨 BAHAYA: Suhu {temp:.1f}°C terlalu ekstrem!")
        status = "critical"
    elif temp < OPTIMAL_RANGES["temperature"]["min"] or temp > OPTIMAL_RANGES["temperature"]["max"]:
        if temp < OPTIMAL_RANGES["temperature"]["min"]:
            issues.append(f"⚠️ PERHATIAN: Suhu {temp:.1f}°C terlalu dingin")
        else:
            issues.append(f"⚠️ PERHATIAN: Suhu {temp:.1f}°C terlalu panas")
        if status != "critical":
            status = "warning"
    
    if ph < OPTIMAL_RANGES["ph"]["critical_min"] or ph > OPTIMAL_RANGES["ph"]["critical_max"]:
        if ph < OPTIMAL_RANGES["ph"]["critical_min"]:
            issues.append(f"🚨 BAHAYA: pH {ph:.1f} terlalu asam!")
        else:
            issues.append(f"🚨 BAHAYA: pH {ph:.1f} terlalu basa!")
        status = "critical"
    elif ph < OPTIMAL_RANGES["ph"]["min"] or ph > OPTIMAL_RANGES["ph"]["max"]:
        if ph < OPTIMAL_RANGES["ph"]["min"]:
            issues.append(f"⚠️ PERHATIAN: pH {ph:.1f} agak asam")
        else:
            issues.append(f"⚠️ PERHATIAN: pH {ph:.1f} agak basa")
        if status != "critical":
            status = "warning"
    
    if methane < OPTIMAL_RANGES["methane"]["critical_min"]:
        issues.append(f"🚨 BAHAYA: Gas metana {methane:.0f} ppm sangat rendah!")
        status = "critical"
    elif methane > OPTIMAL_RANGES["methane"]["critical_max"]:
        issues.append(f"🚨 BAHAYA: Gas metana {methane:.0f} ppm terlalu tinggi!")
        status = "critical"
    elif methane < OPTIMAL_RANGES["methane"]["min"]:
        issues.append(f"⚠️ PERHATIAN: Produksi gas {methane:.0f} ppm masih kurang")
        if status != "critical":
            status = "warning"
    
    return status, issues

def get_ai_guidance(temp, ph, methane, status, issues, user_question=""):
    
    sensor_context = f"""
DATA SISTEM BIOGAS ANDA SAAT INI:
🌡️ Suhu dalam tangki: {temp:.1f}°C
⚗️ Tingkat keasaman (pH): {ph:.1f}
🧪 Level gas metana: {methane:.0f} ppm
📊 Status sistem: {status.upper()}

KONDISI IDEAL YANG DIINGINKAN:
🎯 Suhu terbaik: 35-40°C (seperti suhu tubuh manusia)
🎯 pH terbaik: 6.8-7.2 (seperti air bersih, tidak asam tidak basa)
🎯 Gas metana bagus: 150-300 ppm

YANG PERLU DIPERHATIKAN SEKARANG:
{chr(10).join(issues) if issues else "✅ Semuanya normal dan baik!"}
"""
    
    if user_question:
        prompt = f"{sensor_context}\n\nPERTANYAAN USER: {user_question}\n\nTolong bantu jawab dengan bahasa yang mudah dipahami dan berikan saran praktis yang bisa dilakukan."
    else:
        prompt = f"{sensor_context}\n\nTolong jelaskan kondisi sistem biogas saya sekarang dan apa yang harus saya lakukan. Gunakan bahasa yang mudah dipahami."
    
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": BIOGAS_EXPERT_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8192,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Maaf, ada gangguan sistem. Coba lagi nanti ya! 😅\nError: {str(e)}"

st.title("🏭 Dashboard Biogas Bioserde")
st.markdown("💚 **Monitor biogas Anda dengan mudah dan dapatkan panduan AI yang ramah!**")

if "sensor_history" not in st.session_state:
    st.session_state.sensor_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if arduino_connection:
            st.success("🔗 **Terhubung ke Arduino COM5** - Data real-time dari sensor")
            if iot_client:
                st.success("☁️ **Terhubung ke Azure IoT Hub** - Data tersinkron ke cloud")
            else:
                st.warning("⚠️ **Arduino OK, IoT Hub gagal** - Data hanya lokal")
        else:
            st.warning("⚠️ **Tidak terhubung ke Arduino** - Menggunakan data simulasi")
    
    with col2:
        st.subheader("🔄 Kontrol Data")
        auto_refresh = st.checkbox("Auto Refresh (5 detik)", value=True)
        if st.button("🔄 Perbarui Data"):
            st.rerun()

sensor_data = read_arduino_data()
suhu = sensor_data["temperature"]
ph = sensor_data["ph"]
gas_level = sensor_data["methane"]
data_source = sensor_data["source"]

if data_source == "arduino":
    st.info("📡 **Data dari Arduino**: LM35 + MQ-2 sensor aktif")
elif data_source == "simulation":
    st.info("🎮 **Mode Simulasi**: Arduino tidak terhubung")

status, issues = analyze_sensor_data(suhu, ph, gas_level)

iot_success = send_to_iot_hub(sensor_data, status, issues)

current_reading = {
    "timestamp": time.time(),
    "temperature": suhu,
    "ph": ph, 
    "methane": gas_level,
    "status": status,
    "source": data_source
}
st.session_state.sensor_history.append(current_reading)

if len(st.session_state.sensor_history) > 50:
    st.session_state.sensor_history = st.session_state.sensor_history[-50:]

st.subheader("📊 Monitor Real-time")
col1, col2, col3, col4 = st.columns(4)

status_colors = {"optimal": "🟢", "warning": "🟡", "critical": "🔴"}
status_messages = {
    "optimal": "Baik", 
    "warning": "Perhatian", 
    "critical": "Tindakan"
}

with col1:
    st.metric(
        f"{status_colors[status]} Status",
        status_messages[status],
        f"{len(issues)}" if issues else "OK"
    )

with col2:
    delta_temp = suhu - 37.5
    color = "normal"
    if abs(delta_temp) > 5:
        color = "inverse"
    st.metric("🌡️ Suhu", f"{suhu:.1f}°C", f"{delta_temp:+.1f}°C", delta_color=color)

with col3:
    delta_ph = ph - 7.0
    color = "normal"
    if abs(delta_ph) > 0.5:
        color = "inverse"
    st.metric("⚗️ pH", f"{ph:.1f}", f"{delta_ph:+.1f}", delta_color=color)

with col4:
    delta_gas = gas_level - 225
    color = "normal"
    if delta_gas < -50:
        color = "inverse"
    st.metric("🧪 Gas", f"{gas_level:.0f} ppm", f"{delta_gas:+.0f}", delta_color=color)

if issues:
    for issue in issues:
        if "BAHAYA" in issue:
            st.error(issue)
        else:
            st.warning(issue)
else:
    st.success("✅ Semua parameter dalam kondisi yang baik!")

if st.session_state.sensor_history:
    st.subheader("📈 Grafik Monitoring")
    df = pd.DataFrame(st.session_state.sensor_history)
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('🌡️ Suhu (°C)', '⚗️ Tingkat pH', '🧪 Gas Metana (ppm)'),
        vertical_spacing=0.08
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['temperature'], name='Suhu', line=dict(color='red', width=3)),
        row=1, col=1
    )
    fig.add_hline(y=35, line_dash="dash", line_color="green", annotation_text="Min Ideal", row=1, col=1)
    fig.add_hline(y=40, line_dash="dash", line_color="green", annotation_text="Max Ideal", row=1, col=1)
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['ph'], name='pH', line=dict(color='blue', width=3)),
        row=2, col=1
    )
    fig.add_hline(y=6.8, line_dash="dash", line_color="green", annotation_text="Min Ideal", row=2, col=1)
    fig.add_hline(y=7.2, line_dash="dash", line_color="green", annotation_text="Max Ideal", row=2, col=1)
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['methane'], name='Metana', line=dict(color='orange', width=3)),
        row=3, col=1
    )
    fig.add_hline(y=150, line_dash="dash", line_color="green", annotation_text="Min Bagus", row=3, col=1)
    fig.add_hline(y=300, line_dash="dash", line_color="green", annotation_text="Max Bagus", row=3, col=1)
    
    fig.update_layout(height=600, showlegend=False, title_text="Monitor Data Sensor Real-time")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("🤖 Asisten AI Biogas - Tanya Apa Saja!")
st.markdown("*Asisten yang ramah dan mudah dipahami untuk membantu Anda*")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🔍 Cek Kondisi"):
        user_question = "Bagaimana kondisi sistem biogas saya sekarang? Apakah semuanya baik-baik saja?"
with col2:
    if st.button("🆘 Ada Masalah?"):
        user_question = "Saya merasa ada yang tidak beres dengan biogas saya. Bisa bantu cek apa masalahnya?"
with col3:
    if st.button("💡 Tips Perawatan"):
        user_question = "Apa yang bisa saya lakukan untuk menjaga biogas tetap bagus dan produktif?"
with col4:
    if st.button("❓ Jelaskan Dong"):
        user_question = "Tolong jelaskan dengan sederhana apa arti angka-angka ini dan bagaimana cara bacanya."

if status != "optimal" and not st.session_state.messages:
    auto_guidance = get_ai_guidance(suhu, ph, gas_level, status, issues)
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"**🚨 PERINGATAN OTOMATIS - {status_messages[status].upper()}!**\n\n{auto_guidance}"
    })

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya apa saja tentang biogas Anda... (misal: 'Kenapa gas sedikit?' atau 'Aman nggak nih?')"):
    user_question = prompt

if 'user_question' in locals():
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    with st.chat_message("assistant"):
        with st.spinner("Asisten AI sedang menganalisis data Anda... 🤔"):
            ai_response = get_ai_guidance(suhu, ph, gas_level, status, issues, user_question)
            st.markdown(ai_response)
    
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

with st.sidebar:
    st.header("📋 Panduan Sistem")
    
    st.subheader("🎯 Kondisi Ideal")
    st.success("🌡️ **Suhu**: 35-40°C  \n*Hangat seperti suhu tubuh*")
    st.success("⚗️ **pH**: 6.8-7.2  \n*Tidak asam, tidak basa*") 
    st.success("🧪 **Gas**: 150-300 ppm  \n*Produksi gas yang bagus*")
    
    st.info("""
    **📖 Penjelasan Singkat:**
    
    🌡️ **Suhu Ideal**: Seperti suhu tubuh manusia, bakteri penghasil gas suka kondisi hangat
    
    ⚗️ **pH Netral**: Tidak boleh terlalu asam (seperti cuka) atau terlalu basa (seperti sabun)
    
    🧪 **Gas Metana**: Semakin tinggi, semakin bagus untuk memasak atau listrik
    """)
    
    st.subheader("📊 Ringkasan Hari Ini")
    if st.session_state.sensor_history:
        df = pd.DataFrame(st.session_state.sensor_history)
        
        avg_temp = df['temperature'].mean()
        avg_ph = df['ph'].mean()
        avg_methane = df['methane'].mean()
        
        temp_status = "🟢 Bagus" if 35 <= avg_temp <= 40 else "🟡 Cukup" if 30 <= avg_temp <= 45 else "🔴 Perlu Diperbaiki"
        ph_status = "🟢 Bagus" if 6.8 <= avg_ph <= 7.2 else "🟡 Cukup" if 6.0 <= avg_ph <= 8.5 else "🔴 Perlu Diperbaiki"
        gas_status = "🟢 Bagus" if 150 <= avg_methane <= 300 else "🟡 Cukup" if 80 <= avg_methane <= 350 else "🔴 Perlu Diperbaiki"
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Suhu Rata-rata:**")
            st.write(f"{avg_temp:.1f}°C")
            st.caption(temp_status)
        with col2:
            st.write("**pH Rata-rata:**")
            st.write(f"{avg_ph:.1f}")
            st.caption(ph_status)
        
        st.write("**Gas Rata-rata:**")
        st.write(f"{avg_methane:.0f} ppm")
        st.caption(gas_status)
    
    st.subheader("🔧 Aksi Cepat")
    if st.button("🗑️ Bersihkan Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("📤 Unduh Data"):
        if st.session_state.sensor_history:
            df = pd.DataFrame(st.session_state.sensor_history)
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download Data CSV",
                data=csv,
                file_name=f"data_biogas_{time.strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    st.subheader("💡 Tips Harian")
    tips_list = [
        "🔄 Aduk campuran setiap 2-3 hari",
        "🥬 Tambahkan sayuran busuk untuk nutrisi",
        "🌡️ Jaga suhu tetap hangat dengan selimut",
        "💧 Pastikan tidak ada kebocoran udara",
        "🧪 Cek gas setiap hari untuk keamanan"
    ]
    
    for tip in tips_list:
        st.write(f"• {tip}")
    
    st.divider()
    st.subheader("🆘 Kontak Darurat")
    st.error("""
    **Jika ada masalah serius:**
    
    📞 **Teknisi Bioserde:**  
    +62-123-1234-1234
    
    🚨 **Emergency:**
    - Matikan katup gas jika bocor
    - Ventilasi ruangan
    - Jangan nyalakan api
    """)
    
    st.subheader("⚠️ Tanda Bahaya")
    st.warning("""
    **Segera hubungi teknisi jika:**
    
    🔴 Bau gas yang menyengat
    🔴 Suhu di atas 50°C
    🔴 pH di bawah 6.0
    🔴 Tidak ada produksi gas > 3 hari
    🔴 Ada suara aneh dari sistem
    """)

if auto_refresh:
    placeholder = st.empty()
    for i in range(5, 0, -1):
        placeholder.info(f"🔄 Auto refresh dalam {i} detik...")
        time.sleep(1)
    placeholder.empty()
    st.rerun()

st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🏭 <strong>Dashboard Biogas Bioserde</strong></p>
</div>
""", unsafe_allow_html=True)