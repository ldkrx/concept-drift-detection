# **Laporan Resmi Eksekusi Fase 4: Analisis Metrik Evaluasi Komprehensif & ROI Komputasi**

Dokumen ini memuat temuan akhir dan analisis kuantitatif dari simulasi rolling retraining pada data Indeks Harga Saham Gabungan (IHSG) periode 2010–2026. Segala bentuk metrik telah dihitung secara adil dengan mengisolasi zona pemanasan (warm-up bias) murni pada 3.688 baris zona simulasi (indeks 241–3928).

# **1. Koreksi Metodologis: Diskualifikasi MAPE sebagai Metrik**

Pada awal eksekusi, kita menemukan kecacatan fundamental pada metrik ϵ-MAPE. Pada satu hari bursa yang sangat stagnan (30 November 2017), metrik MAPE milik Pred_XGB_A meledak hingga **190.081.112%** akibat fenomena pembagian dengan angka log return yang nyaris nol mutlak.

**Keputusan Kritis:** Penggunaan MAPE resmi **DIGUGURKAN** untuk keseluruhan naskah. Evaluasi kinerja prediksi dialihkan secara penuh menggunakan MAE (Mean Absolute Error) dan RMSE (Root Mean Square Error) karena terbukti kebal terhadap anomali pembagian nol, sehingga menyajikan komparasi eror yang 100% adil antar model.

# **2. Pembuktian Hipotesis 1: Kematian Plastisitas (Plasticity Death) pada OS-ELM**

Kita berhasil mengonfirmasi secara empiris mengapa model machine learning konvensional tidak bisa dibiarkan berjalan tanpa retraining di pasar dinamis:

**Bukti Statistik:** Model Pred_OSELM_Static memiliki standar deviasi prediksi (σ) sebesar **0.00000034** (mendekati nol mutlak).

**Bukti Visual:** Pada plot rentang tahun 2020 (fig2_oselm_2020.jpg), prediksi OS-ELM Statis terbukti membeku menjadi garis lurus horizontal konstan di kisaran angka **+0.001069**.

**Jebakan Analitis:** Meskipun secara rata-rata jarak (MAE) OS-ELM Statis terlihat "baik" (0,15% lebih kecil dari Daily), itu adalah ilusi matematis. Menebak garis lurus di tengah data yang berfluktuasi antara nilai positif dan negatif kecil memang menghasilkan rata-rata sisaan absolut yang rendah, namun model tersebut **100% tidak memiliki kapasitas** prediksi tren yang berguna di dunia nyata.

# **3. Pembuktian Hipotesis 2: Validasi Empiris The Window Dilemma**

Pengujian pada rumpun XGBoost mengonfirmasi tesis *The Window Dilemma* (Gower-Winter et al., 2026) bahwa detektor concept drift berbasis fixed-window (jendela statis) justru dapat merusak akurasi algoritma berbasis pohon:

| Skenario | Konfigurasi | Penalti MAE | Vonis |
|---|---|---|---|
| Skenario A | Wasserstein 60 Hari | **+95,10%** | Sangat Memburuk |
| Skenario B | Wasserstein 120 Hari | **+37,65%** | Memburuk |
| Skenario C | Aliran ADWIN Murni | **+13,09%** | Penalti XGBoost Terendah |

**Kesimpulan:** Memaksa XGBoost belajar secara berulang pada batasan jendela historis sempit (60/120 hari) pasca-drift memicu overfitting fatal pada noise jangka pendek bursa.

# **4. Temuan Puncak (Novelty): ROI Komputasi Maksimal dengan ADWIN**

Detektor ADWIN (Skenario C) terbukti menjadi **"Pahlawan" (Hero Strategy)** dalam arsitektur penelitian kita, memberikan metrik Trade-off Waktu vs. Akurasi (Return on Investment) yang nyaris sempurna:

**Penghematan Ekstrem:** Memangkas beban komputasi sebesar **96,17%** (Hanya memakan **19,21 detik** dibandingkan **501,90 detik** milik Daily Retraining).

**Pemulihan Detak Jantung:** ADWIN sukses menghidupkan kembali plastisitas OS-ELM yang mati tanpa merusak akurasinya.

