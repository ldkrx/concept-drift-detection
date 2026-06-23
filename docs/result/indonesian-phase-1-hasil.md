## LAPORAN RESMI EKSEKUSI FASE 1: PENGUMPULAN DAN PRA-PEMROSESAN DATA

## I. Akuisisi & Pembersihan Dataset

- **Pemilihan Dataset Utama:** Kita sepakat menggunakan data historis Indeks Harga Saham Gabungan (IHSG) dengan ticker ^JKSE yang diambil dari Yahoo Finance, mencakup rentang waktu dari tahun 2010. Penggunaan indeks pasar lokal ini ditujukan untuk memberikan nilai novelty yang kuat pada target publikasi Seminar Nasional.
- **Pembersihan Format dan Data Kosong:** Data mentah telah dirapikan dengan menghapus baris header yang tidak diperlukan dan mengatur kolom tanggal (Date) sebagai indeks berformat Datetime. Data yang kosong (missing values), seperti pada hari libur bursa, telah diatasi menggunakan metode forward-fill (ffill) untuk menjaga kontinuitas deret waktu tanpa memasukkan bias informasi dari masa depan.
- **Transformasi Stasioneritas:** Harga penutupan absolut telah dikonversi menjadi persentase pengembalian logaritmik harian (Log_Return). Langkah ini krusial untuk menormalkan distribusi data finansial.

## II. Rekayasa Fitur & Transformasi

- **Ekstraksi Fitur Volatilitas (Rolling Volatility):** Kita telah menghitung dan menambahkan fitur simpangan baku bergulir untuk memantau fluktuasi pasar, yaitu volatilitas dalam jendela waktu 20-hari (Vol_20d) dan 60-hari (Vol_60d).
- **Perhitungan Indikator Teknikal dan Momentum:** Untuk menangkap sinyal pergerakan tren dan harga jangka pendek, dataset telah diperkaya dengan:
  - Exponential Moving Average 5-hari (EMA_5d).
  - Tiga batas Bollinger Bands 5-hari, yang terdiri dari pita tengah (BB_Mid), pita atas (BB_Upper), dan pita bawah (BB_Lower).
  - Momentum arah tren berdasarkan perhitungan kumulatif log-return selama 5 hari (Momentum_5d) dan 20 hari (Momentum_20d).

## III. Profil Dataset Akhir

- **Pembersihan Akhir (Dropna):** Sebanyak 60 baris pertama yang mengandung nilai NaN (akibat efek samping dari perhitungan rolling window 60-hari) telah dihapus dengan sukses. Data yang bersih dan siap pakai ini sekarang dimulai secara efektif pada tanggal 31 Maret 2010 dengan nilai metrik yang proporsional.
- **Dimensi Data:** 3.930 baris × 14 kolom (setelah pembersihan dan rekayasa fitur).

## IV. Serah Terima ke Fase 2

Dengan selesainya langkah-langkah di atas, data historis IHSG kini telah sepenuhnya siap untuk digunakan pada Fase 2, yaitu tahap implementasi dan perbandingan algoritma concept drift detectors (baseline standar maupun metrik usulan kita).
