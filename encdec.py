import os
import zipfile
import shutil
import base64
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler
)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# State
CHOOSE_MODE, WAIT_FILE = range(2)

# Emoji alphabet
alphabet = [
    "\U0001f600","\U0001f603","\U0001f604","\U0001f601","\U0001f605","\U0001f923",
    "\U0001f602","\U0001f609","\U0001f60A","\U0001f61b",
]
MAX_STR_LEN = 70
OFFSET = 10

# ========== Fungsi Encrypt/Decrypt ==========

def obfuscate(var_name, file_content, iteration=50):
    b64_content = base64.b64encode(file_content.encode()).decode()
    VARIABLE_NAME = var_name * iteration
    index = 0
    code = f'{VARIABLE_NAME} = ""\n'
    for _ in range(int(len(b64_content) / OFFSET) + 1):
        _str = ''
        for char in b64_content[index:index + OFFSET]:
            byte = str(hex(ord(char)))[2:]
            if len(byte) < 2:
                byte = '0' + byte
            _str += '\\x' + str(byte)
        code += f'{VARIABLE_NAME} += "{_str}"\n'
        index += OFFSET
    code += f'exec(__import__("base64").b64decode({VARIABLE_NAME}.encode("utf-8")).decode("utf-8"))'
    return code

def encode_string(in_s, alphabet):
    from pprint import pformat
    d1 = dict(enumerate(alphabet))
    d2 = {v: k for k, v in d1.items()}
    def chunk_string(in_s, n):
        return "\n".join(
            "{}\\".format(in_s[i : i + n]) for i in range(0, len(in_s), n)
        ).rstrip("\\")
    return (
        'exec("".join(map(chr,[int("".join(str({}[i]) for i in x.split())) for x in\n'
        '"{}"\n.split("  ")])))\n'.format(
            pformat(d2),
            chunk_string(
                "  ".join(" ".join(d1[int(i)] for i in str(ord(c))) for c in in_s),
                MAX_STR_LEN,
            ),
        )
    )

def encrypt_bash(filepath):
    # Menggunakan bash-obfuscate via subprocess
    output_path = filepath + ".enc"
    try:
        subprocess.run(["bash-obfuscate", filepath, "-o", output_path], check=True)
        with open(output_path, "r", encoding="utf-8", errors="ignore") as f:
            data = "# Encrypted by K-fuscator\n# Github- https://github.com/KasRoudra/k-fuscator\n\n" + f.read()
        os.remove(output_path)
        return data
    except Exception as e:
        return None

def decrypt_bash(filepath):
    # Decrypt bash dengan ganti eval jadi echo lalu jalankan
    temp1 = filepath + ".tmp1"
    temp2 = filepath + ".tmp2"
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as in_f:
            filedata = in_f.read()
            if "eval" not in filedata:
                return None
            newdata = filedata.replace("eval", "echo")
        with open(temp1, "w", encoding="utf-8") as out_f:
            out_f.write(newdata)
        subprocess.run(["bash", temp1], stdout=open(temp2, "w"), check=True)
        with open(temp2, "r", encoding="utf-8", errors="ignore") as fin:
            hasil = "# Decrypted by K-fuscator\n# Github- https://github.com/KasRoudra/k-fuscator\n\n" + fin.read()
        os.remove(temp1)
        os.remove(temp2)
        return hasil
    except Exception as e:
        return None

# ========== Handler Bot ==========

