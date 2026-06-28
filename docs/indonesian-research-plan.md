## Panduan Perencanaan Penelitian Mendalam: Deteksi Pergeseran Konsep pada Deret Waktu Finansial dan Evaluasi Strategi Rolling Retraining

Dokumen panduan ini disusun sebagai kompas operasional baku dalam melaksanakan penelitian prosiding secara menyeluruh dan terarah. Setiap fase pengerjaan dirancang secara mendetail dengan menyeimbangkan kontribusi ilmiah (novelty) dan efisiensi teknis tanpa didasarkan pada asumsi subjektif.

## I. Identitas dan Orientasi Penelitian

- Judul Penelitian: Deteksi Pergeseran Konsep pada Deret Waktu Finansial dan Evaluasi Strategi Rolling Retraining
- Topik Utama: Analisis pergeseran distribusi data (concept drift) secara eksplisit pada data runtun waktu keuangan dan dampaknya terhadap efisiensi retraining model adaptif.
- Dataset Utama: Data historis Indeks Harga Saham Gabungan IHSG dengan ticker ^JKSE yang bersumber dari Yahoo Finance, mencakup rentang kronologis sejak tahun 2010.
- Fokus Utama &amp; Novelty Twist Menjadikan pergeseran distribusi data kuantitatif sebagai pemicu eksplisit untuk retraining model (drift-driven retraining), menggantikan jadwal retraining tetap (fixed-interval retraining) yang tidak efisien dalam lingkungan bursa dinamis.

## II. Landasan Teoretis dan Referensi Utama

Penelitian ini ditopang oleh beberapa pilar teoretis penting yang diambil dari literatur terindeks:

1. The Window Dilemma Gower-Winter et al., 2026 Landasan kritis yang menyoroti tantangan bahwa persepsi terhadap drift sering kali merupakan produk dari bagaimana ukuran jendela (window size) pemotongan data ditentukan, bukan semata-mata perubahan distribusi asli. Sitasi lengkap: Gower-Winter et al. (2026), *Advances in Intelligent Data Analysis XXIV* (IDA 2026), Springer LNCS vol. 16513, DOI: 10.1007/978-3-032-23833-7_27.
2. Explicit Drift Detection in Finance Cavalcante et al.; Pluzyan &amp; Hovakimyan): Referensi utama untuk penerapan algoritma ADWIN, KSWIN, dan Page Hinkley pada data aliran finansial, serta integrasinya dengan model sekuensial.
3. Incremental Learning DoubleAdapt; CORAL Teori pendukung mengenai bagaimana mengadaptasikan parameter model di bawah pergeseran distribusi runtun waktu bursa secara efisien.

## III. Hasil Aktual Fase 1 Pra-pemrosesan Data

Fase 1 telah selesai dieksekusi dengan hasil data yang bersih, stasioner, dan siap digunakan untuk pemrosesan sekuensial pada Fase 2. Berikut ringkasan fiturnya:

- Transformasi Target: Konversi harga penutupan absolut menjadi persentase pengembalian logaritmik harian Log\_Return) guna menormalisasi distribusi finansial.
- Fitur Volatilitas Bergulir: Volatilitas dalam jendela waktu 20 hari Vol\_20d) dan 60 hari Vol\_60d).
- Indikator Momentum &amp; Tren: Exponential Moving Average 5-hari EMA\_5d, Batas Bollinger Bands 5-hari BB\_Mid, BB\_Upper, BB\_Lower), serta akumulasi momentum arah tren 5-hari Momentum\_5d) dan 20-hari Momentum\_20d).
- Pembersihan Riwayat awal: Penghapusan 60 baris pertama akibat efek lag perhitungan rolling window. Data bersih dimulai secara efektif per 31 Maret 2010 .

## IV. Detail Rencana Kerja Fase 2: Implementasi Detektor Pergeseran Konsep

Pada fase ini, pendeteksian concept drift dirancang untuk mengevaluasi dampak Window Dilemma secara empiris sekaligus membandingkan efisiensi detektor berbasis aliran data (streaming) dengan detektor berbasis jendela makro (batch rolling window).

