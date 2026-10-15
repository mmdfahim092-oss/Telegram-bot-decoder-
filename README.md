# HTML Decoder Telegram Bot

Telegram-এ `.html`/`.htm` ফাইল গ্রহণ করে পরিচিত JavaScript/Base64 wrapper-গুলোকে **স্ট্যাটিকভাবে** ডিকোড করে HTML ফাইল ফেরত দেয়। ডিকোড করা JavaScript/HTML কখনো চালায় না, browser খোলে না এবং কোনো URL fetch করে না।

## সমর্থিত প্যাটার্ন

- `[{"i": 0, "d": "..."}, ...]` ধরনের index-ভিত্তিক Base64 chunk array, `_res.join('')`/`atob` wrapper-সহ।
- `var encData = '...' + '...';` ধরনের concatenated Base64 string assignment।
- একাধিক স্তর (সর্বোচ্চ 8) ধারাবাহিকভাবে খোলে।

এটি পূর্ণাঙ্গ JavaScript deobfuscator নয়; অন্য কৌশল ব্যবহার হলে ফাইল অপরিবর্তিত ফেরত যেতে পারে।

## সেটআপ

1. Telegram-এ `@BotFather` খুলে `/newbot` দিয়ে bot তৈরি করুন এবং token নিন। Token-টি কাউকে দেবেন না.
2. Python 3.10+ install করুন.
3. Project folder-এ:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Token environment variable-ээр тохируулж асаана:

```bash
export TELEGRAM_BOT_TOKEN='YOUR_BOT_TOKEN'
python bot.py
```

Windows PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
python bot.py
```

Bot চলার পর Telegram-এ bot-কে `/start` দিন এবং HTML-টি **document** হিসেবে পাঠান। 10 MB পর্যন্ত ফাইল সমর্থিত।

## ফাইলসমূহ

- `bot.py` — Telegram bot (polling)
- `decoder.py` — স্বতন্ত্র decoder logic
- `requirements.txt` — Python dependency

## নিরাপত্তা

- অপরিচিত HTML ব্রাউজারে খুলবেন না; এতে বাইরের সাইট, tracking বা ক্ষতিকর script থাকতে পারে।
- Bot-টি লোকাল/নিজের বিশ্বস্ত সার্ভারে চালান; bot token গোপন রাখুন।
- এই নমুনা ফাইল সার্ভারে স্থায়ীভাবে সংরক্ষণ করে না; অস্থায়ী directory কাজ শেষে মুছে যায়।
- চাইলে একা ব্যবহারের জন্য `bot.py`-তে Telegram user ID allowlist যোগ করুন।