**Akurasi Setara Batas Atas:** Pada pengujian rasio khusus di zona krisis 2020, tingkat eror RMSE OS-ELM ADWIN hanya **1,001× (0,1%) lebih buruk** daripada model yang dilatih ulang setiap hari (Daily). Pengorbanan 0,1% akurasi untuk memangkas 96% biaya komputasi adalah penemuan saintifik yang sangat kuat.

# **5. Validasi Respons Krisis (Peristiwa Black Swan 2020)**

Detektor ADWIN membunyikan alarm drift secara akurat pada masa Puncak Kehancuran Bursa akibat COVID-19 (termasuk pada 17 Maret 2020).

Memburuknya MAE sesaat setelah alarm (+27% hingga +44%) **bukanlah** kegagalan model, melainkan realitas guncangan harga ekstrem tak terduga (Black Swan Event). Retraining yang dipicu oleh alarm tersebut adalah mekanisme yang sukses me-reset pemahaman model menuju "Normal Baru" pasca-krisis.

# **6. Matriks Metrik Evaluasi Lintas Skenario**

Tabel berikut menyajikan metrik MAE dan RMSE komparatif akhir di seluruh model prediksi, dihitung murni pada zona simulasi (indeks 241–3928):

| Metrik | Model | Static (Step 5) | Skenario C (ADWIN) | Skenario B (Wass-120) | Skenario A (Wass-60) | Daily (Step 6) |
|---|---|---|---|---|---|---|---|
| **MAE** | Pred_XGB | 0,011059 | 0,009133 | 0,011116 | 0,015755 | 0,008076 |
| **MAE** | Pred_OSELM | 0,007365 | 0,007375 | 0,007373 | 0,007374 | 0,007377 |
| **RMSE** | Pred_XGB | 0,014402 | 0,013699 | 0,014538 | 0,019258 | 0,011999 |
| **RMSE** | Pred_OSELM | 0,010787 | 0,010804 | 0,010804 | 0,010807 | 0,010805 |
| **Std Dev Prediksi** | Pred_XGB | 0,005731 | 0,007630 | 0,007160 | 0,010150 | 0,004900 |
| **Std Dev Prediksi** | Pred_OSELM | 0,000000 | 0,001488 | 0,001489 | 0,001494 | 0,001486 |

**Wawasan Kunci dari Matriks Metrik:**

1. **Hampir Seragamnya Metrik OS-ELM:** Semua skenario OS-ELM menghasilkan MAE yang sangat berdekatan (0,007365–0,007377) dan RMSE (0,010787–0,010807) — rentang hanya ±0,15% relatif. Berbeda dengan XGBoost, pembaruan RLS inkremental OS-ELM konvergen ke basin eror yang serupa terlepas dari frekuensi retraining. Bahkan model statis (nol retrain) mencapai eror agregat yang hampir identik, mengonfirmasi bahwa metrik berbasis rata-rata saja tidak cukup untuk mendeteksi kematian plastisitas.

2. **OS-ELM Harian Tanpa Keunggulan Bermakna:** Retraining harian (MAE=0,007377, RMSE=0,010805) tidak dapat dibedakan secara bermakna dari skenario berbasis drift — tidak lebih baik maupun lebih buruk. Biaya komputasi 26× lipat tidak membeli manfaat akurasi apa pun, menjadikan retraining harian sebagai strategi yang secara objektif tidak rasional untuk OS-ELM.

3. **Gradien Sensitivitas XGBoost:** Penalti MAE relatif terhadap baseline Daily: ADWIN (+13,09%) → Static (+36,94%) → Wass-120 (+37,65%) → Wass-60 (+95,10%). Yang kritis, XGBoost Statis (tanpa retraining) menyamai Wass-120 dalam akurasi, membuktikan bahwa retraining paksa dengan jendela sempit justru merugikan model berbasis pohon — bukti empiris inti bagi tesis Window Dilemma.

4. **Varians Prediksi OS-ELM Statis:** Standar deviasi nol (0,000000) adalah tanda tangan empiris definitif dari kematian plastisitas total — model secara matematis telah flatlined (datar tanpa denyut).

Dokumen ini mengunci keabsahan seluruh perhitungan metrik evaluasi Fase 4. Temuan ini merupakan bukti empiris utama bagi klaim novelty pada naskah prosiding.

(End of file - total 82 lines)
