import os
from music_analyzer import MusicDropAnalyzer

def list_songs(folder_path):
    """Klasördeki müzik dosyalarını listele"""
    music_files = []
    for file in os.listdir(folder_path):
        if file.endswith(('.mp3', '.wav')):
            music_files.append(file)
    return music_files

def main():
    # Şarkıların bulunduğu klasör
    songs_folder = "songs"
    
    # Klasör yoksa oluştur
    if not os.path.exists(songs_folder):
        os.makedirs(songs_folder)
        print(f"'{songs_folder}' klasörü oluşturuldu.")
        print("Lütfen müzik dosyalarınızı bu klasöre ekleyin.")
        return

    # Mevcut şarkıları listele
    songs = list_songs(songs_folder)
    
    if not songs:
        print("Hiç şarkı bulunamadı!")
        print(f"Lütfen müzik dosyalarınızı '{songs_folder}' klasörüne ekleyin.")
        return
    
    # Şarkıları listele
    print("\nMevcut şarkılar:")
    for i, song in enumerate(songs, 1):
        print(f"{i}. {song}")
    
    # Kullanıcıdan şarkı seçmesini iste
    while True:
        try:
            choice = int(input("\nAnaliz etmek istediğiniz şarkının numarasını girin: "))
            if 1 <= choice <= len(songs):
                selected_song = songs[choice-1]
                break
            else:
                print("Geçersiz numara! Lütfen tekrar deneyin.")
        except ValueError:
            print("Lütfen bir sayı girin!")
    
    # Analiz parametrelerini al
    try:
        threshold = float(input("Threshold değerini girin (0.0-1.0 arası, önerilen: 0.5): "))
        min_distance = float(input("Minimum drop aralığını girin (saniye, önerilen: 1.0): "))
    except ValueError:
        print("Geçersiz değer! Varsayılan değerler kullanılacak.")
        threshold = 0.5
        min_distance = 1.0
    
    # Analyzer'ı oluştur ve şarkıyı yükle
    analyzer = MusicDropAnalyzer()
    song_path = os.path.join(songs_folder, selected_song)
    
    print(f"\nŞarkı yükleniyor: {selected_song}")
    analyzer.load_song(song_path)
    
    # Drop noktalarını analiz et
    print("\nDrop noktaları analiz ediliyor...")
    drops = analyzer.analyze_drops(threshold=threshold, min_distance_sec=min_distance)
    print(f"Drop noktaları (saniye): {drops}")
    
    print("\nGörselleştirme oluşturuluyor...")
    analyzer.visualize_analysis(save_path=f"analiz_{selected_song}.png")
    
    
    choice = input("\nŞarkıyı çalarak gerçek zamanlı analiz görmek ister misiniz? (E/H): ")
    if choice.lower() == 'e':
        print("\nŞarkı çalınıyor... (Durdurmak için Ctrl+C)")
        try:
            analyzer.play_with_visualization()
        except KeyboardInterrupt:
            print("\nProgram durduruldu!")

if __name__ == "__main__":
    main()