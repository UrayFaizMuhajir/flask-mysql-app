# flask-mysql-app

Tugas Praktikum Komputasi Awan: Jenkins + GitHub + Docker + Database.

Aplikasi Flask sederhana (CRUD data mahasiswa) yang terhubung ke **MySQL 8**.

## Alur pipeline Jenkins
1. **Checkout**: ambil kode dari GitHub (dipicu webhook)
2. **Build Docker Image**: `docker build`
3. **Test Image**: cek sintaks `app.py` di dalam container
4. **Push Docker Image**: push ke Docker Hub (`urayfaizmuhajir/flask-mysql-app`)
5. **Deploy App + MySQL**: `docker compose up -d` (container app + db)
6. **Verify Database Connection**: cek endpoint `/health`

## Endpoint
- `/`: halaman data mahasiswa (tambah/hapus)
- `/health`: status koneksi database (JSON)

## Menjalankan manual
```
docker compose up -d --build
```
Buka http://localhost:5000
