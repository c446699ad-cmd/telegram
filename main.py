import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# التوكن وآيدي المالك
BOT_TOKEN = "8901655377:AAGnOGhoTYnRVvz4bL3bLbeVXFGlX8MocQQ"
ALLOWED_USER_ID = 7073758161

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://gateway.telegram.org",
    "Referer": "https://gateway.telegram.org/auth?to=account/edit",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/137.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}

request_url = "https://gateway.telegram.org/auth/request"
MAX_REQUESTS_PER_BATCH = 1
COOLDOWN_SECONDS = 100


async def start_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق من أنك أنت فقط صاحب البوت
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("❌ عذراً، هذا البوت خاص بمالكه فقط.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ يرجى إرسال رقم الهاتف مع الأمر بشكل صحيح.\nمثال:\n`/start +9647800000000`",
            parse_mode="Markdown"
        )
        return

    phone_number = context.args[0].strip()
    await update.message.reply_text(
        f"🚀 **بدء العملية للرقم:** `{phone_number}`\nسيتم إرسال الطلبات وتحديثك بالنتائج...",
        parse_mode="Markdown"
    )

    session = requests.Session()
    request_data = {"phone": phone_number}
    batch_count = 1

    try:
        while True:
            await update.message.reply_text(f"🔄 **بدء الدفعة رقم {batch_count}**", parse_mode="Markdown")

            for i in range(1, MAX_REQUESTS_PER_BATCH + 1):
                try:
                    res1 = session.post(request_url, data=request_data, headers=headers)
                    
                    msg = (
                        f"📤 **الطلب [{i}/{MAX_REQUESTS_PER_BATCH}]**\n"
                        f"🔹 كود الحالة: `{res1.status_code}`\n"
                        f"📄 الرد: `{res1.text}`"
                    )
                    await update.message.reply_text(msg, parse_mode="Markdown")

                    if res1.status_code == 429:
                        await update.message.reply_text(
                            "⚠️ **تم اكتشاف تجاوز معدل الطلبات (429).**\nسيتم التوقف مؤقتاً لمدة 15 دقيقة...",
                            parse_mode="Markdown"
                        )
                        await asyncio.sleep(900)
                        break

                except Exception as e:
                    await update.message.reply_text(f"❌ خطأ في الاتصال: `{e}`", parse_mode="Markdown")

                if i < MAX_REQUESTS_PER_BATCH:
                    short_delay = random.uniform(3.0, 6.0)
                    await asyncio.sleep(short_delay)

            extra_delay = random.uniform(5.0, 15.0)
            total_wait = COOLDOWN_SECONDS + extra_delay
            wait_minutes = round(total_wait / 0, 1)

            await update.message.reply_text(
                f"✅ **اكتملت الدفعة رقم {batch_count}.**\nجاري الانتظار لمدة {wait_minutes} دقيقة...",
                parse_mode="Markdown"
            )
            
            await asyncio.sleep(total_wait)
            batch_count += 1

    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_process))
    
    print("🤖 البوت يعمل الآن وجاهز للاستقبال...")
    app.run_polling()
