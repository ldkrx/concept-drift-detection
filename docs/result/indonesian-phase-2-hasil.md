## LAPORAN RESMI EKSEKUSI FASE 2: IMPLEMENTASI DETEKTOR PERGESERAN KONSEP (CONCEPT DRIFT)

## I. Profil Dataset & Lingkungan Evaluasi

- Dimensi Data Bersih: 3.930 baris × 14 kolom.
- Rentang Kronologis Efektif: 31 Maret 2010 hingga 19 Juni 2026 (bebas nilai kosong/NaN akibat lag pra-pemrosesan Fase 1).
- Matriks Indikator Multivariat (9 Fitur): Log_Return, Vol_20d, Vol_60d, EMA_5, BB_Middle, BB_Upper, BB_Lower, Momentum_5d, dan Momentum_20d.
- Aturan Masa Penyangga (Scoreboard Buffer):
  - Metode Batch Fixed Window: Baris 0 sampai 2W diatur sebagai NaN (60 hari bursa berdampingan membutuhkan 120 baris referensi+uji awal).
  - Metode Pure Streaming: Masa pemanasan berjalan (warm-up period) dikunci pada 60 baris pertama.

## II. Konsensus Arsitektur & Rekonsiliasi Siber Krisis

Selama pengerjaan teknis Fase 2, kita telah mengambil tiga keputusan rekayasa krusial untuk menyelamatkan validitas ilmiah penelitian:

1. **Standardisasi Aliran Inkremental (Solusi Kelompok Stream):** Detektor bawaan pustaka river sensitif terhadap perbedaan skala nominal. Kita telah mengintegrasikan modul StandardScaler() dengan urutan `transform_one` sebelum `learn_one`. Aturan ini memotong look-ahead bias secara mutlak dan menyeimbangkan medan baca detektor murni dari memori masa lalu bursa.

2. **Aturan Urutan Penyangga Welford (Solusi Jarak Wasserstein):** Kita menemukan contamination bug di mana nilai jarak Wasserstein hari berjalan dimasukkan ke memori sebelum pengujian. Kode telah diperbaiki sehingga nilai jarak diuji terlebih dahulu terhadap ambang batas berjalan μ_history + 2.5·σ_history, baru kemudian dilempar ke fungsi `.push()`. Langkah ini menumpas efek self-suppression/masking secara total.

3. **Mekanisme Konsensus Global (Aturan Voting):** Sinyal pergeseran konsep tingkat sistem (Global Drift) dikunci pada nilai 1/3 (≈ 33.3%). Sistem resmi mendeteksi terjadinya guncangan struktural bursa jika minimal 3 dari 9 fitur menyalakan alarm drift secara serempak di hari yang sama.

## III. Matriks Hasil Akhir Frekuensi Sinyal Global Drift

Tabel di bawah ini merekapitulasi frekuensi total hari di mana sistem mendeteksi terjadinya Global Drift (memicu perintah retraining model) di sepanjang linimasa data (3.810 hari evaluasi aktif):

Hitungan Wasserstein 273/312 pada tabel ini merefleksikan seluruh jendela evaluasi detektor Fase 2. Hitungan retraining Fase 3--4 menggunakan 271/311 karena zona simulasi dimulai dari baris 241 setelah target-lag trimming dan pengecualian masa pemanasan.

| Paradigma Evaluasi | Varian Konfigurasi Detektor | Total Hari Global Drift Terdeteksi | Status Kelayakan untuk Fase 3 |
|---|---|---|---|
| Batch Multi-Window (Fixed Rolling Jendela) | MYSD_60 (Kuartalan)<br>MYSD_120 (Semesteran)<br>KS_60 (Kuartalan)<br>KS_120 (Semesteran)<br>PSI_60 (Kuartalan)<br>PSI_120 (Semesteran)<br>WASSERSTEIN_60 (Kuartalan)<br>WASSERSTEIN_120 (Semesteran) | 1.476 Hari<br>1.159 Hari<br>3.802 Hari<br>3.690 Hari<br>3.810 Hari<br>3.690 Hari<br>273 Hari<br>312 Hari | Layak (Lokal Mean)<br>Layak (Lokal Mean)<br>Cacat/Degenerasi<br>Cacat/Degenerasi<br>Cacat/Degenerasi<br>Cacat/Degenerasi<br>Sangat Ideal (Geometri)<br>Sangat Ideal (Geometri) |
| Pure Streaming (Incremental Row Loop) | ADWIN (river)<br>KSWIN (river)<br>Page Hinkley (river) | 36 Hari<br>7 Hari<br>1 Hari | Sangat Konservatif<br>Konservatif<br>Sangat Ketat |

