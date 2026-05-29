========================================
  SIP IVR Platform - كيفاش تثبت (Windows)
========================================

هاد المجلد كامل خاصو يوصل لـ:
  C:\Users\klare\Desktop\WORKING

Cloud Agent ما يقدرش يكتب مباشرة على C:\ ديالك.
دير واحد من هاد الطرق:

--- طريقة 1: Copy يدوي ---
1. نزل branch من GitHub:
   https://github.com/davvidx9/DAVIDV2/tree/cursor/sip-ivr-windows-4feb
2. انسخ مجلد WORKING كامل لـ Desktop\WORKING

--- طريقة 2: Git ---
  cd C:\Users\klare\Desktop
  git clone https://github.com/davvidx9/DAVIDV2.git
  cd DAVIDV2
  git checkout cursor/sip-ivr-windows-4feb
  xcopy /E /I WORKING C:\Users\klare\Desktop\WORKING

--- طريقة 3: من Cursor على PC ---
  File > Save Workspace As > C:\Users\klare\Desktop\WORKING

========================================
  التشغيل السريع
========================================
1. ثبت Docker Desktop
2. داخل WORKING:
   - انسخ .env.example إلى .env
   - عمر SIP_* و TELEGRAM_BOT_TOKEN
   - عدّل asterisk\pjsip.conf
3. دبل كليك: START_WINDOWS.bat
   ولا PowerShell: .\install.ps1

Telegram: /start  /redeem KEY  /call رقم شركة اسم 4

========================================
  ملفات المشروع
========================================
  telegram_bot.py   = بوت Telegram
  api.py            = Flask + ARI
  sip_call_manager.py = مكالمات SIP
  call_flows.py     = منطق IVR
  asterisk\         = إعدادات Asterisk
  docker-compose.yml

⚠️ بدّل أي tokens قديمة (Telegram/Mongo) إلا كانت مكشوفة.
