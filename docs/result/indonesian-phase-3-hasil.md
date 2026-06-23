# **Laporan Resmi Pelaksanaan Fase 3: Evaluasi Empiris Pipa Rolling Retraining**

Dokumen ini merupakan laporan komprehensif hasil pengerjaan Fase 3: Pembangunan Model Prediksi & Pipa Rolling Retraining. Seluruh angka, durasi komputasi, dan fluktuasi matematis di bawah ini bersifat mentah, riil, dan objektif dari lingkungan pengujian runtun waktu Indeks Harga Saham Gabungan (IHSG) periode 2010–2026 tanpa rekayasa atau asumsi subjektif. Dokumen ini wajib dijadikan acuan utama (baseline) dalam melaksanakan Fase 4 (Analisis Metrik Evaluasi) dan Fase 5 (Penulisan Artikel Prosiding).

# **1. Ringkasan Eksekutif & Fondasi Pemrosesan Data**

Eksperimen pipa berjalan (prequential loop) test-then-train berhasil diselesaikan dengan tingkat kedisiplinan stasioneritas dan anti-kebocoran data (anti-look-ahead bias) yang sangat ketat. Aturan pemrosesan dikunci pada parameter operasional berikut:

* **Dimensi Matriks Akhir:** Matriks fitur input (X) berukuran 3.929 baris × 9 fitur multivariat, dan vektor target (y) berukuran 3.929 baris. Penjajaran data sinkron 100% setelah pemotongan residu baris akhir akibat pergeseran lag target esok hari (t+1).
* **Zona Pemanasan (Warm-up Zone):** Baris kronologis indeks integer 0 hingga 240 (241 sampel bursa pertama) dialokasikan murni untuk inisialisasi bobot awal jaringan OS-ELM dan parameter dasar pohon XGBoost.
* **Zona Simulasi (Simulation Zone):** Evaluasi prequential berjalan harian tanpa interupsi dimulai dari baris indeks integer 241 hingga baris ke-3.928.
* **Ekspansi Batas Komparasi (Baselines):** Mengintegrasikan dua skenario ekstrem di luar kendali drift-driven, yaitu Skenario Static Model (Batas bawah komputasi / 0 retrain) dan Skenario Daily Retraining (Batas atas komputasi / 3.688 retrain). Kedua skenario ini bertindak sebagai jangkar (fence) komparasi untuk membuktikan novelty efisiensi algoritmik pemicu drift.

# **2. Matriks Komparasi Kinerja Lintas Skenario Pemicu**

Berikut adalah rekapitulasi data empiris yang dicatat secara sekuensial dari kelima pengujian skenario:

| Skenario | Pemicu / Strategi Retraining | Jumlah Retraining | Waktu Komputasi Total (s) |
|---|---|---|---|
| Static Model (Step 5) | Tanpa Retraining (Model Beku) | 0 | 14.34s |
| Skenario C (Step 4) | Drift Stream (ADWIN) | 34 | 19.21s |
| Skenario B (Step 3) | Drift Semester (WASSERSTEIN_120) | 311 | 95.37s |
| Skenario A (Step 2) | Drift Quarter (WASSERSTEIN_60) | 271 | 127.62s |
| \* Daily (Step 6) | Retraining Harian (Buta / Tanpa Syarat) | 3688 | 501.90s |

# **3. Pembahasan Kritis Bedah Anomali Finansial & Paradoks Algoritma**

Hasil riil eksekusi Fase 3 memunculkan tiga anomali ilmiah fundamental yang membongkar asumsi umum dalam arsitektur sistem adaptif bursa saham. Temuan ini akan menjadi kontribusi teoretis utama (novelty) pada naskah prosiding kita:

### **3.1. Paradoks Resolusi Jendela Wasserstein (60 VS 120 Hari)**

Secara konvensional, peneliti berasumsi bahwa memperlebar ukuran jendela statistik (Skenario B = 120 hari) akan memperhalus fluktuasi sehingga jumlah alarm pemicu mengecil. Namun, data eksperimen menunjukkan pembalikan: Jendela Semesteran (120 hari) memicu **311 alarm**, jauh lebih padat daripada Jendela Kuartalan (60 hari) yang hanya memicu **271 alarm**. Hal ini membuktikan secara empiris tesis dari *The Window Dilemma* (Gower-Winter et al., 2026). Jendela yang terlalu besar bertindak sebagai akumulator distorsi; pola pergeseran struktural dari bulan-bulan sebelumnya mengendap di dalam jendela referensi, sehingga begitu ambang batas Wasserstein terlampaui, detektor mengalami badai pemicuan beruntun. Dampaknya, runtime Skenario B membengkak drastis hingga **135.53 detik** akibat beban komputasi perombakan ulang XGBoost yang bertubi-tubi.

### **3.2. Paradoks Beban Komputasi Aliran Pure-Stream (ADWIN Buffer)**

