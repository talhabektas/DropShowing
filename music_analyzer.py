import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sounddevice as sd
import time

class MusicDropAnalyzer:
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.drops = None
        self.onset_env = None
        self.times = None
        
    def load_song(self, file_path):
        """Şarkıyı yükle ve analiz et"""
        print(f"Şarkı yükleniyor: {file_path}")
        self.audio_data, self.sample_rate = librosa.load(file_path)
        print("Şarkı yüklendi!")
        
    def analyze_drops(self, threshold=0.5, min_distance_sec=1):
        """Şarkıdaki drop noktalarını tespit et"""
        if self.audio_data is None:
            raise ValueError("Önce bir şarkı yüklemelisiniz!")
            
        # Onset strength (ses yüksekliği değişimi) hesapla
        self.onset_env = librosa.onset.onset_strength(
            y=self.audio_data, 
            sr=self.sample_rate,
            hop_length=512,
            aggregate=np.median
        )
        
        # Zamanları hesapla
        self.times = librosa.times_like(self.onset_env, sr=self.sample_rate, hop_length=512)
        
        # Drop noktalarını bul
        min_distance = int(min_distance_sec * self.sample_rate / 512)
        peaks, _ = find_peaks(
            self.onset_env,
            height=threshold,
            distance=min_distance
        )
        
        # Drop zamanlarını kaydet
        self.drops = self.times[peaks]
        
        return self.drops
    
    def visualize_analysis(self, save_path=None):
        """Analiz sonuçlarını görselleştir"""
        if self.onset_env is None:
            raise ValueError("Önce analiz yapmalısınız!")
            
        plt.figure(figsize=(15, 8))
        
        # Üst grafik: Dalga formu
        plt.subplot(2, 1, 1)
        librosa.display.waveshow(self.audio_data, sr=self.sample_rate, alpha=0.5)
        plt.title("Şarkı Dalga Formu")
        
        # Drop noktalarını işaretle
        if self.drops is not None:
            plt.vlines(self.drops, -1, 1, color='r', alpha=0.7, label='Drops')
        plt.legend()
        
        # Alt grafik: Onset strength
        plt.subplot(2, 1, 2)
        plt.plot(self.times, self.onset_env, alpha=0.8, label='Onset strength')
        plt.vlines(self.drops, 0, max(self.onset_env), color='r', alpha=0.7)
        plt.title("Ses Yüksekliği Değişimi ve Drop Noktaları")
        plt.xlabel("Zaman (saniye)")
        plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Görsel kaydedildi: {save_path}")
        
        plt.show()
        
    def play_with_visualization(self, start_time=0):
        """Şarkıyı çal ve gerçek zamanlı görselleştirme yap"""
        if self.audio_data is None:
            raise ValueError("Önce bir şarkı yüklemelisiniz!")
            
        # Çalma pozisyonunu hesapla
        start_idx = int(start_time * self.sample_rate)
        audio_to_play = self.audio_data[start_idx:]
        
        # Gerçek zamanlı görselleştirme için figür oluştur
        plt.ion()
        fig, ax = plt.subplots(figsize=(10, 4))
        line, = ax.plot(self.times, self.onset_env)
        current_line = ax.axvline(x=start_time, color='r')
        
        # Drop noktalarını göster
        if self.drops is not None:
            ax.vlines(self.drops, 0, max(self.onset_env), color='g', alpha=0.5)
        
        plt.title("Gerçek Zamanlı Analiz")
        plt.xlabel("Zaman (saniye)")
        plt.ylabel("Ses Yüksekliği")
        
        # Şarkıyı çal
        sd.play(audio_to_play, self.sample_rate)
        
        # Gerçek zamanlı güncelleme
        start_time_ref = time.time()
        try:
            while sd.get_stream().active:
                current_time = time.time() - start_time_ref + start_time
                current_line.set_xdata([current_time, current_time])
                
                # Şu anki drop noktasını kontrol et
                if self.drops is not None:
                    current_drops = self.drops[
                        (self.drops >= current_time) & 
                        (self.drops < current_time + 0.1)
                    ]
                    if len(current_drops) > 0:
                        print(f"DROP! Zaman: {current_time:.2f}")
                
                plt.pause(0.01)
                
        except KeyboardInterrupt:
            sd.stop()
            
        plt.ioff()
        plt.close()