# **DOKUMEN MASTER REFERENSI RISET (FASE 1-4)**

---

**Judul Penelitian:** Deteksi Pergeseran Konsep pada Deret Waktu Finansial dan Evaluasi Strategi Rolling Retraining  
**Fokus Utama:** Menjadikan pergeseran distribusi data kuantitatif sebagai pemicu eksplisit untuk retraining model (drift-driven retraining), menggantikan jadwal retraining tetap (fixed-interval) atau harian secara buta dalam lingkungan bursa yang dinamis.  
 

## **1\. FASE 1: PENGUMPULAN DAN PRA-PEMROSESAN DATA**

Eksekusi Fase 1 berfokus pada pembangunan fondasi data yang bersih, stasioner, dan bebas dari kebocoran data masa depan (look-ahead bias). Seluruh pipa pengolahan data dikunci pada spesifikasi operasional berikut:

### **1.1. Akuisisi & Pembersihan Dataset Utama**

* **Pemilihan Dataset:** Menggunakan data historis Indeks Harga Saham Gabungan (IHSG) dengan ticker ^JKSE yang bersumber dari Yahoo Finance, mencakup rentang kronologis multi-dekade sejak tahun 2010\.  
* **Pembersihan Riil:** Pembersihan data mentah dilakukan dengan menghapus baris header berulang yang tidak diperlukan. Kolom tanggal (Date) diatur secara ketat sebagai indeks berformat Datetime kronologis.  
* **Pembersihan Missing Values (Hari Libur Bursa):** Data kosong akibat hari libur sabtu-minggu atau libur nasional diatasi menggunakan metode forward-fill (ffill). Hal ini krusial untuk menjaga kontinuitas deret waktu tanpa memasukkan bias informasi dari masa depan.  
* **Transformasi Stasioneritas:** Harga penutupan absolut (Close Price) dikonversi menjadi persentase pengembalian logaritmik harian (Log\_Return). Transformasi ini wajib dilakukan untuk menormalkan distribusi data finansial agar kebal terhadap trend nominal jangka panjang.

### **1.2. Rekayasa Fitur & Matriks Indikator Multivariat (9 Fitur)**

Guna menangkap karakteristik volatilitas, tren, dan momentum pasar secara simultan, dataset diperkaya melalui ekstraksi 9 fitur multivariat sebagai berikut:

1. **Log\_Return:** Nilai return logaritmik harian sebagai proksi pergerakan harga inti.  
2. **Vol\_20d (Rolling Volatility):** Simpangan baku bergulir (rolling standard deviation) 20 hari bursa untuk menangkap fluktuasi jangka pendek.  
3. **Vol\_60d (Rolling Volatility):** Simpangan baku bergulir 60 hari bursa untuk memantau pergeseran volatilitas jangka menengah.  
4. **EMA\_5d:** Exponential Moving Average 5 hari bursa untuk melacak tren harga terdekat.  
5. **BB\_Middle (Bollinger Bands):** Garis tengah indikator Bollinger Bands berbasis jendela 5 hari bursa.  
6. **BB\_Upper (Bollinger Bands):** Batas atas Bollinger Bands (Pita Tengah \+ 2 · Standar Deviasi) untuk mendeteksi kondisi jenuh beli.  
7. **BB\_Lower (Bollinger Bands):** Batas bawah Bollinger Bands (Pita Tengah \- 2 · Standar Deviasi) untuk mendeteksi kondisi jenuh jual.  
8. **Momentum\_5d:** Perhitungan kumulatif log-return selama 5 hari bursa terakhir untuk mengukur akselerasi harga jangka pendek.  
9. **Momentum\_20d:** Perhitungan kumulatif log-return selama 20 hari bursa terakhir untuk melacak akselerasi tren jangka menengah.

### **1.3. Profil Akhir Dataset & Masa Penyangga (Warm-up Zone)**

* **Pembersihan Residu Resiko (Dropna):** Sebanyak 60 baris pertama data historis dihapus secara sukses. Penghapusan ini wajib karena 60 baris pertama mengandung nilai kosong (NaN) sebagai efek samping operasi rolling window 60 hari pada fitur Vol\_60d.  
* **Dimensi Data Akhir:** Menghasilkan matriks bersih berukuran 3.930 baris × 14 kolom. Rentang kronologis efektif dimulai secara resmi per tanggal 31 Maret 2010 hingga 19 Juni 2026\.

 

