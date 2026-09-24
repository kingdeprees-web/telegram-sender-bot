import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8954705843:AAHe0Art-IUDpzWysRnPoQyiYps0Jk2y324"

# ساخت دیتابیس
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")

conn.commit()
conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO users (id, username, first_name) VALUES (?, ?, ?)",
        (user.id, user.username, user.first_name)
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"سلام {user.first_name} 🌹\n"
        "به ربات خوش آمدید."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