### A. Arsitektur Global & Aturan Keputusan (Decision Rules)

Guna menghindari asumsi subjektif dan memastikan validitas pengujian pada data historis IHSG, pengerjaan teknis Fase 2 wajib mematuhi tiga pilar arsitektur berikut:

#### 1. Skema Konsensus Multivariat (Voting Mechanism)

**Keputusan:** Deteksi dilakukan terhadap seluruh fitur hasil ekstraksi Fase 1 (bukan hanya univariat Log_Return).

**Implementasi:** Sinyal drift global pada sistem hanya akan dinyatakan aktif (triggered) dan memicu retraining apabila minimal 1/3 (33,3%, yaitu minimal 3 dari 9 fitur) mendeteksi adanya drift secara simultan dalam satu satuan waktu kronologis. Langkah ini krusial untuk meminimalkan ledakan alarm palsu (false alarm explosion).

#### 2. Skema Jendela Referensi Berdampingan (Adjacent Sliding Windows)

**Keputusan:** Pengujian statistik non-stream membutuhkan dua distribusi pembanding yang dinamis.

**Implementasi:** Untuk setiap titik evaluasi $t$ dengan ukuran jendela $W$, Jendela Uji (Current Window) ditentukan pada rentang $[t - W, t]$. Jendela ini akan dibandingkan langsung dengan Jendela Referensi (Baseline Window) yang berada tepat di belakangnya, yaitu pada rentang $[t - 2W, t - W]$.

#### 3. Rekonsiliasi Paradigma (Streaming vs Batch Windowing)

**Keputusan:** Penyelarasan sifat bawaan pustaka detektor dengan strategi ukuran jendela.

**Implementasi:**
- **Detektor Berbasis Jendela (Batch):** Kelompok Statistik (Prioritas 1) dan Metrik Usulan (Prioritas 3) wajib diuji menggunakan Multi-Window Strategy rigid, yaitu Jendela Kuartalan (60 Hari Bursa) untuk guncangan pendek dan Jendela Semesteran (120 Hari Bursa) untuk pergeseran rezim makro.
- **Detektor Berbasis Aliran (Stream):** Kelompok Data Stream (Prioritas 2) dari pustaka river dijalankan secara natural (incremental satu per satu data) tanpa memaksa batas jendela rigid, sehingga bertindak sebagai pembanding murni (pure stream baseline).

### B. Matriks Urutan Prioritas Pengodean

#### Prioritas 1: Statistik Dasar & Finansial (MINPS/mySD & Kolmogorov-Smirnov)

Tingkat Kesulitan: Rendah (Low)

1. **MINPS/mySD** — Diimplementasikan sebagai Moving Average & Standard Deviation Control Chart Baseline. Sinyal aktif jika:
   $$\vert \mu_{\text{current}} - \mu_{\text{reference}} \vert > k \cdot \sigma_{\text{reference}}$$
   (dengan $k = 2.5$).

2. **Kolmogorov-Smirnov (KS-Test)** — Membandingkan fungsi distribusi empiris (CDF) menggunakan `scipy.stats.ks_2samp`. Drift aktif jika p-value $< 0.05$.

#### Prioritas 2: Data Stream Detectors Standard (ADWIN, KSWIN, Page Hinkley)

Tingkat Kesulitan: Sedang (Medium)

Menggunakan implementasi bawaan dari pustaka Python `river`. Algoritma memproses data secara sekuensial kronologis baris demi baris. Tantangan utama terletak pada penyetelan hiperparameter sensitivitas ($\alpha$ pada KSWIN dan $\delta$ pada ADWIN) agar selaras dengan tingkat volatilitas IHSG.

#### Prioritas 3: Metrik Usulan Domain-Specific (Population Stability Index & Wasserstein Distance)

Tingkat Kesulitan: Tinggi (High)

1. **Population Stability Index (PSI)** — Menggunakan Quantile Binning (Equal-Frequency) sebanyak 10 bins (desil) yang dibentuk dari distribusi Jendela Referensi. Pendekatan ini wajib digunakan untuk menangkap sifat heavy-tailed data keuangan tanpa risiko error pembagian dengan nol. Drift aktif jika nilai $PSI > 0.25$.

