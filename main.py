import logging
import requests
import uuid
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- LOG AYARLARI ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DURUMLAR ---
KEY, LIMIT = range(2)

# --- AYARLAR ---
TOKEN = "8613187790:AAEqE8FVwIJgHF056TrxnWES-VJQLcSjv80"
API_URL = "https://venomkey.com/connect"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 **Venom Limit Arttırıcı Bot**\nLütfen işlem yapılacak **Key** değerini gönder:")
    return KEY

async def get_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['key'] = update.message.text
    await update.message.reply_text(f"🔑 Key: `{update.message.text}`\n\nKaç cihaz girişi yapılsın? (Örn: 8 yazarsan 8 kere giriş basar):")
    return LIMIT

async def get_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_limit = update.message.text
    user_key = context.user_data['key']
    
    if not target_limit.isdigit():
        await update.message.reply_text("❌ Lütfen sadece sayı girin!")
        return LIMIT

    target_count = int(target_limit)
    await update.message.reply_text(f"⚙️ {target_count} cihaz girişi basılıyor, lütfen bekleyin...")

    headers = {
        'User-Agent': 'RIYAZVIP', # KeyAuth.hpp dosyasındaki User-Agent
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    success_count = 0
    for i in range(target_count):
        # Her seferinde farklı bir serial (UUID) göndererek farklı cihaz gibi gösteriyoruz
        device_serial = str(uuid.uuid4())
        
        payload = {
            "game": "PUBG", # HPP dosyasındaki oyun parametresi
            "user_key": user_key,
            "serial": device_serial
        }

        try:
            # Döngü içinde her seferinde siteye 'giriş' isteği atıyoruz
            response = requests.post(API_URL, data=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                success_count += 1
            
            # Siteyi yormamak için kısa bir bekleme
            await asyncio.sleep(0.5) 
        except Exception:
            continue

    # Sonuç mesajı ve limit uyarısı
    uyari = ""
    if success_count >= 9:
        uyari = "\n\n⚠️ **DİKKAT:** Key limiti dolmak üzere (Sınır 10)!"

    await update.message.reply_text(
        f"✅ **İşlem Tamamlandı!**\n\n"
        f"🔑 Key: `{user_key}`\n"
        f"📱 Başarıyla basılan giriş: `{success_count}`"
        f"{uyari}"
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ İşlem iptal edildi.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_key)],
            LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_limit)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conv_handler)
    print("--- Bot Başlatıldı ---")
    app.run_polling()

if __name__ == '__main__':
    main()
  

