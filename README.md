# 🎵 Telegram Music Bot

یک ربات تلگرامی پیشرفته برای تشخیص و دانلود موزیک با استفاده از ShazamIO

## 🌟 ویژگی‌ها

### قابلیت‌های اصلی
- 🎵 **تشخیص آهنگ** از فایل‌های صوتی و تصویری
- 📥 **دانلود موزیک** از پلتفرم‌های مختلف
- 🌍 **پشتیبانی از چند زبان** (فارسی و انگلیسی)
- 🔍 **جستجوی اینلاین** در گروه‌ها و کانال‌ها
- ✏️ **ویرایش اطلاعات آهنگ**
- 📊 **آمار و گزارش‌گیری**
- 📢 **ارسال پیام همگانی** توسط ادمین

### پلتفرم‌های پشتیبانی شده
- **YouTube** - دانلود ویدیو و صدا
- **Instagram** - دانلود پست‌ها و ریلز
- **TikTok** - دانلود ویدیوها
- **Pinterest** - دانلود پین‌ها
- **SoundCloud** - دانلود موزیک

### قابلیت‌های ShazamIO
- تشخیص آهنگ از فایل‌های صوتی
- جستجوی آهنگ و هنرمند
- دریافت اطلاعات کامل آهنگ
- دریافت آهنگ‌های مشابه
- دریافت برترین آهنگ‌ها بر اساس کشور و شهر
- دریافت آمار شنیداری آهنگ‌ها

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.8+
- Telegram Bot Token (از @BotFather)
- حساب کاربری تلگرام (برای دسترسی ادمین)

### راه‌اندازی سریع
1. ریپازیتوری را کلون کنید:
```bash
git clone https://github.com/your-username/telegram-music-bot.git
cd telegram-music-bot
```

2. اسکریپت نصب را اجرا کنید:
```bash
chmod +x setup.sh
./setup.sh
```

3. اطلاعات مورد نیاز را وارد کنید:
   - Telegram Bot Token
   - Telegram User ID

4. ربات را شروع کنید:
```bash
./start_bot.sh
```

### راه‌اندازی دستی
1. وابستگی‌های سیستم را نصب کنید:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv ffmpeg git

# CentOS/RHEL
sudo yum install python3 python3-pip ffmpeg git

# macOS
brew install python3 ffmpeg git
```

2. محیط مجازی را ایجاد کنید:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. وابستگی‌های پایتون را نصب کنید:
```bash
pip install -r requirements.txt
```

4. توکن ربات و ID ادمین را در `src/config.py` تنظیم کنید:
```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
ADMIN_USER_ID = 123456789  # Replace with your user ID
```

5. ربات را اجرا کنید:
```bash
python src/bot.py
```

## 🔧 تنظیمات

### تنظیمات اصلی
فایل `src/config.py` شامل تمام تنظیمات ربات است:

```python
# Bot Configuration
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
ADMIN_USER_ID = 123456789

# Firebase Configuration (اختیاری)
FIREBASE_CREDENTIALS_PATH = "config/firebase-credentials.json"
FIREBASE_DATABASE_URL = "https://your-project.firebaseio.com"

# Download Configuration
DOWNLOAD_TIMEOUT = 300
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### تنظیمات Firebase (اختیاری)
برای استفاده از Firebase برای ذخیره‌سازی داده‌ها:

1. پروژه Firebase ایجاد کنید
2. فایل اعتبارنامه را در `config/firebase-credentials.json` قرار دهید
3. تنظیمات را در `src/config.py` به‌روز کنید

## 📱 استفاده از ربات

### دستورات اصلی
- `/start` - شروع ربات و نمایش منوی اصلی
- `/help` - نمایش راهنما
- `/statistics` - نمایش آمار ربات
- `/language` - تغییر زبان
- `/broadcast` - ارسال پیام همگانی (فقط ادمین)

### تشخیص آهنگ
1. فایل صوتی یا تصویری را برای ربات ارسال کنید
2. ربات به صورت خودکار آهنگ را تشخیص می‌دهد
3. نتیجه به همراه اطلاعات کامل آهنگ نمایش داده می‌شود

### دانلود از لینک
1. لینک YouTube، Instagram، TikTok، Pinterest یا SoundCloud را ارسال کنید
2. ربات محتوا را دانلود و برای شما ارسال می‌کند

### جستجوی اینلاین
در هر گروه یا کانالی:
- `@bot_username نام آهنگ` را تایپ کنید
- نتایج جستجو به صورت اینلاین نمایش داده می‌شود

### ویرایش اطلاعات آهنگ
1. از منوی اصلی گزینه "Edit Song Info" را انتخاب کنید
2. فایل آهنگ را ارسال کنید
3. اطلاعات جدید را در قالب مشخص شده وارد کنید

