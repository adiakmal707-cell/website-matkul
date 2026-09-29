from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "website_matkul_rahasia"

USERNAME = "akmal"
PASSWORD = "252525"

DATABASE = "database.db"

def buat_database():
    conn = get_db()

    # Membuat tabel materi
    conn.execute("""
        CREATE TABLE IF NOT EXISTS materi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            kategori TEXT NOT NULL,
            isi TEXT NOT NULL
        )
    """)

    # Membuat tabel mata kuliah
    conn.execute("""
        CREATE TABLE IF NOT EXISTS matkul (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL UNIQUE,
            ikon TEXT NOT NULL,
            deskripsi TEXT
        )
    """)

    # Data mata kuliah awal
    matkul_awal = [
        ("Pemrograman", "💻", "Python, tipe data, variable, expression dan coding."),
        ("Algoritma", "🧠", "Algoritma dan pemecahan masalah."),
        ("Database", "🗄️", "Basis data dan pengelolaan database."),
        ("Sistem Informasi", "🖥️", "Konsep dan penerapan sistem informasi."),
        ("Komputer Dasar", "🧮", "Dasar-dasar komputer."),
        ("Tugas", "📝", "Kumpulan tugas perkuliahan.")
    ]

    for nama, ikon, deskripsi in matkul_awal:
        conn.execute("""
            INSERT OR IGNORE INTO matkul
            (nama, ikon, deskripsi)
            VALUES (?, ?, ?)
        """, (nama, ikon, deskripsi))

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["login"] = True
            return redirect(url_for("dashboard"))

        else:
            return render_template(
                "login.html",
                error="Username atau password salah!"
            )

    return render_template("login.html")

@app.route("/lupa-password", methods=["GET", "POST"])
def lupa_password():

    pesan = None

    if request.method == "POST":

        username = request.form.get("username")

        if username == USERNAME:
            pesan = "Username ditemukan. Silakan hubungi administrator untuk mengatur ulang kata sandi."
        else:
            pesan = "Username tidak ditemukan."

    return render_template(
        "lupa_password.html",
        pesan=pesan
    )

@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if not session.get("login"):
        return redirect(url_for("login"))

    conn = get_db()

    # Jika tombol Simpan ditekan
    if request.method == "POST":

        judul = request.form.get("judul")
        kategori = request.form.get("kategori")
        isi = request.form.get("isi")

        # Simpan materi ke database
        conn.execute("""
            INSERT INTO materi (judul, kategori, isi)
            VALUES (?, ?, ?)
        """, (judul, kategori, isi))

        conn.commit()
        conn.close()

        # Kembali ke dashboard
        return redirect(url_for("dashboard"))

    # Mengambil daftar mata kuliah
    matkul = conn.execute("""
        SELECT * FROM matkul
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    return render_template(
        "tambah.html",
        matkul=matkul
    )


@app.route("/dashboard")
def dashboard():
    if not session.get("login"):
        return redirect(url_for("login"))

    conn = get_db()

    materi = conn.execute("""
        SELECT * FROM materi
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    if materi is None:
        return "Materi tidak ditemukan", 404
    
    return render_template(
        "dashboard.html",
        materi=materi
    )

@app.route("/materi/<int:id>")
def detail_materi(id):
    if not session.get("login"):
        return redirect(url_for("login"))

    conn = get_db()

    materi = conn.execute("""
        SELECT * FROM materi
        WHERE id = ?
    """, (id,)).fetchone()

    conn.close()

    if materi is None:
        return "Materi tidak ditemukan", 404

    return render_template(
        "detail_materi.html",
        materi=materi
    )

@app.route("/hapus-materi/<int:id>", methods=["POST"])
def hapus_materi(id):
    if not session.get("login"):
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute("""
        DELETE FROM materi
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    buat_database()
    app.run(debug=True, host="0.0.0.0", port=5000)