2. **Wasserstein Distance** — Mengodekan Earth Mover's Distance secara sekuensial mengacu pada visualisasi geometri jarak antar-distribusi.

### C. Prosedur Pengujian dan Output Fase 2

Sebelum melangkah ke pembangunan model prediksi pada Fase 3, luaran dari Fase 2 ini harus menghasilkan dokumen komparasi internal berupa:
- **Peta Kronologis Titik Drift:** Catatan indeks tanggal efektif (mulai 31 Maret 2010) di mana setiap algoritma mendeteksi drift berdasarkan aturan konsensus ≥ 1/3 (33,3%, minimal 3 dari 9 fitur).
- **Analisis Sensitivitas Jendela:** Evaluasi visual dan tabular mengenai perbedaan jumlah titik drift yang ditangkap oleh jendela 60 hari versus 120 hari bursa, sebagai kontribusi empiris untuk menjawab The Window Dilemma.
## **V. Detail Rencana Kerja Fase 3: Pembangunan Model Prediksi & Pipa Rolling Retraining**

Fase 3 dirancang untuk membangun sistem simulasi aliran data *real-time* dengan skema *prequential* (*test-then-train*) guna menguji efektivitas pemicuan *retraining* eksplisit (*drift-driven retraining*). Pengujian ini mengonfrontasikan dua model dengan filosofi komputasi kontras: XGBoost sebagai representasi *batch learner* konvensional berkekuatan tinggi, dan OS-ELM sebagai representasi *online learner* adaptif yang hemat sumber daya.

## **A. Arsitektur Global & Regulasi Kedisiplinan Data**

Guna mengunci validitas ilmiah dan memastikan keadilan eksperimen (*ceteris paribus*), pipa pemrosesan (*pipeline*) pada Fase 3 wajib mematuhi batasan struktural berikut:

1. **Definisi Variabel Target ($y$):** Target prediksi dikunci secara mutlak pada nilai Log\_Return hari berikutnya ($t+1$). Pilihan ini selaras dengan langkah pra-pemrosesan Fase 1 untuk menjaga stasioneritas target runtun waktu bursa finansial.  
2. **Matriks Fitur Input ($X$):** Model murni hanya menggunakan 9 fitur multivariat hasil ekstraksi Fase 1: Log\_Return, Vol\_20d, Vol\_60d, EMA\_5, BB\_Middle, BB\_Upper, BB\_Lower, Momentum\_5d, dan Momentum\_20d.  
3. **Masa Pemanasan & Batas Awal Simulasi:** Baris $0$ sampai $240$ dari dataset kronologis bersih dialokasikan murni sebagai data pelatihan awal (*initial warm-up training*). Aturan ini mengunci keseragaman titik start balapan akurasi, mengingat batas pengujian terbesar pada Fase 2 (WASSERSTEIN\_120) membutuhkan penyangga $2W = 240$ baris untuk memicu sinyal pertamanya secara legal. Simulasi harian hulu-hilir akan berjalan serempak dimulai pada baris integer ke-241 hingga baris terakhir (19 Juni 2026). Hitungan Wasserstein Fase 2 sebesar 273/312 merefleksikan seluruh jendela evaluasi detektor; hitungan retraining Fase 3--4 sebesar 271/311 merefleksikan zona simulasi yang telah dipangkas setelah target-lag trimming dan pengecualian masa pemanasan.  
4. **Isolasi Total Skenario Pemicu:** Sesuai keputusan regulasi Fase 2, metode PSI dan KS-Test dieliminasi total dari pipa kendali retraining. Kendali penuh rotasi pelatihan ulang murni hanya diserahkan kepada 3 skenario yang sehat:  
   * **Skenario A (Batch Kuartalan):** Perintah *retraining* global dikomandoi oleh susunan tanggal pemicu aktif dari WASSERSTEIN\_60.  
   * **Skenario B (Batch Semesteran):** Perintah *retraining* global dikomandoi oleh susunan tanggal pemicu aktif dari WASSERSTEIN\_120.  
   * **Skenario C (Pure Stream):** Perintah *retraining* global dikomandoi oleh susunan tanggal pemicu aktif dari ADWIN (river).