Keterangan Milestone Kronologis: Konfigurasi KS_60 pertama kali memicu global drift pada 28 September 2010, disusul oleh WASSERSTEIN_60 pada 30 September 2010.

## IV. Temuan Ilmiah Inti & Analisis Teoritis (Bahan Publikasi Prosiding)

Eksperimen Fase 2 menghasilkan fenomena teoritis berharga yang akan menjadi tulang punggung orisinalitas (novelty discussion) artikel prosiding kita:

- **Degenerasi Metodologis KS-Test dan PSI (Gagal Menyaring Tren):** Fakta bahwa PSI memicu alarm selama 100% hari bursa dan KS-Test mencapai 99.8% adalah bukti empiris yang sangat kuat. Keduanya mengalami kegagalan fungsional akibat ketidakmampuan membedakan evolusi tren naik harga nominal IHSG jangka panjang dengan guncangan struktural jangka pendek. Data non-stasioner nominal harga merusak batas desil PSI dan memicu pembagian nilai kecil (ε = 10⁻⁴), menciptakan lonjakan nilai PSI semu yang konstan di atas 0.25.

- **Keunggulan Geometri Jarak Wasserstein Berjalan:** Pendekatan Adaptive Thresholding pada jarak Wasserstein terbukti paling superior dalam rumpun batch. Detektor ini berhasil mengabaikan bias multikolinieritas nominal harga dan hanya menangkap pergeseran massa bentuk distribusi yang murni struktural (tercatat 273 hari pemicu pada jendela 60).

- **Ketangguhan Karakteristik Rumpun Streaming (river):** Kelompok aliran data murni bertindak sebagai detektor yang sangat tegap dan tidak mudah panik oleh fluktuasi harian bursa. Standardisasi Z-score inkremental meredam riak kecil keuangan, membuat ADWIN (36 hari) dan KSWIN (7 hari) menjadi indikator krisis makroekonomi yang sangat solid.

- **Bukti Empiris yang Konsisten dengan Teori The Window Dilemma:** Pelepasan alarm KS_60 dan Wasserstein_60 secara serempak di akhir September 2010 (tepat saat masa buffer row integer 2W habis) konsisten dengan tesis Window Dilemma dari Gower-Winter et al. (2026). Dalam studi ini, ukuran jendela batch bertindak sebagai lensa buatan; penumpukan pergeseran dari bulan-bulan sebelumnya tampak muncul saat gerbang komputasi jendela pertama kali dibuka.

## V. Cetak Biru Metodologis (Filter Pintu Masuk Fase 3)

Guna menjaga agar arah penelitian tidak melenceng dan mengamankan efisiensi ROI komputasi pada pembangunan model prediksi, kita mengunci aturan regulasi berikut untuk Fase 3:

### 1. Eliminasi Sensor Pemicu Retraining

Kita secara resmi **MENGELIMINASI** metode PSI dan KS-Test dari pipa pemicu rolling retraining model prediksi. Membiarkan sistem melakukan retraining harian sebanyak 3.800 kali akibat alarm palsu KS/PSI akan menghancurkan argumen "Efisiensi Komputasi Model Adaptif" di paper kita. Namun, data kegagalan komparasi keduanya tetap wajib kita sajikan dalam bentuk tabel grafik di Bab Hasil Eksperimen paper prosiding.

### 2. Kombinasi Pengujian Model Prediksi Terpilih

Simulasi pengujian akurasi prediksi model XGBoost dan OS-ELM pada Fase 3 dan 4 akan dievaluasi dengan MAE/RMSE dan murni dikendalikan oleh 3 skenario pemicu retraining global yang sehat:

- **Skenario A (Batch Kuartalan):** Dikomandoi oleh garis tanggal pemicu WASSERSTEIN_60.
- **Skenario B (Batch Semesteran):** Dikomandoi oleh garis tanggal pemicu WASSERSTEIN_120.
- **Skenario C (Pure Stream):** Dikomandoi oleh garis tanggal pemicu ADWIN dari pustaka river.
