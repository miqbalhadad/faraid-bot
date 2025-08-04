🕌 Chatbot Telegram Perhitungan Warisan Islam (Faraid)

Bot Telegram yang mengimplementasikan dua metode AI untuk menghitung pembagian warisan berdasarkan hukum Islam:

    Forward Chaining - Sistem berbasis aturan IF-THEN
    Dempster-Shafer Theory - Sistem berbasis tingkat kepercayaan

📋 Deskripsi Proyek

Proyek ini dikembangkan untuk keperluan penelitian skripsi yang menggabungkan teknologi AI dengan hukum Islam dalam perhitungan warisan (Faraid). Bot menggunakan dua pendekatan berbeda untuk memberikan perbandingan metodologi dalam menangani ketidakpastian dan kompleksitas aturan warisan Islam.
🎯 Fitur Utama

    ✅ Perhitungan Forward Chaining: Menggunakan aturan IF-THEN berdasarkan Al-Quran dan Hadits
    ✅ Perhitungan Dempster-Shafer: Menangani ketidakpastian dengan belief functions
    ✅ Interface Telegram: Mudah digunakan melalui chat bot
    ✅ Perbandingan Metode: Menampilkan hasil kedua metode secara bersamaan
    ✅ Validasi Input: Memastikan konsistensi data ahli waris
    ✅ Penjelasan Detail: Memberikan reasoning untuk setiap keputusan

🏗️ Struktur Proyek

warisan-bot/
│
├── main.py              # Bot utama dan conversation handler
├── forward.py           # Implementasi Forward Chaining
├── dempster.py          # Implementasi Dempster-Shafer Theory
├── requirements.txt     # Dependencies Python
├── README.md           # Dokumentasi proyek
└── .env                # File konfigurasi (buat manual)

🚀 Instalasi dan Setup
1. Clone atau Download Proyek
bash

git clone <repository-url>
cd warisan-bot

2. Install Dependencies
bash

pip install -r requirements.txt

3. Buat Bot Telegram

    Chat dengan @BotFather di Telegram
    Ketik /newbot dan ikuti instruksi
    Simpan token bot yang diberikan

4. Konfigurasi

Buka file main.py dan ganti "YOUR_BOT_TOKEN_HERE" dengan token bot Anda:
python

TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

5. Jalankan Bot
bash

python main.py

📖 Cara Penggunaan
Memulai Perhitungan

    Start chat dengan bot di Telegram
    Ketik /start untuk melihat welcome message
    Ketik /hitung untuk memulai perhitungan warisan

Input Data Ahli Waris

Bot akan menanyakan satu per satu:

    Anak laki-laki (jumlah)
    Anak perempuan (jumlah)
    Suami/Istri (jumlah)
    Ayah/Ibu (ada/tidak)
    Saudara laki-laki/perempuan (jumlah)

Pilih Metode Perhitungan

    Forward Chaining: Hasil berdasarkan aturan pasti
    Dempster-Shafer: Hasil dengan tingkat kepercayaan
    Bandingkan Kedua: Menampilkan perbandingan metode

🔬 Metodologi
Forward Chaining

Menggunakan sistem production rules dengan format:

IF (kondisi ahli waris) THEN (bagian warisan)

Contoh aturan:

    IF ada anak laki-laki dan perempuan THEN bagian laki-laki = 2x perempuan
    IF suami dan ada anak THEN suami = 1/4
    IF istri dan tidak ada anak THEN istri = 1/4

Dempster-Shafer Theory

Menggunakan:

    Frame of Discernment (Θ): Set semua ahli waris
    Basic Probability Assignment (BPA): Mass function untuk setiap evidence
    Belief Functions: Tingkat kepercayaan minimum
    Plausibility Functions: Tingkat kepercayaan maksimum
    Dempster's Rule: Kombinasi multiple evidence

📊 Contoh Output
Forward Chaining

🔗 METODE FORWARD CHAINING

📜 Aturan yang Diterapkan:
- Anak laki-laki dan perempuan: laki-laki = 2x perempuan
- Ibu mendapat 1/6 karena ada anak

💰 Hasil Pembagian:
- Anak Laki-laki: 2/3 = 66.67%
- Anak Perempuan: 1/3 = 33.33%
- Ibu: 1/6 = 16.67%