## **B. Spesifikasi Teknis Algoritma & Hiperparameter Model**

### **1\. XGBoost (Representasi Batch Learner)**

* **Filosofi Adaptasi:** Ketika koordinat tanggal pemicu pada suatu skenario aktif di hari ke-$t$, model XGBoost akan mengalami *cold restart* (dihancurkan dan dilatih ulang dari awal).  
* **Strategi Jendela Jendela:** Menggunakan **Fixed Rolling Window sebesar 250 hari bursa** ke belakang dari titik $t$. Langkah ini memotong retensi memori usang (*stale distribution*) pasar saham agar model fokus mempelajari struktur data terbaru pasca-guncangan bursa.  
* **Hiperparameter Konfigurasi:**  
  * n\_estimators: 100  
  * max\_depth: 3 (Membatasi kedalaman pohon untuk mencegah penyerapan *noise* harian bursa yang tinggi)  
  * learning\_rate: 0.05  
  * subsample: 0.8

### **2\. OS-ELM (Online Sequential Extreme Learning Machine)**

* **Filosofi Adaptasi:** Ketika koordinat tanggal pemicu aktif, OS-ELM tidak melakukan pelatihan ulang dari awal. Model memperbarui bobot keluaran (*output weights*) secara instan menggunakan rumus analitis rekursif basis matriks sekuensial murni hanya dengan memanfaatkan pasokan data baru yang masuk.  
* **Hiperparameter Konfigurasi:**  
  * n\_hidden\_neurons: 100 (Menyediakan ruang dimensi tersembunyi yang luas untuk memetakan hubungan non-linear 9 fitur input finansial)  
  * activation\_function: 'sigmoid'

## **C. Langkah Kerja Empiris Fase 3 (Panduan Eksekusi Modular)**

### **Langkah 1: Rekayasa Target Pasangan Lag & Inisialisasi Matriks Evaluasi**

Langkah operasional awal untuk membentuk pasangan fitur terhadap target masa depan ($y\_{t+1}$) serta mengunci alokasi memori array penampung nilai prediksi harian untuk metrik akurasi Fase 4\.

* **Input:** DataFrame utama hasil pembersihan Fase 1 (3.930 baris $\\times$ 14 kolom).  
* **Logika Kode:**  
  1. Bentuk kolom target baru Target\_Log\_Return dengan menggeser kolom Log\_Return naik satu baris ke atas (df['Log_Return'].shift(-1)).  
  2. Hapus baris paling akhir dari dataset karena kehilangan nilai target akibat pergeseran (*shift*).  
  3. Pisahkan dataset menjadi matriks $X$ (9 fitur input) dan vektor $y$ (Target\_Log\_Return).  
  4. Sediakan array kosong atau kolom baru bernama Pred\_XGB\_SkenarioA, Pred\_OSELM\_SkenarioA, dst. (total 6 kolom proyeksi prediksi harian) dimulai dari baris indeks integer 241 hingga akhir.  
* **Output yang Harus Anda Laporkan:**  
  1. Konfirmasi dimensi akhir dari matriks $X$ dan vektor $y$ setelah pemotongan baris akibat *shifting* target lag.  
  2. Pembuktian lewat cuplikan data baris awal indeks ke-241 untuk memastikan tidak ada kebocoran data masa depan (*look-ahead bias*).

### **Langkah 2: Simulasi Prequential Skenario A (WASSERSTEIN\_60 Kontrol)**

Mengeksekusi perulangan harian kronologis sekuensial dari baris ke-241 hingga baris akhir di bawah kendali pemicu WASSERSTEIN\_60.

