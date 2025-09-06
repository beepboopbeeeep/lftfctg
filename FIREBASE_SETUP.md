# راه‌اندازی ربات تلگرامی موزیک در Google Firebase

این راهنما به شما نشان می‌دهد که چگونه ربات تلگرامی موزیک را در Google Firebase راه‌اندازی کنید.

## پیش‌نیازها

1. **حساب Google**: شما به یک حساب Google نیاز دارید
2. **حساب GitHub**: برای کد منبع
3. **Telegram Bot Token**: از @BotFather
4. **Telegram User ID**: برای دسترسی ادمین

## مرحله 1: راه‌اندازی پروژه Firebase

### 1.1 ایجاد پروژه Firebase
1. به [Firebase Console](https://console.firebase.google.com/) بروید
2. روی "Add project" کلیک کنید
3. نام پروژه را وارد کنید (مثلاً `telegram-music-bot`)
4. Google Analytics را غیرفعال کنید (اختیاری)
5. روی "Create project" کلیک کنید

### 1.2 تنظیم Cloud Functions
1. در منوی سمت چپ، روی "Build" > "Functions" کلیک کنید
2. روی "Get started" کلیک کنید
3. بیلینگ را فعال کنید (اگر قبلاً فعال نکرده‌اید)
4. منتظر بمانید تا Cloud Functions راه‌اندازی شود

## مرحله 2: آماده‌سازی کد

### 2.1 کلون کردن ریپازیتوری
```bash
git clone https://github.com/your-username/telegram-music-bot.git
cd telegram-music-bot
```

### 2.2 نصب وابستگی‌ها
```bash
npm install -g firebase-tools
```

### 2.3 ایجاد فایل‌های Firebase
در ریشه پروژه، فایل‌های زیر را ایجاد کنید:

#### `firebase.json`
```json
{
  "functions": {
    "source": "functions",
    "runtime": "python310",
    "env": {
      "PYTHON_VERSION": "3.10"
    }
  },
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  }
}
```

#### `.firebaserc`
```json
{
  "projects": {
    "default": "your-project-id"
  }
}
```

#### `firestore.rules`
```json
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

#### `firestore.indexes.json`
```json
{
  "indexes": [
    {
      "collectionGroup": "users",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "joined_at",
          "order": "DESCENDING"
        },
        {
          "fieldPath": "is_active",
          "order": "ASCENDING"
        }
      ]
    },
    {
      "collectionGroup": "songs",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "recognized_at",
          "order": "DESCENDING"
        },
        {
          "fieldPath": "user_id",
          "order": "ASCENDING"
        }
      ]
    }
  ]
}
```

## مرحله 3: ایجاد ساختار Cloud Functions

### 3.1 ایجاد دایرکتوری functions
```bash
mkdir functions
cd functions
```

### 3.2 ایجاد فایل‌های مورد نیاز

#### `functions/main.py`
```python
import os
import json
import logging
from datetime import datetime
from flask import Request, Response
from functions_framework import http
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Import bot modules
import sys
sys.path.append('../src')
from bot import MusicBot
from config import BOT_TOKEN, ADMIN_USER_ID

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Global bot instance
bot_instance = None

def get_bot():
    """Get or create bot instance"""
    global bot_instance
    if bot_instance is None:
        bot_instance = MusicBot()
    return bot_instance

@http
def telegram_webhook(request: Request) -> Response:
    """Handle incoming Telegram updates"""
    try:
        # Get the update from Telegram
        update_data = request.get_json()
        
        if not update_data:
            return Response('No update data', status=400)
        
        # Create Update object
        update = Update.de_json(update_data, get_bot().application.bot)
        
        # Process the update
        asyncio.run(get_bot().application.process_update(update))
        
        return Response('OK', status=200)
        
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return Response(f'Error: {str(e)}', status=500)

