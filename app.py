import os
import time

import pymysql
from flask import Flask, jsonify, redirect, render_template_string, request, url_for

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppass123"),
    "database": os.getenv("DB_NAME", "praktikum"),
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def init_db(retries=30, delay=2):
    """Tunggu MySQL siap, lalu buat tabel jika belum ada."""
    for attempt in range(1, retries + 1):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS mahasiswa (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nama VARCHAR(100) NOT NULL,
                        nim VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            print("Database siap.", flush=True)
            return
        except pymysql.MySQLError as exc:
            print(f"Menunggu database ({attempt}/{retries}): {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError("Tidak bisa terhubung ke database")


PAGE = """
<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <title>Data Mahasiswa - Flask + MySQL</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; }
    table { width: 100%; border-collapse: collapse; margin-top: 16px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background: #f0f0f0; }
    input { padding: 6px; margin-right: 6px; }
    button { padding: 6px 12px; }
    .ok { color: green; }
  </style>
</head>
<body>
  <h1>Data Mahasiswa</h1>
  <p class="ok">Flask + Docker + Jenkins, terhubung ke MySQL ({{ db_host }}/{{ db_name }})</p>
  <form method="post" action="{{ url_for('tambah') }}">
    <input name="nama" placeholder="Nama" required>
    <input name="nim" placeholder="NIM" required>
    <button type="submit">Tambah</button>
  </form>
  <table>
    <tr><th>ID</th><th>Nama</th><th>NIM</th><th>Dibuat</th><th></th></tr>
    {% for m in data %}
    <tr>
      <td>{{ m.id }}</td><td>{{ m.nama }}</td><td>{{ m.nim }}</td><td>{{ m.created_at }}</td>
      <td>
        <form method="post" action="{{ url_for('hapus', mhs_id=m.id) }}">
          <button type="submit">Hapus</button>
        </form>
      </td>
    </tr>
    {% else %}
    <tr><td colspan="5">Belum ada data.</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""


@app.route("/")
def index():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM mahasiswa ORDER BY id DESC")
        data = cur.fetchall()
    return render_template_string(
        PAGE, data=data, db_host=DB_CONFIG["host"], db_name=DB_CONFIG["database"]
    )


@app.route("/tambah", methods=["POST"])
def tambah():
    nama = request.form.get("nama", "").strip()
    nim = request.form.get("nim", "").strip()
    if nama and nim:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO mahasiswa (nama, nim) VALUES (%s, %s)", (nama, nim))
    return redirect(url_for("index"))


@app.route("/hapus/<int:mhs_id>", methods=["POST"])
def hapus(mhs_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM mahasiswa WHERE id = %s", (mhs_id,))
    return redirect(url_for("index"))


@app.route("/health")
def health():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM mahasiswa")
            total = cur.fetchone()["total"]
        return jsonify(status="ok", database="connected", total_mahasiswa=total)
    except Exception as exc:  # noqa: BLE001
        return jsonify(status="error", database="disconnected", detail=str(exc)), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
