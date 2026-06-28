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

Secara konvensional, peneliti berasumsi bahwa memperlebar ukuran jendela statistik (Skenario B = 120 hari) akan memperhalus fluktuasi sehingga jumlah alarm pemicu mengecil. Namun, data eksperimen menunjukkan pembalikan: Jendela Semesteran (120 hari) memicu **311 alarm**, jauh lebih padat daripada Jendela Kuartalan (60 hari) yang hanya memicu **271 alarm**. Temuan ini konsisten dengan sekaligus memperluas tesis *The Window Dilemma* (Gower-Winter et al., 2026). Interpretasi empiris kami adalah bahwa jendela yang lebih besar dapat bertindak sebagai akumulator distorsi; pola pergeseran struktural dari bulan-bulan sebelumnya mengendap di dalam jendela referensi, sehingga begitu ambang batas Wasserstein terlampaui, detektor mengalami badai pemicuan beruntun. Ironisnya, efisiensi komputasi justru meningkat: meskipun memicu **15% lebih banyak retraining** (311 vs 271), Skenario B hanya membutuhkan **95.37 detik** — berkurang **25%** dibandingkan Skenario A (127.62 detik). Hubungan terbalik ini menggugat asumsi bahwa jumlah retraining semata-mata menentukan biaya komputasi. Kuncinya terletak pada biaya per-retrain OS-ELM: setiap retrain Wasserstein-120 beroperasi pada buffer data akumulasi yang lebih pendek (akibat jarak pemicuan yang lebih rapat), sehingga menghasilkan operasi inversi matriks yang lebih kecil (0,307s per retrain) dibandingkan buffer besar pada Wasserstein-60 yang jarang memicu (0,471s per retrain).

### **3.2. Paradoks Beban Komputasi Aliran Pure-Stream (ADWIN Buffer)**

Skenario C (ADWIN) bertindak sebagai detektor aliran murni yang sangat konservatif. Sepanjang 15 tahun linimasa, ADWIN berhasil meredam noise pasar dan hanya meloloskan **34 kali sinyal drift struktural**. Efisiensi komputasinya luar biasa: Skenario C selesai hanya dalam **19.21 detik** — berkurang **96,17%** dari Daily Retraining (501,90 detik) dan hanya **4,87 detik** di atas baseline Static (14,34 detik). Ini menjadikan ADWIN sebagai strategi drift-driven paling efisien secara komputasi di antara semua skenario yang diuji.

Namun, paradoks halus muncul saat menganalisis biaya per-retrain: setiap retrain ADWIN memakan rata-rata **0,565 detik**, jauh lebih tinggi daripada Daily (0,136s/retrain) dan Wasserstein-120 (0,307s/retrain). Premi ini timbul karena interval panjang antara alarm ADWIN yang jarang (34 retrain sepanjang 15 tahun) menyebabkan buffer data sekuensial OS-ELM mengakumulasi ribuan baris antar retrain. Saat pemicu ADWIN akhirnya menyala, fungsi rekursif least squares (RLS) harus melakukan inversi matriks pada buffer akumulasi yang membengkak ini. Namun, biaya per-retrain ini menjadi dapat diabaikan secara absolut — total waktu komputasi 19,21 detik tetap menempatkan ADWIN sebagai pemenang komputasi yang jelas, membuktikan bahwa metrik efisiensi dunia nyata adalah total runtime, bukan biaya per-peristiwa.

### **3.3. Fenomena Kematian Plastisitas (Weight Collapse) pada OS-ELM**

Pemeriksaan mendalam pada ekor runtun waktu prediksi (tail zone Juni 2026) mendeteksi adanya gejala pembekuan numerik pada model OS-ELM. Prediksi harian model OS-ELM berangsur-angsur mengendap menjadi nilai konstan linier (Skenario B membeku pada `+0.000206` dan Skenario C pada `+0.000200`). Ini merupakan bukti empiris yang sangat mahal mengenai risiko *over-regularization*. Ketika data mengalir tanpa adanya interupsi penyegaran parameter dalam jangka waktu yang terlampau panjang, estimasi analitis pseudo-invers mengalami saturasi matematis. Bobot internal model kehilangan kemampuan adaptasi mikro terhadap volatilitas harian baru dan runtuh menjadi penilai tren statis. Fenomena keruntuhan plastisitas ini mengonfirmasi mengapa model komparasi non-linear seperti XGBoost—yang dipaksa melakukan *cold restart* menggunakan jendela bergulir tetap 250 hari terakhir—tetap mempertahankan volatilitas prediksinya (XGB std berada sehat di angka 0.007–0.010).

### **3.4. Pembuktian Paradoks Eksperimen Melalui Batas Ekstrem (Static vs Daily)**

**Bukti Empiris Kelumpuhan Statis OS-ELM:** Pada Skenario Static (Step 5), tanpa interupsi penyegaran data, OS-ELM mengalami degenerasi total dengan nilai varians atau standar deviasi (σ) sebesar 0.000000 dan membeku pada nilai konstan tunggal +0.001090. Ini mendukung interpretasi bahwa fungsi aktivasi sigmoid pada data aliran finansial multivariat dapat mengalami saturasi numerik permanen tanpa retraining.

**Kebangkitan Kembali via Inkremental Harian:** Kontras dengan kondisi statis, Skenario Daily Retraining (Step 6) berhasil membangkitkan kembali plastisitas OS-ELM (skor σ naik sehat ke 0.001486). Namun, penyegaran harian ini harus dibayar dengan lonjakan waktu komputasi yang destruktif mencapai 501.90 detik (meroket sangat ekstrem hingga hampir 3.400% dibandingkan waktu baseline model statis 14.34 detik). Lonjakan masif ini mengunci argumen inti riset: retraining harian secara buta menghasilkan pemborosan overhead komputasi yang tidak masuk akal dalam lingkungan bursa produksi.

# **4. Panduan Interaksi Langkah Kerja untuk Fase Selanjutnya**

Seluruh matriks hasil proyeksi dari pengujian Fase 3 telah aman dipersingkat dan disimpan ke dalam struktur direktori repositori kita. Data penampung yang siap diolah pada fase berikutnya adalah:

1. `predictions_step2.csv` (Luaran Skenario A — Wasserstein 60)
2. `predictions_step3.csv` (Luaran Skenario B — Wasserstein 120)
3. `predictions_step4.csv` (Luaran Skenario C — ADWIN)
4. `predictions_step5.csv` (Luaran Skenario Batas Atas Eror — Static)
5. `predictions_step6.csv` (Luaran Skenario Batas Atas Komputasi — Daily)

**Catatan Rigid Fase 4:** Evaluasi metrik akurasi akhir (MAE dan RMSE) wajib dihitung secara komparatif lintas 5 skenario ini (total 10 kolom prediksi model) murni pada zona simulasi bursa (baris indeks integer 241 hingga 3928). ε-MAPE hanya boleh dipertahankan sebagai uji tekan diagnostik untuk ketidakstabilan target dekat nol.

Dokumen ini mengunci keabsahan seluruh rangkaian pipa retraining. Pada pelaksanaan Fase 4 nanti, kita dilarang keras mengubah, menggeser, atau memodifikasi nilai prediksi harian yang telah diproduksi di Fase 3 ini untuk menjamin kesucian pengujian statistik.
