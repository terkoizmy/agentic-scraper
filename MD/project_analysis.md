# Analisis dan Saran Pengembangan Agentic-Scraper

Berdasarkan tinjauan struktur proyek berjalan, terdapat fondasi arsitektur yang sangat bagus yang mengombinasikan ReAct agent, RAG, dan pemisahan Vector Database. Namun, agar proyek ini benar-benar berjalan sesuai konsep *autonomous scraper*, beberapa fungsionalitas inti masih perlu disambung dan diselesaikan.

Berikut adalah daftar pilar yang masih kurang, beserta rekomendasi penambahannya untuk versi produksi:

## 1. Integrasi Scheduler Sebenarnya (Backend) 🚨 Prioritas Utama
Saat ini sistem *scheduler* (`apscheduler` di `backend/scheduler/cron.py`) hanya sekadar menyala tanpa aksi apa-apa.
* **Kondisi:** Meskipun *user* menginput `schedule_hours` (misal 24 jam) saat menambah target *source*, database tidak mengeksekusinya ke siklus *scheduler*.
* **Aksi Pengerjaan:**
  * Buat metode sinkronasi (contoh: `sync_jobs()`) di `scheduler/cron.py` yang membaca seluruh record pada tabel `sources` di PostgreSQL.
  * Secara dinamis meregistrasikan rutinitas *background* (contoh: memanggil pipeline otomatis) di memory scheduler menggunakan perintah eksekusi dari `apscheduler`, sesuai dengan interval masing-masing *source*.

## 2. Aksi "Scrape Now", "Edit", & "Delete" (Frontend)
Halaman referensi Data Sources (`/sources`) masih sebatas melihat tabel (Read) dan *Create*.
* **Aksi Pengerjaan:**
  * Tambahkan kolom baru (`Actions/Aksi`) pada baris tabel situs Web Sources.
  * **Scrape Now (⚡):** Tombol yang me-*request* operasi secara manual untuk merayapi data (*scrape/crawl*), melewati antrean jadwal background.
  * **Edit & Delete:** Tambahkan binding UI untuk menyambung rute Backend `PATCH /api/sources/{id}` (untuk update jadwal/status aktif) dan `DELETE /api/sources/{id}` (menghapus referensi cascading pada database).

## 3. Pembuatan RAG "Playground" (Frontend)
Direktori `frontend/src/pages/playground` masih **kosong**. Sistem telah menyertakan integrasi RAG dan ChromaDB di sisi backend, tetapi kita membutuhkan jembatan UI untuk menguji kualitas vector semantic-nya.
* **Aksi Pengerjaan:**
  * Buat tampilan UI Playground sederhana yang berisi form pencarian layaknya Google Search.
  * *Request* dari UI tersebut akan memanggil `POST /api/query`.
  * Tampilkan *card/hasil penelusuran* dari serpihan data mentah *(chunks)* berserta indikator kedekatan pencarian (*Confidence / Similarity Score*). Hal ini berguna untuk menakar kualitas chunking dan efisiensi model embedder dari database vektor secara visual.

## 4. Halaman Histori "Scrape Jobs" Spesifik (Frontend)
Direktori `frontend/src/pages/jobs` masih **kosong**. Walaupun *dashboard* telah menampilkan aktivitas logs teratas, Anda membutuhkan jejak audit secara penuh.
* **Aksi Pengerjaan:**
  * Implementasikan halaman baru (tabel list) yang mengambil daftar aktivitas melalui rute backend `GET /api/scrape/jobs`.
  * Sangat krusial untuk menambahkan kolom "Error Detail" untuk memantau pesan error spesifik (`job.error`). Fitur ini menjadi poin pengecekan utama ketika terdapat rintangan perayapan, seperti gangguan limit jaringan, target diproteksi Cloudflare anti-bot scraper, dsj.

## 5. Sinkronisasi Frontend dengan Agent Chat
Berdasarkan _rulebase_ proyek, endpoint `POST /api/agent/ask` memproses alur reasoning intelligence (ReAct). UI pada "chat-bubble" perlu dipersolid koneksinya.
* **Prioritas:** Memastikan UI layar Agent sepenuhnya dapat merender struktur respon streaming (bila perlu memunculkan visual *thinking/calls tool* layaknya ChatGPT pro) serta dapat memanggil *tool web_search* maupun merender kesimpulan sumber data secara elegan kepada pengguna.

---
**Catatan Selanjutnya:** Mengerjakan **Poin 1** dan **Poin 2** akan memberikan pijakan *quick-wins* yang terasa paling instan pada fungsionalitas keseluruhan aplikasi Anda.
