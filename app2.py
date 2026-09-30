from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "website_matkul_rahasia"

USERNAME = "akmal"
PASSWORD = "252525"

DATABASE = "database.db"

def buat_database():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
    )
    """)

    # Jadwal Matkul
    conn.execute("""
    CREATE TABLE IF NOT EXISTS jadwal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hari TEXT NOT NULL,
    jam_mulai TEXT NOT NULL,
    jam_selesai TEXT NOT NULL,
    mata_kuliah TEXT NOT NULL,
    ruang TEXT NOT NULL
)
""")

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

    jadwal_data = [
    ("Senin", "07.30", "09.10",
     "Pengantar Rekayasa Perangkat Lunak", "LAB CC304"),

    ("Senin", "13.00", "14.40",
     "Algoritma dan Dasar Pemrograman", "LAB CC304"),

    ("Senin", "14.50", "16.30",
     "Organisasi dan Arsitektur Komputer (Jam Terstruktur)", "LAB CC304"),

    ("Selasa", "07.30", "12.00",
     "Organisasi dan Arsitektur Komputer", "LAB CC304"),

    ("Selasa", "13.00", "14.40",
     "Algoritma dan Dasar Pemrograman (Jam Terstruktur)", "LAB CC304"),

    ("Rabu", "07.30", "09.10",
     "Sistem Informasi", "LAB CC304"),

    ("Rabu", "09.20", "14.40",
     "Algoritma dan Dasar Pemrograman", "LAB CC304"),

    ("Rabu", "14.50", "16.30",
     "Algoritma dan Dasar Pemrograman (Jam Terstruktur)", "LAB CC304"),

    ("Kamis", "07.30", "12.00",
     "Basis Data", "LAB CC304"),

    ("Kamis", "13.00", "14.40",
     "Matematika Diskrit", "LAB CC304"),

    ("Jumat", "09.20", "12.00",
     "Basis Data (Jam Terstruktur)", "LAB CC304"),

    ("Jumat", "13.00", "14.40",
     "Pancasila", "LAB CC304")
]

    conn.executemany("""
    INSERT INTO jadwal
    (hari, jam_mulai, jam_selesai, mata_kuliah, ruang)
    VALUES (?, ?, ?, ?, ?)
    """, jadwal_data)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/jadwal")
def jadwal():
    if not session.get("login"):
        return redirect(url_for("login"))

    hari = request.args.get("hari", "Senin")

    conn = get_db()

    data_jadwal = conn.execute("""
        SELECT *
        FROM jadwal
        WHERE hari = ?
        ORDER BY jam_mulai
    """, (hari,)).fetchall()

    conn.close()

    return render_template(
        "jadwal.html",
        jadwal=data_jadwal,
        hari=hari
    )

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["login"] = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["nama"] = user["nama"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        else:

            return render_template(
                "login.html",
                error="Username atau password salah!"
            )

    return render_template("login.html")

@app.route("/daftar", methods=["GET", "POST"])
def daftar():
    pesan = None

    if request.method == "POST":
        nama = request.form["nama"].strip()
        username = request.form["username"].strip()
        password = request.form["password"]
        konfirmasi = request.form["konfirmasi"]

        if not nama or not username or not password:
            pesan = "Semua field wajib diisi."
            return render_template("daftar.html", pesan=pesan)

        if password != konfirmasi:
            pesan = "Konfirmasi password tidak cocok."
            return render_template("daftar.html", pesan=pesan)

        conn = get_db()

        user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user:
            conn.close()
            pesan = "Username sudah digunakan."
            return render_template("daftar.html", pesan=pesan)

        password_hash = generate_password_hash(password)

        conn.execute("""
            INSERT INTO users (nama, username, password, role)
            VALUES (?, ?, ?, ?)
        """, (nama, username, password_hash, "user"))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("daftar.html", pesan=pesan)

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