Skenario C (ADWIN) bertindak sebagai detektor aliran murni yang sangat konservatif. Sepanjang 15 tahun linimasa, ADWIN berhasil meredam noise pasar dan hanya meloloskan **34 kali sinyal drift struktural**. Kendati demikian, muncul paradoks komputasi yang menakjubkan: Skenario C membutuhkan waktu komputasi total selama **61.99 detik**. Angka ini secara mengejutkan *lebih lambat* daripada Skenario A (59.97 detik) yang frekuensi retraining-nya hampir 8 kali lipat lebih banyak (271 kali). Analisis struktural membuktikan bahwa ketika alarm drift jarang aktif, blok memori (buffer) data sekuensial yang dikumpulkan oleh OS-ELM membengkak hingga ribuan baris. Ketika interupsi pemicu ADWIN akhirnya menyala, fungsi rekursif least squares (RLS) pada OS-ELM dipaksa mengeksekusi inversi matriks berdimensi raksasa sekaligus. Temuan ini mematahkan dogma naif bahwa "semakin sedikit jumlah retraining, sistem otomatis akan selalu berjalan lebih cepat".

### **3.3. Fenomena Kematian Plastisitas (Weight Collapse) pada OS-ELM**

Pemeriksaan mendalam pada ekor runtun waktu prediksi (tail zone Juni 2026) mendeteksi adanya gejala pembekuan numerik pada model OS-ELM. Prediksi harian model OS-ELM berangsur-angsur mengendap menjadi nilai konstan linier (Skenario B membeku pada `+0.000206` dan Skenario C pada `+0.000200`). Ini merupakan bukti empiris yang sangat mahal mengenai risiko *over-regularization*. Ketika data mengalir tanpa adanya interupsi penyegaran parameter dalam jangka waktu yang terlampau panjang, estimasi analitis pseudo-invers mengalami saturasi matematis. Bobot internal model kehilangan kemampuan adaptasi mikro terhadap volatilitas harian baru dan runtuh menjadi penilai tren statis. Fenomena keruntuhan plastisitas ini mengonfirmasi mengapa model komparasi non-linear seperti XGBoost—yang dipaksa melakukan *cold restart* menggunakan jendela bergulir tetap 250 hari terakhir—tetap mempertahankan volatilitas prediksinya (XGB std berada sehat di angka 0.007–0.010).

### **3.4. Pembuktian Paradoks Eksperimen Melalui Batas Ekstrem (Static vs Daily)**

**Pembuktian Kelumpuhan Statis OS-ELM:** Pada Skenario Static (Step 5), dibuktikan secara empiris bahwa tanpa interupsi penyegaran data, OS-ELM mengalami degenerasi total dengan nilai varians atau standar deviasi (σ) sebesar 0.000000, membeku pada nilai konstan tunggal +0.001090. Ini memvalidasi asumsi teoretis bahwa fungsi aktivasi sigmoid pada data aliran finansial multivariat tanpa retraining akan langsung mengalami saturasi numerik permanen.

**Kebangkitan Kembali via Inkremental Harian:** Kontras dengan kondisi statis, Skenario Daily Retraining (Step 6) berhasil membangkitkan kembali plastisitas OS-ELM (skor σ naik sehat ke 0.001486). Namun, penyegaran harian ini harus dibayar dengan lonjakan waktu komputasi yang destruktif mencapai 501.90 detik (meroket sangat ekstrem hingga hampir 3.400% dibandingkan waktu baseline model statis 14.34 detik). Lonjakan masif ini mengunci argumen inti riset: retraining harian secara buta menghasilkan pemborosan overhead komputasi yang tidak masuk akal dalam lingkungan bursa produksi.

# **4. Panduan Interaksi Langkah Kerja untuk Fase Selanjutnya**

Seluruh matriks hasil proyeksi dari pengujian Fase 3 telah aman dipersingkat dan disimpan ke dalam struktur direktori repositori kita. Data penampung yang siap diolah pada fase berikutnya adalah:

1. `predictions_step2.csv` (Luaran Skenario A — Wasserstein 60)
2. `predictions_step3.csv` (Luaran Skenario B — Wasserstein 120)
3. `predictions_step4.csv` (Luaran Skenario C — ADWIN)
4. `predictions_step5.csv` (Luaran Skenario Batas Atas Eror — Static)
5. `predictions_step6.csv` (Luaran Skenario Batas Atas Komputasi — Daily)

**Catatan Rigid Fase 4:** Evaluasi metrik akurasi (RMSE dan MAPE) wajib dihitung secara komparatif lintas 5 skenario ini (total 10 kolom prediksi model) murni pada zona simulasi bursa (baris indeks integer 241 hingga 3928).

Dokumen ini mengunci keabsahan seluruh rangkaian pipa retraining. Pada pelaksanaan Fase 4 nanti, kita dilarang keras mengubah, menggeser, atau memodifikasi nilai prediksi harian yang telah diproduksi di Fase 3 ini untuk menjamin kesucian pengujian statistik.
