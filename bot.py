import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8954705843:AAFcoC77Hfi-qhVe7NM0boAEYy2wDmGTRjw"
ADMIN_ID = 7091881591  # User ID خودت را اینجا وارد کن


def db():
    return sqlite3.connect("users.db")


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()


def is_admin(user_id):
    return user_id == ADMIN_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 🌹\n"
        "ربات آماده است."
    )


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    keyboard = [
        ["➕ افزودن User ID"],
        ["🗑 حذف User ID"],
        ["📋 لیست User IDها"],
        ["📢 ارسال تبلیغ"],
    ]

    await update.message.reply_text(
        "پنل مدیریت:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    context.user_data["action"] = "add"

    await update.message.reply_text(
        "User ID را وارد کنید:"
    )


async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    context.user_data["action"] = "remove"

    await update.message.reply_text(
        "User ID موردنظر را وارد کنید:"
    )


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()

    conn.close()

    if not users:
        await update.message.reply_text(
            "هنوز User ID ثبت نشده است."
        )
        return

    text = "📋 لیست User IDها:\n\n"

    for i, user in enumerate(users, 1):
        text += f"{i}. {user[0]}\n"

    await update.message.reply_text(text)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    context.user_data["action"] = "broadcast"

    await update.message.reply_text(
        "📢 متن تبلیغ را ارسال کنید:"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text

    if text == "➕ افزودن User ID":
        await add_user(update, context)
        return

    if text == "🗑 حذف User ID":
        await remove_user(update, context)
        return

    if text == "📋 لیست User IDها":
        await list_users(update, context)
        return

    if text == "📢 ارسال تبلیغ":
        await broadcast(update, context)
        return

    action = context.user_data.get("action")

    if action == "add":
        try:
            user_id = int(text)

            conn = db()
            cur = conn.cursor()

            cur.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
                (user_id,)
            )

            conn.commit()
            conn.close()

            context.user_data.clear()

            await update.message.reply_text(
                f"✅ User ID {user_id} ثبت شد."
            )

        except ValueError:
            await update.message.reply_text(
                "❌ User ID باید عدد باشد."
            )

    elif action == "remove":
        try:
            user_id = int(text)

            conn = db()
            cur = conn.cursor()

            cur.execute(
                "DELETE FROM users WHERE user_id = ?",
                (user_id,)
            )

            conn.commit()
            conn.close()

            context.user_data.clear()

            await update.message.reply_text(
                f"✅ User ID {user_id} حذف شد."
            )

        except ValueError:
            await update.message.reply_text(
                "❌ User ID باید عدد باشد."
            )

    elif action == "broadcast":
        conn = db()
        cur = conn.cursor()

        cur.execute("SELECT user_id FROM users")
        users = cur.fetchall()

        conn.close()

        success = 0
        failed = 0

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user[0],
                    text=text
                )
                success += 1

            except Exception:
                failed += 1

        context.user_data.clear()

        await update.message.reply_text(
            f"📢 ارسال انجام شد.\n\n"
            f"✅ موفق: {success}\n"
            f"❌ ناموفق: {failed}"
        )


def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
