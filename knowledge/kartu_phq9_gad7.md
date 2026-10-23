# Kartu Pengetahuan PHQ-9 dan GAD-7

Dokumen ini menjadi sumber chatbot untuk menjelaskan kuesioner PHQ-9 dan GAD-7, cara membaca hasilnya, dan batas-batasnya.

## Apa itu PHQ-9 dan GAD-7

PHQ-9 (Patient Health Questionnaire-9) adalah kuesioner 9 pertanyaan untuk menyaring gejala depresi. GAD-7 (Generalized Anxiety Disorder-7) adalah kuesioner 7 pertanyaan untuk menyaring gejala kecemasan. Keduanya dikembangkan oleh Spitzer, Williams, Kroenke, dan rekan, serta banyak dipakai di layanan kesehatan primer di berbagai negara.

Kedua kuesioner menanyakan seberapa sering suatu keluhan dialami **selama 2 minggu terakhir**. Keduanya boleh digandakan, diterjemahkan, dan ditampilkan tanpa izin khusus.

## Apa yang ditanyakan

**PHQ-9 (depresi)** menanyakan sembilan keluhan: kehilangan minat atau gairah, suasana hati murung atau putus asa, masalah tidur, lelah atau kurang tenaga, perubahan nafsu makan, merasa gagal atau kurang berharga, sulit berkonsentrasi, gerakan atau bicara melambat atau justru gelisah, serta pikiran lebih baik mati atau ingin melukai diri.

**GAD-7 (kecemasan)** menanyakan tujuh keluhan: gugup atau tegang, sulit menghentikan rasa khawatir, terlalu mengkhawatirkan banyak hal, sulit bersantai, gelisah hingga sulit duduk diam, mudah kesal, dan rasa takut seolah sesuatu yang buruk akan terjadi.

## Cara menghitung skor

Setiap pertanyaan dijawab dengan salah satu dari empat pilihan:
- 0 = tidak pernah
- 1 = beberapa hari
- 2 = lebih dari separuh waktu
- 3 = hampir setiap hari

Skor PHQ-9 adalah jumlah 9 jawaban (rentang 0–27). Skor GAD-7 adalah jumlah 7 jawaban (rentang 0–21). Semakin tinggi skor, semakin banyak atau semakin sering keluhan yang dilaporkan.

## Tingkat keluhan

PHQ-9 (depresi):

| Skor | Tingkat |
|---|---|
| 0–4 | Minimal |
| 5–9 | Ringan |
| 10–14 | Sedang |
| 15–19 | Sedang–berat |
| 20–27 | Berat |

GAD-7 (kecemasan):

| Skor | Tingkat |
|---|---|
| 0–4 | Minimal |
| 5–9 | Ringan |
| 10–14 | Sedang |
| 15–21 | Berat |

Skor 10 ke atas pada salah satu kuesioner umumnya dipakai sebagai tanda bahwa sebaiknya dilakukan pemeriksaan lanjutan oleh tenaga profesional.

## Cara membaca hasil

- **Hasil PHQ-9 dan GAD-7 adalah hasil skrining, bukan diagnosis.** Skor tinggi menunjukkan banyak keluhan yang dilaporkan dalam dua minggu terakhir. Skor tidak menentukan apakah seseorang memiliki gangguan tertentu.
- **Hasil bisa berubah.** Karena yang ditanyakan dua minggu terakhir, skor bisa naik atau turun mengikuti keadaan.
- **Depresi dan kecemasan sering muncul bersamaan.** Skor keduanya biasanya bergerak searah. Pola keluhan, misalnya lebih banyak keluhan tidur dan lelah atau lebih banyak rasa khawatir, bisa membantu memahami keadaan seseorang.
- **Penafsiran yang tepat perlu tenaga profesional.** Psikolog atau dokter akan menilai hasil bersama riwayat dan keadaan orang tersebut.

## Pertanyaan nomor 9 PHQ-9

Pertanyaan nomor 9 menanyakan pikiran bahwa lebih baik mati atau ingin melukai diri. **Jawaban apa pun selain "tidak pernah" perlu ditanggapi serius, berapa pun skor totalnya.** Dalam keadaan ini sebaiknya segera berbicara dengan orang yang dipercaya dan menghubungi layanan bantuan, misalnya Healing119.id (telepon 119 ekstensi 8), atau datang ke IGD rumah sakit terdekat bila dalam bahaya.

## Hal yang tidak diukur

- Kuesioner ini tidak memeriksa penyebab keluhan, misalnya kondisi fisik, efek obat, atau kejadian hidup tertentu.
- Kuesioner ini tidak menentukan jenis penanganan yang dibutuhkan.
- Aplikasi ini tidak mengukur stres secara khusus. Untuk mengelola stres, chatbot merujuk panduan WHO "Hal yang Perlu Dilakukan Saat Stres".

## Tentang aplikasi ini

- Aplikasi ini adalah **proyek belajar**, bukan layanan kesehatan.
- **Jawaban pengguna tidak disimpan.** Jawaban hanya dipakai untuk menghitung hasil saat itu.
- Model dalam aplikasi dilatih dari dataset terbuka berisi jawaban PHQ-9 dan GAD-7 sekitar 24 ribu mahasiswa di Tiongkok (2021). **Data ini tidak mewakili masyarakat Indonesia**, sehingga perbandingan dengan kelompok dalam data hanya bersifat gambaran.

## Tiga cara aplikasi membaca hasil

1. **Skoring resmi** adalah hasil utama. Skor dan tingkat dihitung dengan aturan baku di atas.
2. **Model klasifikasi** adalah pembanding. Model ini dilatih menebak tingkat dari jawaban item. Karena belajar dari jawaban yang sama dengan skoring resmi, hasilnya hampir selalu sama. Kalau berbeda, skoring resmi yang dipakai.
3. **Profil pola keluhan** adalah informasi tambahan. Model pengelompokan menempatkan jawaban ke kelompok yang pola keluhannya mirip, misalnya keluhan yang paling menonjol adalah tidur dan kelelahan, atau rasa khawatir. Profil ini hanya menggambarkan kemiripan pola, bukan kategori klinis.

## Kapan sebaiknya mencari bantuan profesional

Sebaiknya berbicara dengan psikolog, dokter, atau tenaga kesehatan jika:
- skor PHQ-9 atau GAD-7 10 ke atas,
- keluhan berlangsung lebih dari dua minggu atau terus berulang,
- keluhan mengganggu pekerjaan, sekolah, hubungan, tidur, atau makan,
- merasa tidak sanggup mengatasinya sendiri,
- muncul pikiran untuk menyakiti diri atau mengakhiri hidup. Dalam keadaan ini, segera hubungi layanan bantuan.

Pilihan awal yang bisa dihubungi: puskesmas atau rumah sakit terdekat, psikolog, atau layanan Healing119.id dari Kementerian Kesehatan (telepon 119 ekstensi 8).

## Sumber

- Kroenke, K., Spitzer, R.L., & Williams, J.B.W. (2001). The PHQ-9: Validity of a brief depression severity measure. *Journal of General Internal Medicine*, 16(9), 606–613.
- Spitzer, R.L., Kroenke, K., Williams, J.B.W., & Löwe, B. (2006). A brief measure for assessing generalized anxiety disorder: The GAD-7. *Archives of Internal Medicine*, 166(10), 1092–1097.
- Su, Z. (2023). Temporal dynamics in psychological assessments [dataset]. Zenodo. https://zenodo.org/records/10423537 (CC BY 4.0)
