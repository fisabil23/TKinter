import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "prediksi_diabetes.db"


# Membuat database dan tabel
def buat_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pasien TEXT NOT NULL,
            usia INTEGER NOT NULL,
            gula_darah REAL NOT NULL,
            bmi REAL NOT NULL,
            riwayat_ortu TEXT NOT NULL,
            hasil_prediksi TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Fungsi prediksi risiko diabetes
def prediksi_risiko(gula, bmi, riwayat):
    if gula >= 200:
        return "Sangat Tinggi", "#dc2626"

    elif gula >= 140:
        if bmi >= 30 and riwayat == "Ya":
            return "Tinggi", "#ea580c"
        return "Sedang", "#ca8a04"

    elif bmi >= 30:
        if riwayat == "Ya":
            return "Sedang", "#ca8a04"
        return "Waspada", "#2563eb"

    elif riwayat == "Ya":
        return "Waspada", "#2563eb"

    else:
        return "Rendah", "#16a34a"


# Fungsi menyimpan data pasien
def simpan_pasien():
    nama = entry_nama.get().strip()
    usia_text = entry_usia.get().strip()
    gula_text = entry_gula.get().strip()
    bmi_text = entry_bmi.get().strip()
    riwayat = combo_ortu.get()

    if not nama or not usia_text or not gula_text or not bmi_text or not riwayat:
        messagebox.showwarning(
            "Peringatan",
            "Semua kolom harus diisi!"
        )
        return

    try:
        usia = int(usia_text)
        gula = float(gula_text.replace(",", "."))
        bmi = float(bmi_text.replace(",", "."))

    except ValueError:
        messagebox.showerror(
            "Kesalahan",
            "Usia harus bilangan bulat, sedangkan gula darah dan BMI harus berupa angka."
        )
        return

    if usia < 1 or usia > 120:
        messagebox.showerror(
            "Kesalahan",
            "Usia harus antara 1 sampai 120 tahun."
        )
        return

    if gula <= 0 or gula > 1000:
        messagebox.showerror(
            "Kesalahan",
            "Gula darah harus lebih dari 0 dan maksimal 1000 mg/dL."
        )
        return

    if bmi < 10 or bmi > 100:
        messagebox.showerror(
            "Kesalahan",
            "BMI harus antara 10 sampai 100."
        )
        return

    hasil, warna = prediksi_risiko(
        gula, bmi, riwayat
    )

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pasien
        (nama_pasien, usia, gula_darah, bmi,
         riwayat_ortu, hasil_prediksi)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nama, usia, gula, bmi, riwayat, hasil))

    conn.commit()
    conn.close()

    label_hasil.config(
        text="Hasil Prediksi: " + hasil,
        fg=warna
    )

    messagebox.showinfo(
        "Berhasil",
        "Data pasien berhasil disimpan!"
    )


# Fungsi menampilkan seluruh data pasien
def lihat_data():
    jendela = tk.Toplevel(root)
    jendela.title("Riwayat Data Pasien")
    jendela.geometry("900x400")

    kolom = (
        "id", "nama", "usia", "gula",
        "bmi", "ortu", "hasil"
    )

    tabel = ttk.Treeview(
        jendela,
        columns=kolom,
        show="headings"
    )

    judul = {
        "id": "ID",
        "nama": "Nama Pasien",
        "usia": "Usia",
        "gula": "Gula Darah",
        "bmi": "BMI",
        "ortu": "Riwayat Ortu",
        "hasil": "Hasil Prediksi"
    }

    for kolom_item in kolom:
        tabel.heading(
            kolom_item,
            text=judul[kolom_item]
        )
        tabel.column(
            kolom_item,
            width=120,
            anchor="center"
        )

    tabel.pack(fill="both", expand=True)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nama_pasien, usia, gula_darah,
               bmi, riwayat_ortu, hasil_prediksi
        FROM pasien
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()

    for baris in data:
        tabel.insert("", "end", values=baris)

    if not data:
        messagebox.showinfo(
            "Informasi",
            "Belum ada data pasien yang tersimpan.",
            parent=jendela
        )


# Fungsi mengosongkan form
def reset_form():
    entry_nama.delete(0, tk.END)
    entry_usia.delete(0, tk.END)
    entry_gula.delete(0, tk.END)
    entry_bmi.delete(0, tk.END)
    combo_ortu.set("")

    label_hasil.config(
        text="Hasil prediksi akan tampil di sini",
        fg="#475569"
    )


# Membuat database
buat_database()


# Membuat jendela utama
root = tk.Tk()
root.title("Aplikasi Prediksi Risiko Diabetes")
root.geometry("550x620")
root.resizable(False, False)
root.configure(bg="#f1f5f9")


# Judul aplikasi
tk.Label(
    root,
    text="PREDIKSI RISIKO DIABETES",
    font=("Arial", 18, "bold"),
    bg="#f1f5f9",
    fg="#1e3a8a"
).pack(pady=20)


# Frame form input
form = tk.Frame(root, bg="#f1f5f9")
form.pack(padx=30, pady=10)


def tambah_label(teks, baris):
    tk.Label(
        form,
        text=teks,
        font=("Arial", 10),
        bg="#f1f5f9"
    ).grid(
        row=baris,
        column=0,
        sticky="w",
        padx=10,
        pady=10
    )


tambah_label("Nama Pasien", 0)
entry_nama = ttk.Entry(form, width=30)
entry_nama.grid(row=0, column=1, pady=10)

tambah_label("Usia (tahun)", 1)
entry_usia = ttk.Entry(form, width=30)
entry_usia.grid(row=1, column=1, pady=10)

tambah_label("Gula Darah (mg/dL)", 2)
entry_gula = ttk.Entry(form, width=30)
entry_gula.grid(row=2, column=1, pady=10)

tambah_label("BMI", 3)
entry_bmi = ttk.Entry(form, width=30)
entry_bmi.grid(row=3, column=1, pady=10)

tambah_label("Riwayat Diabetes Orang Tua", 4)

combo_ortu = ttk.Combobox(
    form,
    values=["Ya", "Tidak"],
    state="readonly",
    width=27
)
combo_ortu.grid(row=4, column=1, pady=10)


# Label hasil prediksi
label_hasil = tk.Label(
    root,
    text="Hasil prediksi akan tampil di sini",
    font=("Arial", 12, "bold"),
    bg="#f1f5f9",
    fg="#475569"
)
label_hasil.pack(pady=15)


# Tombol aplikasi
frame_tombol = tk.Frame(root, bg="#f1f5f9")
frame_tombol.pack(pady=10)

ttk.Button(
    frame_tombol,
    text="Prediksi & Simpan",
    command=simpan_pasien
).grid(row=0, column=0, padx=5)

ttk.Button(
    frame_tombol,
    text="Lihat Data",
    command=lihat_data
).grid(row=0, column=1, padx=5)

ttk.Button(
    frame_tombol,
    text="Reset",
    command=reset_form
).grid(row=0, column=2, padx=5)


# Keterangan
tk.Label(
    root,
    text="Catatan: hasil ini merupakan simulasi tugas, bukan diagnosis medis.",
    font=("Arial", 8),
    bg="#f1f5f9",
    fg="#64748b",
    wraplength=480
).pack(side="bottom", pady=15)


# Menjalankan aplikasi
root.mainloop()