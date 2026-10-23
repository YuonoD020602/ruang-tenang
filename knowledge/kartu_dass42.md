# Kartu Pengetahuan DASS-42

Dokumen ini menjadi sumber chatbot untuk menjelaskan DASS-42, cara membaca hasilnya, dan batas-batasnya. Bahasa dibuat sederhana agar mudah dipahami pengguna awam.

## Apa itu DASS-42

DASS-42 (Depression Anxiety Stress Scales) adalah kuesioner berisi 42 pernyataan untuk mengukur tiga keadaan emosi negatif: depresi, kecemasan, dan stres. Kuesioner ini disusun oleh S.H. Lovibond dan P.F. Lovibond (1995) dari University of New South Wales, Australia.

Setiap pernyataan menanyakan seberapa sering atau seberapa kuat suatu keadaan dialami **selama satu minggu terakhir**. DASS-42 dikembangkan pada orang dewasa dan remaja akhir (usia 17 tahun ke atas) dari populasi umum, bukan pasien.

## Tiga skala dan apa yang diukur

Setiap skala terdiri dari 14 pernyataan.

**Depresi** mengukur keadaan seperti:
- suasana hati murung atau sedih
- merasa tidak ada harapan
- merasa hidup tidak berarti
- merendahkan diri sendiri atau merasa tidak berharga
- kehilangan minat dan tidak bisa menikmati hal-hal yang biasanya menyenangkan
- sulit memulai atau menggerakkan diri untuk berbuat sesuatu

**Kecemasan** mengukur keadaan seperti:
- reaksi tubuh, misalnya jantung berdebar, mulut kering, atau sulit bernapas tanpa sebab fisik
- gemetar atau tubuh terasa lemas
- rasa cemas dalam situasi tertentu, misalnya takut panik di depan orang lain
- perasaan takut atau panik yang dirasakan

**Stres** mengukur ketegangan yang berlangsung terus-menerus, seperti:
- sulit bersantai
- tegang atau gelisah
- mudah kesal atau tersinggung
- bereaksi berlebihan terhadap situasi
- tidak sabar

Perbedaan kecemasan dan stres: kecemasan lebih berkaitan dengan reaksi takut yang muncul tiba-tiba, sedangkan stres lebih berkaitan dengan ketegangan yang menetap dalam waktu lama.

## Cara menghitung skor

Setiap pernyataan dijawab dengan salah satu dari empat pilihan:
- 0 = tidak sesuai dengan saya sama sekali
- 1 = sesuai dengan saya sampai tingkat tertentu, atau kadang-kadang
- 2 = sesuai dengan saya sampai batas yang cukup besar, atau cukup sering
- 3 = sangat sesuai dengan saya, atau hampir selalu

Skor tiap skala adalah jumlah jawaban dari 14 pernyataan milik skala itu. Rentang skor tiap skala adalah 0 sampai 42. Semakin tinggi skor, semakin berat keadaan yang dilaporkan.

## Tingkat keparahan

| Tingkat | Depresi | Kecemasan | Stres |
|---|---|---|---|
| Normal | 0–9 | 0–7 | 0–14 |
| Ringan | 10–13 | 8–9 | 15–18 |
| Sedang | 14–20 | 10–14 | 19–25 |
| Berat | 21–27 | 15–19 | 26–33 |
| Sangat berat | 28 ke atas | 20 ke atas | 34 ke atas |

Batas tiap skala berbeda. Contohnya, skor 15 berarti "berat" pada skala kecemasan, tetapi masih "ringan" pada skala stres. Karena itu, skor antarskala tidak bisa langsung dibandingkan; yang dibandingkan adalah tingkatnya.

## Cara membaca hasil

- **Hasil DASS-42 adalah hasil skrining, bukan diagnosis.** Skor tinggi menunjukkan seseorang melaporkan banyak keluhan dalam seminggu terakhir. Skor itu tidak menentukan apakah seseorang memiliki gangguan mental tertentu.
- **DASS-42 memandang keluhan sebagai rentang, bukan kotak.** Perbedaan antara orang dengan skor rendah dan skor tinggi adalah perbedaan seberapa berat keluhannya, bukan perbedaan jenis.
- **Hasil bisa berubah.** Karena yang ditanyakan adalah satu minggu terakhir, skor bisa naik atau turun mengikuti keadaan, misalnya saat sedang banyak tekanan.
- **Pola tiga skala lebih bermakna daripada satu angka.** Misalnya, stres tinggi dengan depresi dan kecemasan rendah menunjukkan pola yang berbeda dari tiga skala yang semuanya tinggi.
- **Penafsiran yang tepat perlu tenaga profesional.** Untuk orang yang sedang mencari bantuan atau mengalami tekanan berat, hasil DASS sebaiknya dibaca bersama psikolog atau tenaga kesehatan yang terlatih.