## 🌐 راه‌اندازی در Google Firebase

برای راه‌اندازی در Google Firebase، به فایل `FIREBASE_SETUP.md` مراجعه کنید.

## 📊 ساختار پروژه

```
telegram-music-bot/
├── src/
│   ├── bot.py                 # فایل اصلی ربات
│   ├── config.py              # تنظیمات ربات
│   ├── handlers/              # هندلرهای ربات
│   ├── services/              # سرویس‌های اصلی
│   │   ├── song_recognizer.py # تشخیص آهنگ
│   │   ├── downloader.py      # دانلودر
│   │   └── firebase_service.py # سرویس فایربیس
│   ├── models/                # مدل‌های داده
│   │   ├── user.py            # مدل کاربر
│   │   └── song.py            # مدل آهنگ
│   └── utils/                 # توابع کمکی
│       └── helpers.py
├── downloads/                # فایل‌های دانلود شده
├── temp/                      # فایل‌های موقت
├── logs/                      # لاگ‌ها
├── config/                    # تنظیمات
├── requirements.txt           # وابستگی‌های پایتون
├── setup.sh                   # اسکریپت نصب
├── start_bot.sh               # اسکریپت اجرا
└── README.md                  # این فایل
```

## 🔧 عیب‌یابی

### مشکلات رایج

#### 1. ربات پاسخ نمی‌دهد
- بررسی کنید که توکن ربات صحیح است
- مطمئن شوید که ربات در حال اجراست
- لاگ‌ها را برای خطا بررسی کنید

#### 2. تشخیص آهنگ کار نمی‌کند
- مطمئن شوید که فایل صوتی باکیفیت است
- بررسی کنید که فایل حداکثر حجم مجاز را ندارد
- از فرمت‌های پشتیبانی شده استفاده کنید

#### 3. دانلود کار نمی‌کند
- بررسی کنید که اینترنت شما پایدار است
- مطمئن شوید که لینک معتبر است
- بررسی کنید که پلتفرم مورد نظر پشتیبانی می‌شود

#### 4. خطاهای Firebase
- بررسی کنید که فایل اعتبارنامه صحیح است
- مطمئن شوید که پروژه Firebase فعال است
- بررسی کنید که قوانین Firestore صحیح تنظیم شده‌اند

### لاگ‌ها
برای مشاهده لاگ‌ها:
```bash
# محلی
tail -f logs/bot.log

# سیستم‌دی
sudo journalctl -u telegram-music-bot -f

# Firebase
firebase functions:log
```

## 📈 آمار و گزارش‌گیری

ربات آمارهای زیر را جمع‌آوری می‌کند:
- تعداد کل کاربران
- تعداد آهنگ‌های تشخیص داده شده
- تعداد آهنگ‌های دانلود شده
- وضعیت فعلی ربات
- زمان پاسخ‌دهی ربات

برای مشاهده آمار:
```
/statistics
```

## 🛡️ امنیت

### نکات امنیتی
- هرگز توکن ربات را در دسترس عمومی قرار ندهید
- از رمزهای عبور قوی برای Firebase استفاده کنید
- دسترسی ادمین را محدود کنید
- به‌طور منظم لاگ‌ها را بررسی کنید

### محافظت از داده‌ها
- اطلاعات کاربران به صورت امن ذخیره می‌شوند
- فایل‌های موقت به صورت خودکار حذف می‌شوند
- دسترسی به Firebase با قوانین سخت‌گیرانه محافظت می‌شود

## 🤝 مشارکت

ما از مشارکت‌ها استقبال می‌کنیم! لطفاً قبل از ارسال Pull Request:

1. ریپازیتوری را فورک کنید
2. یک شاخه جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
3. تغییرات خود را اعمال کنید (`git commit -m 'Add amazing feature'`)
4. شاخه را پوش کنید (`git push origin feature/amazing-feature`)
5. یک Pull Request ایجاد کنید

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای اطلاعات بیشتر، فایل [LICENSE](LICENSE) را مطالعه کنید.

## 🙏 تشکرها

- [ShazamIO](https://github.com/shazamio/ShazamIO) برای تشخیص آهنگ
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) برای API تلگرام
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) برای دانلود از یوتیوب
- [Firebase](https://firebase.google.com/) برای ذخیره‌سازی ابری

## 📞 پشتیبانی

اگر سوال یا مشکلی دارید:
- یک Issue در GitHub ایجاد کنید
- به [مستندات](https://github.com/your-username/telegram-music-bot/wiki) مراجعه کنید
- با ادمین تماس بگیرید

---

⭐ اگر این پروژه برای شما مفید بود، لطفاً آن را ستاره کنید!