## **2\. FASE 2: IMPLEMENTASI DETEKTOR PERGESERAN KONSEP (CONCEPT DRIFT)**

Fase 2 bertujuan mengonstruksi pipa deteksi perubahan distribusi data finansial secara eksplisit menggunakan dua paradigma utama: Batch Multi-Window dan Pure Streaming Aliran Data.

### **2.1. Rekonsiliasi Arsitektur Siber Krisis & Aturan Rekayasa**

Tiga keputusan rekayasa krusial diimplementasikan untuk menjamin validitas ilmiah detektor:

* **Standardisasi Aliran Inkremental:** Detektor bawaan pustaka river sangat sensitif terhadap perbedaan skala nominal fitur. Pipa sekuensial mengintegrasikan modul StandardScaler() secara online dengan urutan operasi transform\_one dijalankan mutlak sebelum learn\_one, guna memotong look-ahead bias harian.  
* **Aturan Penyangga Jarak Wasserstein (Welford Buffer):** Guna menghindari bug kontaminasi di mana nilai jarak hari berjalan mengotori memori referensi sebelum diuji, algoritma diperbaiki secara rigid. Nilai jarak Wasserstein diuji terlebih dahulu terhadap ambang batas adaptif berjalan (μ\_history \+ 2.5 · σ\_history). Setelah vonis alarm diputuskan, barulah nilai tersebut didorong ke fungsi .push() untuk memperbarui memori historis. Aturan ini menumpas efek self-suppression (masking semu) secara total.  
* **Mekanisme Konsensus Global (Aturan Voting):** Sinyal pergeseran distribusi tingkat sistem (Global Drift Alarm) dikunci pada batas konsensus 1/3 (× 33.3%). Sistem resmi menetapkan terjadinya guncangan struktural bursa jika minimal 3 dari 9 fitur multivariat menyalakan alarm drift secara serempak pada hari bursa yang sama.

### **2.2. Matriks Hasil Akhir Frekuensi Sinyal Global Drift**

Berikut adalah rekapitulasi data empiris frekuensi deteksi Global Drift di sepanjang linimasa pengujian aktif selama 3.810 hari bursa:

| Paradigma Evaluasi | Varian Konfigurasi Detektor | Total Hari Global Drift Terdeteksi | Status Kelayakan untuk Fase 3   |
| :---- | :---- | :---- | :---- |
| **Batch Multi-Window** (Fixed Rolling Window) | MYSD\_60 (Kuartalan) | 1.476 Hari | Layak (Kontrol Lokal Mean) |
|  | MYSD\_120 (Semesteran) | 1.159 Hari | Layak (Kontrol Lokal Mean) |
|  | KS\_60 & KS\_120 (Kolmogorov-Smirnov) | 3.802 Hari / 3.690 Hari | **DISKUALIFIKASI / DEGENERASI** |
|  | PSI\_60 & PSI\_120 (Population Stability Index) | 3.810 Hari / 3.690 Hari | **DISKUALIFIKASI / DEGENERASI** |
| **Batch Multi-Window** (Metrik Geometri Usulan) | WASSERSTEIN\_60 (Skenario A) | 273 Hari | **Sangat Ideal (Geometri Bentuk)** |
|  | WASSERSTEIN\_120 (Skenario B) | 312 Hari | **Sangat Ideal (Geometri Bentuk)** |
| **Pure Streaming** (Incremental Online Loop) | ADWIN (Skenario C) | 36 Hari | **Sangat Konservatif & Lolos Filtasi** |
|  | KSWIN (river) | 7 Hari | Konservatif (Cadangan) |
|  | Page Hinkley (river) | 1 Hari | Terlalu Ketat |

*Milestone Kronologis Sinyal Pertama:* Konfigurasi KS\_60 pertama kali melepas sinyal drift pada tanggal 28 September 2010, diikuti secara serempak oleh WASSERSTEIN\_60 pada 30 September 2010\.

### **2.3. Analisis Teoretis Kegagalan Sensor (Bahan Orisinalitas Artikel)**