## Hal yang tidak diukur DASS-42

- DASS-42 **tidak berisi pertanyaan tentang keinginan menyakiti diri atau mengakhiri hidup.** Skor rendah tidak berarti risiko itu tidak ada. Siapa pun yang memiliki pikiran seperti itu perlu segera menghubungi layanan bantuan, apa pun hasil skornya.
- DASS-42 tidak memeriksa penyebab keluhan, misalnya kondisi fisik, efek obat, atau kejadian hidup tertentu.
- DASS-42 tidak menentukan jenis penanganan yang dibutuhkan.

## Tentang aplikasi ini

- Aplikasi ini adalah **proyek belajar dan alat peraga**, bukan layanan kesehatan.
- Pengguna **tidak mengisi kuesioner sendiri.** Aturan penggunaan DASS tidak mengizinkan kuesioner ini diberikan lewat website atau aplikasi yang terbuka untuk umum. Karena itu, aplikasi menampilkan contoh hasil dari responden anonim dalam dataset publik.
- Data berasal dari survei DASS-42 online yang terbuka di Open Psychometrics (2017–2019). Setelah dibersihkan, data berisi sekitar 31 ribu responden dewasa.
- **Data ini tidak mewakili masyarakat Indonesia.** Pengisinya sukarela, lebih dari separuh berasal dari Malaysia, dan hanya sebagian kecil dari Indonesia. Orang yang sedang merasa tidak baik cenderung lebih tertarik mengikuti tes seperti ini, sehingga proporsi skor tinggi dalam data jauh lebih besar daripada di masyarakat umum.

## Tiga cara aplikasi membaca hasil

1. **Skoring resmi** adalah hasil utama. Skor dan tingkat dihitung langsung dengan aturan baku DASS-42 di atas.
2. **Model klasifikasi** adalah pembanding. Model ini dilatih menebak tingkat keparahan dari 42 jawaban. Karena belajar dari jawaban yang sama dengan skoring resmi, hasilnya hampir selalu sama. Kalau berbeda, skoring resmi yang dipakai.
3. **Profil pola respons** adalah informasi tambahan. Model pengelompokan menempatkan responden ke kelompok yang pola jawabannya mirip. Profil ini hanya menggambarkan kemiripan pola, bukan kategori klinis.

## Kapan sebaiknya mencari bantuan profesional

Sebaiknya berbicara dengan psikolog, dokter, atau tenaga kesehatan jika:
- keluhan berlangsung lebih dari dua minggu atau terus berulang,
- keluhan mengganggu pekerjaan, sekolah, hubungan, tidur, atau makan,
- merasa tidak sanggup mengatasinya sendiri,
- muncul pikiran untuk menyakiti diri atau mengakhiri hidup. Dalam keadaan ini, segera hubungi layanan bantuan.

Pilihan awal yang bisa dihubungi: puskesmas atau rumah sakit terdekat, psikolog, atau layanan Healing119.id dari Kementerian Kesehatan (telepon 119 ekstensi 8).

## Sumber

- Lovibond, S.H., & Lovibond, P.F. (1995). *Manual for the Depression Anxiety Stress Scales* (2nd ed.). Sydney: Psychology Foundation.
- DASS – Overview of the DASS and its uses. University of New South Wales. https://dass.psy.unsw.edu.au/over.htm
- DASS – Frequently Asked Questions. University of New South Wales. https://dass.psy.unsw.edu.au/DASSFAQ.htm
- PsyToolkit – Depression Anxiety Stress Scales (tabel batas skor DASS-42). https://psytoolkit.org/survey-library/depression-anxiety-stress-dass.html
- Open Psychometrics (2019). Depression Anxiety and Stress Scale Survey [dataset]. https://openpsychometrics.org/_rawdata/DASS_data_21.02.19.zip