user_mode = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1️⃣ Encrypt Bash", callback_data="encrypt_bash"),
            InlineKeyboardButton("2️⃣ Decrypt Bash", callback_data="decrypt_bash"),
        ],
        [
            InlineKeyboardButton("3️⃣ Encrypt Python Variable", callback_data="encrypt_var"),
            InlineKeyboardButton("4️⃣ Encrypt Python Emoji", callback_data="encrypt_emoji"),
        ]
    ]
    await update.message.reply_text(
        "Pilih mode yang kamu inginkan:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSE_MODE

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data
    user_id = query.from_user.id
    user_mode[user_id] = {"mode": mode}
    if mode == "encrypt_var":
        await query.edit_message_text("Kirim nama variable untuk encrypt, format: `variable_name,iteration (opsional)`\n\nContoh: `VAR,30`", parse_mode="Markdown")
        return CHOOSE_MODE
    else:
        await query.edit_message_text("Silakan kirim file atau file zip yang ingin diproses.")
        return WAIT_FILE

async def get_varname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if "," in text:
        var, iterasi = text.split(",", 1)
        iterasi = int(iterasi) if iterasi.isdigit() else 50
    else:
        var = text
        iterasi = 50
    user_mode[user_id]["varname"] = var.strip()
    user_mode[user_id]["iteration"] = iterasi
    await update.message.reply_text(f"Nama variable: `{var.strip()}`\nIteration: `{iterasi}`\n\nSekarang silakan upload file atau file zip.", parse_mode="Markdown")
    return WAIT_FILE

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    info = user_mode.get(user_id)
    if not info:
        await update.message.reply_text("Kamu belum pilih mode. Mulai dengan /start")
        return ConversationHandler.END

    # Ambil file
    file = update.message.document
    if not file:
        await update.message.reply_text("Tolong kirim file!")
        return WAIT_FILE

    filename = file.file_name
    ext = os.path.splitext(filename)[1].lower()
    tgfile = await file.get_file()
    inpath = f"temp_{user_id}_{filename}"
    await tgfile.download_to_drive(inpath)

    mode = info["mode"]

    # Proses file ZIP
    if ext == ".zip":
        outdir = f"out_{user_id}"
        os.makedirs(outdir, exist_ok=True)
        hasil_dir = f"hasil_{user_id}"
        os.makedirs(hasil_dir, exist_ok=True)
        with zipfile.ZipFile(inpath, "r") as zip_ref:
            zip_ref.extractall(outdir)
        processed = 0
        for root, dirs, files in os.walk(outdir):
            for fname in files:
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fin:
                    content = fin.read()
                if mode == "encrypt_bash":
                    hasil = encrypt_bash(fpath)
                elif mode == "decrypt_bash":
                    hasil = decrypt_bash(fpath)
                elif mode == "encrypt_var":
                    var = info.get("varname", "VAR")
                    iteration = info.get("iteration", 50)
                    hasil = obfuscate(var, content, iteration)
                elif mode == "encrypt_emoji":
                    hasil = encode_string(content, alphabet)
                else:
                    hasil = None
                if hasil:
                    with open(os.path.join(hasil_dir, fname), "w", encoding="utf-8") as fout:
                        fout.write(hasil)
                    processed += 1
        # zip hasil
        outzip = f"result_{user_id}.zip"
        with zipfile.ZipFile(outzip, "w") as zf:
            for fname in os.listdir(hasil_dir):
                zf.write(os.path.join(hasil_dir, fname), arcname=fname)
        await update.message.reply_document(document=open(outzip, "rb"), filename="processed_" + filename)
        # Bersihkan
        for p in [inpath, outzip]:
            if os.path.exists(p): os.remove(p)
        shutil.rmtree(outdir)
        shutil.rmtree(hasil_dir)
        return ConversationHandler.END

    # File tunggal
    else:
        with open(inpath, "r", encoding="utf-8", errors="ignore") as fin:
            content = fin.read()
        if mode == "encrypt_bash":
            hasil = encrypt_bash(inpath)
        elif mode == "decrypt_bash":
            hasil = decrypt_bash(inpath)
        elif mode == "encrypt_var":
            var = info.get("varname", "VAR")
            iteration = info.get("iteration", 50)
            hasil = obfuscate(var, content, iteration)
        elif mode == "encrypt_emoji":
            hasil = encode_string(content, alphabet)
        else:
            hasil = None
        if hasil:
            outfile = f"out_{user_id}.txt"
            with open(outfile, "w", encoding="utf-8") as fout:
                fout.write(hasil)
            await update.message.reply_document(document=open(outfile, "rb"), filename="processed_" + filename)
            os.remove(outfile)
        else:
            await update.message.reply_text("Gagal proses file!")
        os.remove(inpath)
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dibatalkan.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_MODE: [
                CallbackQueryHandler(choose_mode),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_varname),
            ],
            WAIT_FILE: [
                MessageHandler(filters.Document.ALL, handle_file)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("cancel", cancel))
    print("Bot jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()