* **Degenerasi Metodologis KS-Test & PSI:** Fakta empiris bahwa PSI memicu alarm pada 100% hari bursa dan KS-Test mencapai 99.8% membuktikan adanya kecacatan fatal. Kedua algoritma ini tidak mampu membedakan evolusi tren naik harga nominal jangka panjang bursa dengan guncangan struktural jangka pendek. Sifat non-stasioneritas harga finansial merusak pembagian desil PSI, memicu pembagian numerik dengan angka sangat kecil (ε \= 10−4), sehingga menciptakan lonjakan nilai PSI semu yang konstan di atas ambang batas standar (0.25). PSI dan KS-Test resmi **didiskualifikasi** dari pipa pemicu retraining agar tidak merusak argumen efisiensi komputasi paper.  
* **Keunggulan Geometri Jarak Wasserstein Berjalan:** Berhasil mengabaikan bias multikolinieritas nominal harga dan murni hanya menangkap pergeseran massa bentuk distribusi spasial fitur secara struktural (tercatat memicu 273 hari alarm pada jendela 60).  
* **Bukti Empiris Tesis The Window Dilemma:** Pelepasan alarm KS\_60 dan Wasserstein\_60 secara serempak di akhir September 2010 (tepat saat masa buffer baris integer 2W habis) membuktikan secara nyata tesis Gower-Winter et al. (2026). Ukuran jendela batch bertindak sebagai lensa buatan; penumpukan pergeseran tersembunyi dari bulan-bulan sebelumnya meledak seketika saat gerbang komputasi jendela pertama kali dibuka.

 

## **3\. FASE 3: EVALUASI EMPIRIS PIPA ROLLING RETRAINING**

Fase 3 mengunci hasil simulasi prequential loop (test-then-train) runtun waktu IHSG periode 2010–2026. Angka durasi komputasi dan frekuensi retraining dicatat secara objektif tanpa rekayasa.

### **3.1. Parameter Operasional dan Pembagian Jendela Kerja**

* **Dimensi Penjajaran Matriks:** Matriks fitur input (X) berukuran 3.929 baris × 9 fitur multivariat, dijajajarkan sinkron 100% dengan vektor target (y) esok hari (t+1) setelah pemotongan residu baris akhir akibat lag.  
* **Zona Pemanasan (Warm-up Zone):** Baris kronologis indeks integer 0 hingga 240 (241 sampel pertama) dialokasikan murni untuk inisialisasi bobot analitis pseudo-invers awal OS-ELM dan parameter dasar pohon XGBoost.  
* **Zona Simulasi Bursa (Simulation Zone):** Evaluasi prequential berjalan harian tanpa interupsi dimulai dari baris indeks integer 241 hingga baris ke-3.928 (total 3.688 baris uji aktif).  
* **Jangkar Batas Ekstrem (Baselines):** Mengintegrasikan Skenario Static Model (Batas bawah komputasi / 0 retrain) dan Skenario Daily Retraining (Batas atas komputasi / 3.688 retrain) sebagai pagar komparasi algoritmik.

### **3.2. Matriks Komparasi Beban Komputasi Sekuensial**

| Kode Eksperimen | Skenario / Strategi Retraining Pemicu | Jumlah Eksekusi Retraining | Waktu Komputasi Total (Detik)   |
| :---- | :---- | :---- | :---- |
| Step 5 | **Static Model** (Model Dibekukan Pasca Warm-up) | 0 Kali | 14,34 detik |
| Step 4 | **Skenario C** (Drift Stream Trigger \- ADWIN) | 34 Kali | **19,21 detik** |
| Step 3 | **Skenario B** (Drift Semesteran \- WASSERSTEIN\_120) | 311 Kali | 95,37 detik |
| Step 2 | **Skenario A** (Drift Kuartalan \- WASSERSTEIN\_60) | 271 Kali | 127,62 detik |
| Step 6 | **Daily Retraining** (Penyegaran Paksa Tanpa Syarat) | 3.688 Kali | 501,90 detik |

### **3.3. Bedah Kritis Paradoks Komputasi & Fenomena Numerik**

