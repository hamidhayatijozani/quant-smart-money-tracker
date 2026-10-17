# Quant Smart Money Tracker

**معماری جامع سیستم ردیابی، تحلیل رفتار و تولید سیگنال‌های کمّی تریدرهای برتر در صرافی‌های بین‌المللی**

سیستم صنعتی برای ردیابی و تحلیل رفتار تریدرهای برتر (Smart Money / Lead Traders) در صرافی‌های Binance، OKX و Bybit همراه با تولید سیگنال کمّی، موتور هوش مصنوعی رفتارشناس و لایه‌های ایمنی پیشرفته.

---

## وضعیت فعلی پروژه (Current Status)

| بخش                              | وضعیت              |
|----------------------------------|--------------------|
| معماری کامل                     | ✅ تکمیل شده       |
| ساختار پروژه                    | ✅ ایجاد شده       |
| Docker Compose (Kafka + ClickHouse) | ✅ آماده        |
| ماژول Safety & Idempotency      | ✅ آماده           |
| Behavioral AI Engine            | ✅ اسکلت آماده     |
| Configuration                   | ✅ آماده           |
| **Binance Collector (Leaderboard)** | ✅ پیاده‌سازی شده |
| **ClickHouse Storage + Schema** | ✅ پیاده‌سازی شده  |
| Main Discovery Loop             | ✅ متصل شده        |
| Position Streaming (واقعی)      | 🔄 نیاز به منبع داده خارجی |
| OKX / Bybit Collectors          | 🔄 بعدی            |
| Kafka Producer/Consumer         | 🔄 بعدی            |
| RL Agent                        | 🔄 برنامه‌ریزی شده |
| Dashboard                       | 🔄 برنامه‌ریزی شده |

---

## ساختار فعلی پروژه

```
quant-smart-money-tracker/
├── infrastructure/
│   └── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── main.py                     # Discovery loop + AI placeholder
│   ├── config.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── binance.py              # ✅ Leaderboard + skeleton positions
│   ├── storage/
│   │   ├── __init__.py
│   │   └── clickhouse.py           # ✅ Schema + insert methods
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   └── behavioral.py
│   └── safety/
│       ├── __init__.py
│       └── idempotency.py
├── .env.example
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

---

## راه‌اندازی سریع (Quick Start)

### ۱. کلون کردن مخزن
```bash
git clone https://github.com/hamidhayatijozani/quant-smart-money-tracker.git
cd quant-smart-money-tracker
```

### ۲. ایجاد محیط مجازی و نصب وابستگی‌ها
```bash
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
pip install -r requirements.txt
```

### ۳. تنظیم متغیرهای محیطی
```bash
cp .env.example .env
```

### ۴. راه‌اندازی زیرساخت
```bash
cd infrastructure
docker compose up -d
```

- Kafka UI → http://localhost:8080  
- ClickHouse → http://localhost:8123

### ۵. اجرای سیستم
```bash
python -m src.main
```

سیستم شروع به دریافت لیدربورد بایننس (روزانه + هفتگی) می‌کند و داده‌ها را در ClickHouse ذخیره می‌نماید.

---

## نقشه راه به‌روز

### فاز ۱ – Foundation ✅ تقریباً کامل
- [x] معماری و مستندات
- [x] ساختار + Docker
- [x] Safety & Idempotency
- [x] Behavioral AI Skeleton
- [x] Binance Leaderboard Collector
- [x] ClickHouse Schema & Storage

### فاز ۲ – Core Engine (در حال پیشرفت)
- [x] Binance Leaderboard
- [ ] Position data source (نیاز به منبع معتبر)
- [ ] Kafka integration
- [ ] OKX + Bybit collectors
- [ ] محاسبه دقیق PnL/ROI
- [ ] تولید سیگنال پایه

### فاز ۳ – Intelligence
- [ ] مدل Transformer واقعی
- [ ] RL Copy-Optimization Agent
- [ ] Multi-Source Fusion

### فاز ۴ – Production Ready
- [ ] Dashboard
- [ ] Alerting
- [ ] Backtesting
- [ ] Live execution with Shadow Mode

---

## نکات مهم

- **Position data**: API رسمی بایننس پوزیشن‌های سایر کاربران را در اختیار عموم قرار نمی‌دهد. برای production باید از منبع داده معتبر (سرویس‌های third-party یا scraper مجاز) استفاده شود.
- سیستم فعلاً در حالت **Discovery + Storage** کار می‌کند و آماده اتصال لایه‌های بعدی است.

---

**ساخته‌شده با همکاری Grok**  
https://github.com/hamidhayatijozani/quant-smart-money-tracker