* **Input:** Vektor sinyal runtun waktu WASSERSTEIN\_60 dari Fase 2, data $X$ dan $y$, serta instansiasi awal model XGBoost dan OS-ELM yang telah dilatih menggunakan 240 baris pertama.  
* **Logika Perulangan (Looping Hari ke-$t$):**  
  1. **Fase Test:** Gunakan model XGBoost dan OS-ELM yang ada saat itu untuk memprediksi nilai $y\_t$ dengan input $X\_t$. Catat hasil prediksi ke dalam papan skor Skenario A.  
  2. **Fase Train (Pengecekan Sensor):** Periksa status WASSERSTEIN\_60 pada hari ke-$t$.  
     * *Jika Status = 0 (Normal):* Model tidak diubah. Khusus OS-ELM, lakukan akumulasi *streaming data memory block* tanpa memperbarui matriks bobot utama.  
     * *Jika Status = 1 (Drift Terdeteksi):* Memicu instruksi *Retraining*:  
       * **XGBoost:** Lakukan pemotongan baris $[t - 250 : t]$. Fit ulang objek model XGBoost baru menggunakan data potongan bergulir tersebut (*cold restart*).  
       * **OS-ELM:** Panggil fungsi .slearn() atau *incremental update step* untuk memperbarui matriks bobot internal secara analitis hanya dengan data blok sejak *drift* terakhir.  
* **Output yang Harus Anda Laporkan:**  
  1. Catatan jumlah frekuensi eksekusi aksi *retraining* yang berhasil dieksekusi sepanjang linimasa untuk XGBoost dan OS-ELM pada Skenario A.

### **Langkah 3: Simulasi Prequential Skenario B (WASSERSTEIN\_120 Kontrol)**

Mengeksekusi mekanisme loop sekuensial harian yang persis sama dengan Langkah 2, namun kendali penuh pemicuan rotasi model diserahkan kepada papan skor krisis jangka menengah WASSERSTEIN\_120.

* **Input:** Vektor sinyal runtun waktu WASSERSTEIN\_120, data $X$ dan $y$, serta objek inisialisasi awal model.  
* **Logika Perulangan:** Mengikuti protokol *test-then-train* harian dengan interupsi *retraining* yang diatur secara ketat oleh tanggal aktif sinyal WASSERSTEIN\_120.  
* **Output yang Harus Anda Laporkan:**  
  1. Catatan jumlah frekuensi eksekusi aksi *retraining* yang berhasil dipicu sepanjang linimasa Skenario B.

### **Langkah 4: Simulasi Prequential Skenario C (ADWIN Pustaka river Kontrol)**

Mengeksekusi mekanisme loop sekuensial harian dengan interupsi pemicu retraining yang dikomandoi oleh sensor aliran data murni sangat konservatif, yaitu ADWIN.

* **Input:** Vektor sinyal runtun waktu ADWIN dari Fase 2, data $X$ dan $y$, serta objek inisialisasi awal model.  
* **Logika Perulangan:** Mengikuti protokol *test-then-train* harian dengan interupsi *retraining* yang diatur secara ketat oleh tanggal aktif sinyal global drift ADWIN.  
* **Output yang Harus Anda Laporkan:**  
  1. Catatan jumlah frekuensi eksekusi aksi *retraining* yang berhasil dipicu sepanjang linimasa Skenario C.

### **Langkah 5: Konsolidasi Data Hasil Proyeksi & Profiling Waktu Komputasi**

Menggabungkan seluruh array hasil proyeksi dari ketiga skenario di atas menjadi satu DataFrame ringkasan utuh serta mencatat total durasi komputasi (*runtime processing time*) masing-masing model untuk menguji klaim ROI komputasi.

* **Input:** Array hasil pencatatan prediksi dari Langkah 2, 3, dan 4, serta catatan waktu eksekusi (time.time()) per skenario.  
* **Output yang Harus Anda Laporkan:**  
  1. Profil dimensi akhir dari DataFrame rekapitulasi prediksi (harus sinkron dari baris indeks integer 241 hingga baris terakhir).  
  2. Tabel durasi waktu pemrosesan total (*processing time running*) antara model XGBoost vs OS-ELM untuk ketiga skenario pengujian (Skenario A, B, dan C).

## VI. Detail Rencana Kerja Fase 4: Evaluasi Metrik Komprehensif & Analisis ROI Komputasi