@http
def health_check(request: Request) -> Response:
    """Health check endpoint"""
    return Response(json.dumps({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), status=200, mimetype='application/json')

@http
def setup_webhook(request: Request) -> Response:
    """Setup webhook for Telegram"""
    try:
        bot = get_bot()
        webhook_url = f"https://{os.environ['FUNCTION_REGION']}-{os.environ['GCP_PROJECT']}.cloudfunctions.net/telegram_webhook"
        
        # Set webhook
        asyncio.run(bot.application.bot.set_webhook(webhook_url))
        
        return Response(json.dumps({
            'status': 'success',
            'webhook_url': webhook_url
        }), status=200, mimetype='application/json')
        
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return Response(f'Error: {str(e)}', status=500)
```

#### `functions/requirements.txt`
```txt
functions-framework==3.*
python-telegram-bot>=20.4
shazamio>=0.6.0
yt-dlp>=2023.7.6
instaloader>=4.9.2
requests>=2.31.0
firebase-admin>=6.3.0
spotipy>=2.23.0
mutagen>=1.46.0
Pillow>=10.0.0
flask>=2.3.0
```

#### `functions/__init__.py`
```python
# Cloud Functions for Firebase
```

## مرحله 4: استقرار در Firebase

### 4.1 لاگین به Firebase
```bash
firebase login
```

### 4.2 اتصال به پروژه
```bash
firebase use your-project-id
```

### 4.3 استقرار Cloud Functions
```bash
firebase deploy --only functions
```

### 4.4 تنظیم متغیرهای محیطی
```bash
firebase functions:config:set bot.token="YOUR_BOT_TOKEN"
firebase functions:config:set admin.user_id="YOUR_USER_ID"
```

## مرحله 5: تنظیم وب‌هوک

### 5.1 دریافت URL تابع
پس از استقرار، Firebase یک URL برای تابع شما ارائه می‌دهد. آن را کپی کنید.

### 5.2 تنظیم وب‌هوک تلگرام
از طریق مرورگر یا curl:
```bash
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "YOUR_FUNCTION_URL"}'
```

یا از طریق تابع setup_webhook:
```bash
curl "YOUR_SETUP_WEBHOOK_URL"
```

## مرحله 6: تست ربات

### 6.1 تست سلامت
```bash
curl "YOUR_HEALTH_CHECK_URL"
```

### 6.2 تست ربات
1. به ربات در تلگرام بروید
2. دستور `/start` را ارسال کنید
3. بررسی کنید که ربات پاسخ می‌دهد

## مرحله 7: مانیتورینگ و لاگ‌ها

### 7.1 مشاهده لاگ‌ها
```bash
firebase functions:log
```

### 7.2 مانیتورینگ در کنسول Firebase
1. به Firebase Console بروید
2. به بخش "Build" > "Functions" بروید
3. روی تابع مورد نظر کلیک کنید
4. لاگ‌ها را در تب "Logs" مشاهده کنید

## عیب‌یابی

### مشکلات رایج

#### 1. خطای زمان اجرا (Runtime Error)
- بررسی کنید که تمام وابستگی‌ها نصب شده‌اند
- مطمئن شوید که نسخه پایتون با Firebase سازگار است
- لاگ‌ها را برای خطاهای خاص بررسی کنید

#### 2. وب‌هوک کار نمی‌کند
- بررسی کنید که URL تابع صحیح است
- مطمئن شوید که توکن ربات صحیح است
- بررسی کنید که تابع به درستی مستقر شده است

#### 3. مشکلات حافظه
- Firebase Cloud Functions محدودیت حافظه دارد
- برای عملیات سنگین، ممکن است نیاز به افزایش حافظه داشته باشید

#### 4. مشکلات شبکه
- Firebase ممکن است دسترسی به برخی سایت‌ها را محدود کند
- بررسی کنید که سرویس‌های خارجی قابل دسترسی هستند

### راه‌حل‌ها

#### افزایش حافظه و زمان اجرا
در `firebase.json`:
```json
{
  "functions": {
    "source": "functions",
    "runtime": "python310",
    "memory": "1GB",
    "timeout": "540s"
  }
}
```

#### بهینه‌سازی عملکرد
- از کشینگ استفاده کنید
- عملیات سنگین را به صورت غیرهمزمان انجام دهید
- از مدیریت خطای مناسب استفاده کنید

## هزینه‌ها

### محدودیت‌های رایگان Firebase
- 125,000 فراخوانی Cloud Functions در ماه
- 40,000 GB-ثانیه زمان CPU در ماه
- 5 GB ذخیره‌سازی Firestore در ماه
- 50,000 سند خواندن/نوشتن در روز

### تخمین هزینه برای ربات موزیک
- تشخیص آهنگ: ~1-2 ثانیه CPU
- دانلود آهنگ: ~5-10 ثانیه CPU
- ذخیره‌سازی کاربران: ~1 KB به ازای هر کاربر
- ذخیره‌سازی آهنگ‌ها: ~5 KB به ازای هر آهنگ

برای 1000 کاربر و 5000 آهنگ:
- CPU: ~10,000 ثانیه (رایگان)
- ذخیره‌سازی: ~30 MB (رایگان)
- خواندن/نوشتن: ~10,000 در روز (رایگان)

## بهینه‌سازی برای Firebase

### 1. کاهش زمان اجرا
```python
# Use caching for frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(key):
    # Cache frequently accessed data
    pass
```

### 2. مدیریت حافظه
```python
# Clean up temporary files
import os
import tempfile

def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith('tmp'):
            os.remove(os.path.join(temp_dir, file))
```

### 3. مدیریت خطا
```python
# Proper error handling
try:
    # Your code here
except Exception as e:
    logger.error(f"Error: {e}")
    # Return appropriate response
    return Response('Error occurred', status=500)
```

## نکات امنیتی

### 1. محافظت از توکن‌ها
- هرگز توکن‌ها را در کد ذخیره نکنید
- از Firebase Config برای متغیرهای محیطی استفاده کنید
- دسترسی به توکن‌ها را محدود کنید

### 2. اعتبارسنجی ورودی‌ها
```python
# Validate user input
def validate_input(user_input):
    if not user_input or len(user_input) > 1000:
        return False
    return True
```

### 3. محدودیت نرخ درخواست
```python
# Rate limiting
from datetime import datetime, timedelta
from collections import defaultdict

request_counts = defaultdict(int)
last_reset = datetime.now()

def rate_limit(user_id, max_requests=10):
    global last_reset
    now = datetime.now()
    
    # Reset counter every hour
    if (now - last_reset) > timedelta(hours=1):
        request_counts.clear()
        last_reset = now
    
    request_counts[user_id] += 1
    return request_counts[user_id] <= max_requests
```

## جمع‌بندی

راه‌اندازی ربات تلگرامی موزیک در Google Firebase یک راه حل مقیاس‌پذیر و قابل اعتماد است. با دنبال کردن این راهنما، شما می‌توانید ربات خود را در محیط ابری راه‌اندازی کنید و از مزایای زیر بهره‌مند شوید:

- مقیاس‌پذیری خودکار
- قابلیت اطمینان بالا
- مانیتورینگ و لاگ‌بندی پیشرفته
- هزینه‌های قابل پیش‌بینی
- به‌روزرسانی‌های آسان

اگر در حین راه‌اندازی با مشکلی مواجه شدید، می‌توانید از بخش عیب‌یابی استفاده کنید یا در مستندات Firebase اطلاعات بیشتری کسب کنید.