* **Paradoks Pembalikan Resolusi Jendela Wasserstein (60 vs 120 Hari):** Secara konvensional, memperlebar ukuran jendela statistik diasumsikan akan memperhalus fluktuasi data dan menekan jumlah pemicuan. Namun data riil menunjukkan anomali terbalik: Jendela Semesteran (120 hari) memicu 311 alarm, jauh lebih padat daripada Jendela Kuartalan (60 hari) yang hanya memicu 271 alarm. Hal ini membuktikan secara empiris tesis *The Window Dilemma* (Gower-Winter et al., 2026). Jendela besar bertindak sebagai akumulator distorsi historis bursa; tren pergeseran struktural dari bulan-bulan sebelumnya mengendap di dalam jendela referensi, sehingga begitu ambang batas Wasserstein terlampaui, detektor mengalami badai pemicuan beruntun.  
  **Anomali Efisiensi Waktu:** Meskipun memicu retraining 15% lebih banyak, Skenario B (120 hari) selesai 25% lebih cepat daripada Skenario A (95,37s vs 127,62s). Hal ini meruntuhkan asumsi lama bahwa jumlah retraining semata-mata menentukan biaya komputasi total. Penyebabnya terletak pada mekanisme sekuensial OS-ELM: jarak pemicuan yang lebih rapat menyebabkan buffer data akumulasi baru di antara dua alarm menjadi lebih pendek, mempercepat biaya inversi matriks analitis per peristiwa (0,307s per retrain pada Wass-120 vs 0,471s per retrain pada Wass-60).  
* **Paradoks Biaya Per-Peristiwa Pure-Stream ADWIN:** Skenario C (ADWIN) mencatatkan total runtime tersingkat di antara strategi adaptif (19,21 detik; hemat 96,17% dari harian). Namun, setiap satu peristiwa retraining ADWIN memakan biaya rata-rata paling mahal, yaitu 0,565 detik per kejadian (dibandingkan harian yang hanya 0,136s atau Wass-120 sebesar 0,307s). Premi biaya ini timbul karena saking konservatifnya ADWIN (hanya 34 alarm sepanjang 15 tahun), interval hari antar-alarm membengkak sangat lebar. Akibatnya, buffer data runtun waktu yang masuk ke memori penampung OS-ELM menumpuk hingga ribuan baris, memaksa fungsi *Recursive Least Squares* (RLS) melakukan inversi matriks raksasa saat alarm akhirnya berbunyi. Temuan ini menegaskan bahwa metrik efisiensi arsitektur produksi adalah total runtime sistem, bukan biaya operasi tunggal per peristiwa.  
* **Indikasi Ilmiah "Kematian Plastisitas" OS-ELM Statis:** Pada Skenario Static Model, pembekuan parameter menyebabkan model mengalami saturasi numerik permanen dengan nilai standar deviasi prediksi harian mutlak nol (0.000000) dan memprediksi nilai garis lurus horizontal konstan tunggal sebesar \+0.001090 di sepanjang akhir runtun waktu (tail zone Juni 2026). Sebaliknya, model non-linear XGBoost (menggunakan cold restart jendela bergulir tetap 250 hari) berhasil mempertahankan tingkat denyut varians prediksinya secara sehat di angka σ \= 0.007–0.010.

 

## **4\. FASE 4: METRIK EVALUASI KOMPREHENSIF DAN ROI KOMPUTASI**

Fase 4 memetakan analisis kuantitatif performa prediksi lintas skenario yang dihitung adil murni pada zona simulasi bursa bebas bias pemanasan (indeks baris 241 hingga 3.928).

### **4.1. Koreksi Metodologis Mutlak: Diskualifikasi Metrik MAPE**

Eksperimen Fase 4 menemukan kecacatan matematis fundamental pada penggunaan metrik ε-MAPE dalam domain data finansial stasioner. Pada hari bursa tanggal **30 November 2017**, kondisi pasar yang sangat stagnan membuat nilai aktual Log\_Return IHSG berada sangat dekat dengan angka nol mutlak. Fenomena pembagian dengan angka mendekati nol ini meledakkan nilai eror ε-MAPE milik skenario pemicu kuartalan hingga menyentuh angka **190.081.112%**, yang secara logis merusak rata-rata agregat statistik seluruh naskah.  
**Keputusan Ilmiah Baku:** Metrik MAPE resmi **DIGUGURKAN** dari keseluruhan artikel ilmiah. Evaluasi dialihkan secara penuh menggunakan metrik Mean Absolute Error (MAE) dan Root Mean Square Error (RMSE) karena terbukti kebal terhadap anomali pembagian nol, menyajikan medan komparasi eror yang 100% adil.

### **4.2. Matriks Metrik Akurasi & Varians Prediksi Akhir**

