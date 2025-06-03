import serial
import time
import json
import random
from datetime import datetime

# Konfigurasi
PORT = 'COM3'
BAUD = 9600
CHECK_INTERVAL = 15  # Detik antara prediksi

def main():
    print("\n===== BIOSERDE SIMPLE BRIDGE =====")
    print("Koneksi Serial dengan Prediksi Lokal")
    print("===================================\n")
    
    ser = None
    last_check = 0
    last_data = None
    
    try:
        print(f"Menghubungkan ke Arduino ({PORT})...")
        ser = serial.Serial(PORT, BAUD, timeout=2)
        print(f"✓ Terhubung ke Arduino")
        
        # Beri waktu Arduino boot ulang
        time.sleep(3)
        ser.reset_input_buffer()
        
        print("\nMonitoring data biogas (Ctrl+C untuk keluar)")
        print("------------------------------------------\n")
        
        while True:
            # Baca data dari serial
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    
                    # Cek apakah ini data JSON
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            data = json.loads(line)
                            ph = data.get('ph')
                            biogas = data.get('biogas_production')
                            
                            if ph is not None and biogas is not None:
                                last_data = data
                                print(f"Data baru: pH={ph:.1f}, biogas={biogas:.1f} m³")
                        except json.JSONDecodeError:
                            print(f"Arduino: {line}")
                    elif line:
                        print(f"Arduino: {line}")
                except Exception as e:
                    print(f"Error reading: {str(e)}")
            
            # Waktu untuk prediksi?
            current_time = time.time()
            if current_time - last_check >= CHECK_INTERVAL and last_data:
                check_status(ser, last_data)
                last_check = current_time
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Koneksi serial ditutup")

def check_status(ser, data):
    """Prediksi status sistem biogas dan kirim ke Arduino"""
    print("\n----- Analisis Status -----")
    
    # Ambil nilai
    ph = data.get('ph', 7.0)
    biogas = data.get('biogas_production', 50.0)
    
    # Prediksi sederhana
    is_anomaly = False
    cause = ""
    
    # Aturan sederhana
    if ph < 6.5 or ph > 8.0:
        is_anomaly = True
        cause = "pH Level"
    elif biogas < 25.0 or biogas > 85.0:
        is_anomaly = True
        cause = "Biogas Production"
    
    # Kadang-kadang buat anomali acak untuk demo
    if not is_anomaly and random.random() < 0.15:  # 15% anomali acak
        is_anomaly = True
        cause = random.choice(["pH Level", "Biogas Production"])
    
    # Tampilkan hasil
    print(f"Waktu: {datetime.now().strftime('%H:%M:%S')}")
    print(f"pH: {ph:.1f} (normal: 6.5-8.0)")
    print(f"Biogas: {biogas:.1f} m³ (normal: 25-85)")
    print(f"Status: {'⚠️ ANOMALI' if is_anomaly else '✓ Normal'}")
    if is_anomaly:
        print(f"Penyebab: {cause}")
    
    # Kirim hasil ke Arduino
    command = f"RESULT:{1 if is_anomaly else 0},{cause}\n"
    print(f"→ Mengirim ke Arduino: {command.strip()}")
    
    try:
        ser.write(command.encode())
    except Exception as e:
        print(f"Error mengirim perintah: {str(e)}")
    
    print("----- Analisis Selesai -----")

if __name__ == "__main__":
    main()