Dempster-Shafer

🎯 METODE DEMPSTER-SHAFER THEORY

📊 Evidence dan Belief Functions:
- Evidence Keberadaan Anak (Reliabilitas: 0.95)
- Evidence Keberadaan Orang Tua (Reliabilitas: 0.80)

💰 Hasil Pembagian:
- Anak Laki-laki: 1/2 = 50.00% (Belief: 0.456)
- Anak Perempuan: 1/4 = 25.00% (Belief: 0.234)
- Ibu: 1/6 = 16.67% (Belief: 0.189)

🎲 Tingkat Kepastian Total: 0.879

🧪 Testing

Jalankan test cases:
bash

pytest test_forward.py
pytest test_dempster.py

Contoh test case:
python

def test_basic_inheritance():
    heirs = {'anak_laki': 1, 'anak_perempuan': 1, 'ibu': 1}
    fc = ForwardChaining()
    result = fc.calculate_inheritance(heirs)
    assert 'Anak Laki-laki' in result['shares']
    assert result['shares']['Anak Laki-laki']['percentage'] > 0

📚 Referensi Hukum Islam
Al-Quran

    QS. An-Nisa (4): 11 - Pembagian untuk anak
    QS. An-Nisa (4): 12 - Pembagian untuk suami/istri dan orang tua
    QS. An-Nisa (4): 176 - Pembagian untuk saudara

Hadits

    HR. Bukhari: "Berikanlah faraidh kepada ahlinya"
    HR. Muslim: Tentang pembagian 'asabah

Konsep Fiqh

    Faraidh: Bagian yang telah ditentukan
    'Asabah: Ahli waris yang mendapat sisa
    'Awl: Pengurangan proporsional jika total > 1
    Radd: Penambahan jika ada sisa

🔧 Kustomisasi
Menambah Aturan Forward Chaining
python

self.rules.append({
    'name': 'Aturan Baru',
    'condition': lambda facts: kondisi_anda,
    'action': self._action_function,
    'description': 'Deskripsi aturan'
})

Menambah Evidence Dempster-Shafer
python

evidence_sources.append({
    'name': 'Evidence Baru',
    'mass_function': mass_func_dict,
    'reliability': 0.85
})

🐛 Troubleshooting
Bot Tidak Merespons

    Pastikan token bot benar
    Cek koneksi internet
    Lihat log error di terminal

Error Perhitungan

    Pastikan input valid (tidak negatif)
    Cek konsistensi data (tidak boleh suami dan istri bersamaan)
    Lihat log untuk detail error

Hasil Tidak Sesuai

    Validasi dengan perhitungan manual
    Cek aturan yang diterapkan
    Bandingkan dengan referensi fiqh

📝 Pengembangan Lebih Lanjut
Fitur Tambahan

    Export hasil ke PDF
    Visualisasi grafik
    Database untuk menyimpan riwayat
    Multi-language support
    Web interface
    API REST

Optimisasi

    Caching hasil perhitungan
    Parallel processing untuk multiple evidence
    Machine learning untuk optimasi belief values
    Fuzzy logic integration

👥 Kontribusi

Proyek ini dikembangkan untuk keperluan akademis. Kontribusi dan saran perbaikan sangat diterima:

    Fork repository
    Buat branch baru (git checkout -b feature/AmazingFeature)
    Commit changes (git commit -m 'Add some AmazingFeature')
    Push ke branch (git push origin feature/AmazingFeature)
    Buat Pull Request

📄 Lisensi

Proyek ini dibuat untuk keperluan edukatif dan penelitian skripsi. Penggunaan untuk tujuan komersial memerlukan izin khusus.
⚠️ Disclaimer

Bot ini adalah alat bantu edukatif dan penelitian. Untuk kasus warisan yang kompleks atau memiliki implikasi hukum, selalu konsultasikan dengan ahli hukum Islam yang berkompeten.
📞 Kontak

    Author: [Nama Anda]
    Email: [email@anda.com]
    University: [Nama Universitas]
    Department: [Jurusan/Program Studi]

Semoga Allah SWT memberikan kemudahan dalam menuntut ilmu dan mengamalkannya. Aamiin. 🤲