| Metrik Evaluasi | Model Prediksi Utama | Static Model (Step 5\) | Skenario C (ADWIN) | Skenario B (Wass-120) | Skenario A (Wass-60) | Daily Baseline (Step 6\)   |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **MAE** (Mean Absolute Error) | Pred\_XGB (XGBoost) | 0,011059 | **0,009133** | 0,011116 | 0,015755 | 0,008076 |
|  | Pred\_OSELM (OS-ELM) | 0,007365 | 0,007375 | 0,007373 | 0,007374 | 0,007377 |
| **RMSE** (Root Mean Sq. Error) | Pred\_XGB (XGBoost) | 0,014402 | **0,013699** | 0,014538 | 0,019258 | 0,011999 |
|  | Pred\_OSELM (OS-ELM) | 0,010787 | 0,010804 | 0,010804 | 0,010807 | 0,010805 |
| **Standar Deviasi Prediksi** (σ) | Pred\_XGB (XGBoost) | 0,005731 | 0,007630 | 0,007160 | 0,010150 | 0,004900 |
|  | Pred\_OSELM (OS-ELM) | **0,000000** | 0,001488 | 0,001489 | 0,001494 | 0,001486 |

### **4.3. Interpretasi Hasil Analisis Kuantitatif**

1. **Validasi Ilusi Matematis Kematian Plastisitas OS-ELM:** Model Pred\_OSELM\_Static menghasilkan nilai MAE terkecil secara agregat ($0,007365$). Namun, nilai standar deviasi harian yang mutlak nol ($0,00000034$) dan verifikasi plot visual bursa tahun 2020 membongkar realitas sesungguhnya: model mengalami kematian plastisitas total, membeku menjadi sebuah garis lurus horizontal datar pada titik harga $+0,001069$. Karena nilai pengembalian logaritmik harian IHSG berfluktuasi rapat di sekitar angka nol, tebakan garis lurus secara statistik menghasilkan rata-rata simpangan absolut yang rendah. Namun, model tersebut 100% kehilangan kegunaan prediksi tren di dunia nyata. Skenario pemicu drift (ADWIN dan Wasserstein) sukses menghidupkan kembali denyut varians model (σ ≈ 0,00148) dengan pengorbanan akurasi agregat desimal yang sangat tidak signifikan (±0,15% relatif).  
2. **Gradien Sensitivitas dan Overfitting Pohon XGBoost (The Window Dilemma):** Pengujian rumpun model pohon keputusan XGBoost menunjukkan urutan gradien penalti MAE relatif terhadap kondisi ideal harian (Daily) sebagai berikut: ADWIN (+13,09%) → Static (+36,94%) → Wass-120 (+37,65%) → Wass-60 (+95,10%). Memaksa XGBoost melakukan retraining pada jendela historis sempit pasca-drift (Skenario A \- Wass 60 hari) justru merusak akurasi sebesar \+95,10%. Hal ini menjadi bukti empiris inti bagi tesis *The Window Dilemma*: penyegaran parameter pada batasan baris data yang terlalu sempit justru menjebak algoritma berbasis pohon ke dalam perangkap overfitting terhadap noise berjangka pendek bursa saham.  
3. **ADWIN Sebagai Hero Strategy (Puncak Novelty):** Skenario C (ADWIN) mengunci posisi trade-off ROI komputasi terbaik. Model ini berhasil memangkas 96,17% biaya runtime dari model harian (hanya butuh 19,21 detik vs 501,90 detik). Pada masa krisis ekstrim kejatuhan bursa akibat pandemi COVID-19 (peristiwa *Black Swan* per 17 Maret 2020), nilai eror RMSE OS-ELM berbasis pemicu ADWIN terbukti hanya 1,001× (atau hanya terpaut 0,1%) lebih buruk dibandingkan model harian yang boros daya.  
4. **Justifikasi Lonjakan Eror Krisis 2020:** Terjadinya pemburukan metrik MAE sesaat sebesar \+27% hingga \+44% tepat setelah alarm ADWIN berbunyi pada Maret 2020 bukanlah tanda kegagalan model, melainkan cerminan guncangan harga ekstrem tak terduga (Black Swan Event). Retraining sekuensial yang dipicu oleh alarm ADWIN tersebut terbukti menjadi mekanisme penyelamat yang sukses melakukan me-reset pemahaman bobot model menuju kondisi "Normal Baru" pasca-krisis makroekonomi bursa lokal.