Berikut adalah draf penulisan ulang secara menyeluruh, mendalam, dan terstruktur untuk **Fase 3: Pembangunan Model Prediksi & Pipa Rolling Retraining**. Anda dapat langsung menyalin bagian ini untuk memperbarui berkas panduan perencanaan utama Anda secara manual.

# **V. Detail Rencana Kerja Fase 3: Pembangunan Model Prediksi & Pipa Rolling Retraining**

Fase 3 dirancang untuk membangun sistem simulasi aliran data *real-time* dengan skema *prequential* (*test-then-train*) guna menguji efektivitas pemicuan *retraining* eksplisit (*drift-driven retraining*). Pengujian ini mengonfrontasikan dua model dengan filosofi komputasi kontras: XGBoost sebagai representasi *batch learner* konvensional berkekuatan tinggi, dan OS-ELM sebagai representasi *online learner* adaptif yang hemat sumber daya.

## **A. Arsitektur Global & Regulasi Kedisiplinan Data**

Guna mengunci validitas ilmiah dan memastikan keadilan eksperimen (*ceteris paribus*), pipa pemrosesan (*pipeline*) pada Fase 3 wajib mematuhi batasan struktural berikut:

1. **Definisi Variabel Target ($y$):** Target prediksi dikunci secara mutlak pada nilai Log\_Return hari berikutnya ($t+1$). Pilihan ini selaras dengan langkah pra-pemrosesan Fase 1 untuk menjaga stasioneritas target runtun waktu bursa finansial.  
2. **Matriks Fitur Input ($X$):** Model murni hanya menggunakan 9 fitur multivariat hasil ekstraksi Fase 1: Log\_Return, Vol\_20d, Vol\_60d, EMA\_5, BB\_Middle, BB\_Upper, BB\_Lower, Momentum\_5d, dan Momentum\_20d.  
3. **Masa Pemanasan & Batas Awal Simulasi:** Baris $0$ sampai $240$ dari dataset kronologis bersih dialokasikan murni sebagai data pelatihan awal (*initial warm-up training*). Aturan ini mengunci keseragaman titik start balapan akurasi, mengingat batas pengujian terbesar pada Fase 2 (WASSERSTEIN\_120) membutuhkan penyangga $2W = 240$ baris untuk memicu sinyal pertamanya secara legal. Simulasi harian hulu-hilir akan berjalan serempak dimulai pada baris integer ke-241 hingga baris terakhir (19 Juni 2026).  
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
* **Output yang Harus Anda Laporkan:** 1\. Konfirmasi dimensi akhir dari matriks $X$ dan vektor $y$ setelah pemotongan baris akibat *shifting* target lag.  
  2\. Pembuktian lewat cuplikan data baris awal indeks ke-241 untuk memastikan tidak ada kebocoran data masa depan (*look-ahead bias*).

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

## **📥 Langkah Konfirmasi Sebelum Memulai Pengodean**

Kerangka kerja modular untuk Fase 3 telah dikunci secara rigid, ilmiah, dan terbebas dari asumsi subjektif. Sesuai dengan pakta integritas dan protokol kerja asisten penelitian Anda, **saya meminta konfirmasi Anda: Apakah susunan instruksi modular beserta spesifikasi input-output untuk Fase 3 ini sudah sesuai dengan kebutuhan dokumen perencanaan Anda?**  
Jika Anda sudah memberikan konfirmasi final, silakan berikan instruksi kepada saya untuk membuka pintu eksekusi teknis **Langkah 1 (Rekayasa Target Pasangan Lag & Inisialisasi Matriks Evaluasi)** di lingkungan pengodean Anda\!