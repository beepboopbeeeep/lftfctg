# 🚀 راهنمای شروع سریع

این راهنما به شما کمک می‌کند تا ربات تلگرامی موزیک را به سرعت راه‌اندازی کنید.

## 📋 پیش‌نیازها

- Python 3.8+
- Telegram Bot Token (از @BotFather)
- Telegram User ID (برای دسترسی ادمین)

## 🎯 راه‌اندازی در ۳ دقیقه

### ۱. دریافت توکن ربات
1. به [@BotFather](https://t.me/BotFather) در تلگرام بروید
2. دستور `/newbot` را ارسال کنید
3. نام ربات را وارد کنید (مثلاً "Music Recognition Bot")
4. نام کاربری ربات را وارد کنید (مثلاً @MusicRecognitionBot)
5. توکن دریافتی را کپی کنید

### ۲. دریافت ID کاربری
1. به [@userinfobot](https://t.me/userinfobot) در تلگرام بروید
2. ID عددی خود را کپی کنید

### ۳. دانلود و اجرا
```bash
# دانلود پروژه
git clone https://github.com/your-username/telegram-music-bot.git
cd telegram-music-bot

# اجرای اسکریپت نصب
chmod +x setup.sh
./setup.sh

# وارد کردن اطلاعات
- Telegram Bot Token: [توکنی که کپی کردید]
- Telegram User ID: [ID عددی شما]

# شروع ربات
./start_bot.sh
```

## 🔧 تنظیمات سریع

### ویرایش توکن و ID ادمین
فایل `src/config.py` را ویرایش کنید:
```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # توکن خود را جایگزین کنید
ADMIN_USER_ID = 123456789  # ID خود را جایگزین کنید
```

### شروع ربات
```bash
# روش ۱: اسکریپت
./start_bot.sh

# روش ۲: دستی
source venv/bin/activate
python src/bot.py
```

## 🎵 استفاده از ربات

### دستورات اصلی
- `/start` - شروع ربات
- `/help` - راهنما
- `/statistics` - آمار ربات
- `/language` - تغییر زبان

### تشخیص آهنگ
1. فایل صوتی یا تصویری را به ربات ارسال کنید
2. ربات به صورت خودکار آهنگ را تشخیص می‌دهد
3. نتیجه با اطلاعات کامل نمایش داده می‌شود

### دانلود از لینک
1. لینک YouTube، Instagram، TikTok، Pinterest یا SoundCloud را ارسال کنید
2. ربات محتوا را دانلود و برای شما ارسال می‌کند

## 🌐 راه‌اندازی در سرور

### روش ۱: اسکریپت نصب سرویس
```bash
# نصب به عنوان سرویس سیستم‌عامل
sudo ./install-service.sh

# مدیریت سرویس
sudo systemctl start telegram-music-bot
sudo systemctl status telegram-music-bot
sudo systemctl stop telegram-music-bot
```

### روش ۲: Docker
```bash
# ساخت و اجرا
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f
```

### روش ۳: Google Firebase
```bash
# نصب Firebase CLI
npm install -g firebase-tools

# لاگین به Firebase
firebase login

# استقرار
firebase deploy --only functions
```

## 📊 قابلیت‌های اصلی

### ✅ پیاده‌سازی شده
- 🎵 تشخیص آهنگ از فایل‌های صوتی و تصویری
- 📥 دانلود از YouTube, Instagram, TikTok, Pinterest, SoundCloud
- 🌍 پشتیبانی از فارسی و انگلیسی
- 🔍 جستجوی اینلاین در گروه‌ها
- ✏️ ویرایش اطلاعات آهنگ
- 📊 آمار و گزارش‌گیری
- 📢 ارسال پیام همگانی توسط ادمین
- 🔧 تنظیمات پیشرفته

### 🔧 قابلیت‌های فنی
- پشتیبانی از ShazamIO برای تشخیص آهنگ
- ذخیره‌سازی داده‌ها در Firebase (اختیاری)
- مدیریت خطا و لاگ‌بندی پیشرفته
- پاکسازی خودکار فایل‌های موقت
- محدودیت نرخ درخواست برای جلوگیری از اسپم
- بهینه‌سازی برای اجرا در سرور

## 🛠️ عیب‌یابی سریع

### ربات پاسخ نمی‌دهد
1. بررسی کنید که توکن صحیح است
2. مطمئن شوید که اینترنت دارید
3. لاگ‌ها را بررسی کنید: `tail -f logs/bot.log`

### تشخیص آهنگ کار نمی‌کند
1. فایل صوتی باید حداقل ۱۰ ثانیه باشد
2. کیفیت صدا باید مناسب باشد
3. از فرمت‌های MP3, M4A, WAV, OGG استفاده کنید

### دانلود کار نمی‌کند
1. لینک را بررسی کنید (معتبر و عمومی باشد)
2. اینترنت خود را چک کنید
3. پلتفرم مورد نظر را در لیست پشتیبانی شده بررسی کنید

### خطاهای حافظه
1. فضای دیسک را بررسی کنید
2. فایل‌های موقت را پاک کنید: `rm -rf temp/*`
3. محدودیت حافظه را افزایش دهید

## 📞 پشتیبانی

- 📧 ایمیل: support@example.com
- 💬 تلگرام: @your_support_bot
- 🐛 گزارش خطا: GitHub Issues
- 📖 مستندات: [Wiki](https://github.com/your-username/telegram-music-bot/wiki)

## 🎉 موفق باشید!

ربات شما اکنون آماده است! 🎵

برای شروع:
1. به ربات در تلگرام بروید
2. دستور `/start` را ارسال کنید
3. از قابلیت‌های ربات لذت ببرید

---

⭐ اگر این پروژه برای شما مفید بود، لطفاً آن را ستاره کنید!