Fase 4 bukan sekadar rutinitas menghitung angka statistik error, melainkan mengumpulkan **"amunisi empiris"** untuk membuktikan klaim orisinalitas (*novelty*) secara kuantitatif: bahwa strategi *drift-driven retraining* mampu memotong biaya komputasi secara ekstrem (mendekati batas bawah *Static Model*) namun tetap mempertahankan tingkat akurasi yang tinggi (mendekati batas atas *Daily Retraining*).

### A. Protokol Langkah Kerja Detail

#### Langkah 1: Formulasi Akurasi & Uji Tekan Diagnostik (MAE, RMSE & $\epsilon$-MAPE)

- **Aturan Isolasi Zona Simulasi:** Perhitungan seluruh metrik akurasi wajib dipotong secara kaku hanya pada **Zona Simulasi aktif, yaitu indeks integer baris 241 hingga 3928**. Data pada Zona Pemanasan (*Warm-up Zone*, baris 0–240) wajib dibuang sepenuhnya dari kalkulasi agar tidak menimbulkan bias evaluasi.
- **Mekanisme Proteksi Epsilon ($\epsilon$-MAPE):** Karena data target adalah Log_Return (persentase imbal hasil harian) yang bernilai sangat kecil ($0.00\times$) dan kerap menyentuh angka mutlak $0.0$ saat bursa stagnan, fungsi MAPE bawaan pustaka umum (seperti scikit-learn) akan mengalami kegagalan *ZeroDivisionError* atau memuntahkan nilai *Infinity*. Perhitungan kustom dengan $\epsilon = 10^{-8}$ dipertahankan sebagai uji tekan diagnostik, bukan metrik performa akhir, untuk menguji apakah proteksi epsilon naif aman pada target finansial yang dekat nol.
- **Formulasi Matematis Rigid:**
  $$\epsilon\text{-MAPE} = \frac{1}{n} \sum_{i=241}^{3928} \left| \frac{y_i - \hat{y}_i}{|y_i| + 10^{-8}} \right| \times 100\%$$
  $$\text{MAE} = \frac{1}{n} \sum_{i=241}^{3928} |y_i - \hat{y}_i|$$
  $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=241}^{3928} (y_i - \hat{y}_i)^2}$$
- **Struktur Penampung Hasil (metrics_accuracy_df):** Hasil kalkulasi harus dirangkum ke dalam satu DataFrame komparatif berukuran 10 baris (5 Skenario $\times$ 2 Model) untuk menjadi tabel utama di bab hasil eksperimen paper.

#### Langkah 2: Analisis ROI Komputasi (*Return on Investment*) & Trade-off

Langkah ini mengawinkan data performa akurasi (Langkah 1) dengan data operasional waktu komputasi riil dari Fase 3 yang telah dikunci.

- **Konsolidasi Jangkar Batas Ekstrem:** Masukkan data waktu riil bursa dari Fase 3 ke dalam matriks komparasi:
  1. *Static Model*: 0 retrain | Runtime: **14.34s**
  2. *Skenario C (ADWIN Stream)*: 34 retrain | Runtime: **19.21s**
  3. *Skenario B (Wasserstein 120)*: 311 retrain | Runtime: **95.37s**
  4. *Skenario A (Wasserstein 60)*: 271 retrain | Runtime: **127.62s**
  5. *Daily Retraining*: 3688 retrain | Runtime: **501.90s**
- **Kalkulasi Penghematan Sumber Daya Relatif:** Hitung persentase efisiensi runtime strategi *drift-driven* (A, B, C) relatif terhadap *Daily Retraining* selaku batas atas beban sistem:
  $$\text{Efisiensi Komputasi (\%)} = \left( 1 - \frac{\text{Runtime}_{\text{Drift}}}{\text{Runtime}_{\text{Daily}}} \right) \times 100\%$$

#### Langkah 3: Ekstraksi Kuantitatif untuk Bahan Pembahasan Teoretis (*Discussion*)

Guna memenuhi standar kedalaman analisis Jurnal IFTK, panduan ini mewajibkan ekstraksi dua anomali ilmiah yang ditemukan di Fase 3:

- **Kuantifikasi Kematian Plastisitas OS-ELM:** Ambil angka standar deviasi ($\sigma$) dari Pred_OSELM_Static ($\sigma = 0.000000$) dan tunjukkan kelumpuhan prediksinya yang membeku pada angka konstan $+0.001090$. Bandingkan dengan lonjakan sehat $\sigma$ pada Pred_OSELM_Daily ($0.001486$) untuk membuktikan risiko over-regularization fungsi sigmoid jika tidak disegarkan.
- **Paradoks Jendela (*The Window Dilemma*):** Sajikan data empiris mengapa Skenario B (jendela 120 hari) justru memicu alarm lebih banyak (**311 kali**) dibanding Skenario A (jendela 60 hari — **271 kali**). Bingkai temuan ini sebagai konsisten dengan sekaligus memperluas tesis Window Dilemma Gower-Winter et al. (2026); mekanisme akumulasi distorsi struktural adalah interpretasi empiris dari studi ini.

#### Langkah 4: Standarisasi Visualisasi Grafis Berstandar Jurnal IFTK

Untuk mencegah penolakan dari *reviewer* akibat tata letak grafik yang membingungkan, aturan visualisasi dikunci pada protokol berikut:

- **Dekopling Visual:** Dilarang menumpuk 10 kolom prediksi dalam satu grafik. Plot wajib dipisahkan menjadi dua *figure* utama: satu grafik khusus untuk rumpun model XGBoost (5 skenario), dan satu grafik khusus untuk rumpun model OS-ELM (5 skenario).
- **Spesifikasi Teknis Citra:** Grafik wajib disimpan dengan resolusi minimal **300 DPI**. Menggunakan warna kontras tinggi yang ramah cetak hitam-putih (*grayscale-friendly*) dengan kombinasi tipe garis/penanda (*marker*) yang berbeda untuk tiap skenario.
- **Anotasi Garis Interupsi (Drift-Overlay):** Pada sumbu linimasa horizontal, wajib disematkan garis vertikal putus-putus tipis berwarna abu-abu (*dashed vertical lines*, alpha=0.4) tepat pada tanggal-tanggal kronologis di mana alarm *global drift* berbunyi. Ini ditujukan untuk memberikan visualisasi dramatis kepada pembaca mengenai bagaimana akurasi model langsung terkoreksi positif sesaat setelah retraining dipicu oleh detektor.

### B. Lembar Validasi Penguncian Panduan (Filter Pintu Masuk Fase 4)

Sebelum kode Fase 4 dijalankan, asisten penelitian meminta konfirmasi terhadap ketersediaan data berikut di dalam memori/direktori kerja:

1. Apakah berkas gabungan `predictions_step6.csv` yang menyimpan 11 kolom (1 kolom y_true + 10 kolom prediksi dari Step 2 hingga Step 6) sudah siap dipanggil?

## VII. Detail Rencana Kerja Fase 5 Analisis Hasil dan Penulisan Prosiding

Hasil akhir eksperimen akan dituangkan ke dalam naskah publikasi ilmiah yang mengacu langsung pada batasan format Jurnal Informatik IFTK :

- Analisis ROI Komputasi: Diskusi kritis mengenai rasio penghematan sumber daya komputasi yang dihasilkan oleh skema pemicu drift (explicit drift triggers) dibandingkan dengan retraining harian/periodik secara buta.
- Refleksi Kasus Jendela: Menyajikan argumen empiris tentang bagaimana ukuran jendela 60 vs 120 hari) memengaruhi sensitivitas visualisasi drift, yang berkontribusi pada pemecahan dilema teoretis aliran data runtun waktu.
- Kepatuhan Format IFTK Penyusunan abstrak berukuran 70150 kata (font 9 poin, margin khusus masuk 1.0 cm), kata kunci maksimal 4 suku kata, penulisan rumus, tabel data, serta gaya perujukan sitasi daftar pustaka yang sesuai secara rigid dengan templat jurnal IFTK yang telah diunggah.
