````markdown
# Telegram Bot enc-decrypt

Bot Telegram untuk **encrypt/decrypt file Bash dan Python**,  
dengan fitur:
- **Encrypt Bash script** (`bash-obfuscate`)
- **Decrypt Bash script** (ganti `eval` ke `echo`)
- **Encrypt Python ke Variable base64**
- **Encrypt Python ke Emoji**
- Bisa file satuan **atau** ZIP (proses semua file di dalam ZIP!)
- Semua pilihan pakai tombol (inline button) di Telegram

---

## Fitur Utama

- **User-friendly**: pilih menu via tombol, langsung upload file.
- **Multiple file**: upload ZIP, bot otomatis ekstrak & proses semua file di dalamnya.
- **Auto bersih**: file sementara akan dihapus otomatis setelah proses selesai.

---

## Instalasi

### 1. **Clone / Download Project**

```bash
git clone https://github.com/nama-repo-anda/k-fuscator-telegram-bot.git
cd k-fuscator-telegram-bot
````

*Atau cukup download semua file di satu folder.*

### 2. **Install Python dependencies**

Pastikan sudah pakai Python 3.8+

```bash
pip install -r requirements.txt
```

### 3. **Install NodeJS & bash-obfuscate**

> **bash-obfuscate** dibutuhkan untuk fitur encrypt Bash.

```bash
npm install -g bash-obfuscate
```

Cek sukses install:

```bash
bash-obfuscate --help
```

### 4. **Set token Bot di .env**

Buat file `.env` di folder ini, isi:

```
TELEGRAM_TOKEN=isi_token_bot_anda
```

---

## Penggunaan

Jalankan bot:

```bash
python endec.py
```

* **/start** di chat ke bot Telegram kamu.
* Pilih menu (pakai tombol).
* Upload file yang mau diproses (.sh, .py, atau .zip).
* Hasil proses otomatis dikirimkan kembali oleh bot.

---

## File

* **endec.py** — source code utama bot Telegram.
* **requirements.txt** — kebutuhan python.
* **package.json** (opsional) — untuk install bash-obfuscate via npm jika ingin via file, tapi lebih mudah via `npm install -g bash-obfuscate`.
* **.env** — file rahasia berisi token (tidak perlu diupload ke github).

---

## Catatan Penting

* Fitur **Encrypt/Decrypt Bash** hanya bisa jalan jika `bash-obfuscate` sudah terinstall di sistem.
* Bot akan **membersihkan file sementara** secara otomatis setelah tiap proses.
* Untuk encrypt python ke variable, kamu bisa set nama variable dan jumlah iteration saat diminta (contoh: `VAR,30`).

---

## Lisensi

Bot ini berdasarkan kode [KasRoudra/k-fuscator](https://github.com/KasRoudra/k-fuscator).
Silakan modifikasi sesuai kebutuhan pribadi.

---

## Kontribusi

PR dan ide baru silakan dibuka atau kontak admin repo.

---

```
