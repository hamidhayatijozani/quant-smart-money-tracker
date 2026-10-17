# Quant Smart Money Tracker

**معماری جامع سیستم ردیابی، تحلیل رفتار و تولید سیگنال‌های کمّی تریدرهای برتر در صرافی‌های بین‌المللی**

سیستم صنعتی برای ردیابی و تحلیل رفتار تریدرهای برتر (Smart Money / Lead Traders) در صرافی‌های Binance، OKX و Bybit همراه با تولید سیگنال کمّی، موتور هوش مصنوعی رفتارشناس و لایه‌های ایمنی پیشرفته.

---

## وضعیت فعلی پروژه (Current Status)

| بخش                        | وضعیت          |
|---------------------------|----------------|
| معماری کامل               | ✅ تکمیل شده   |
| ساختار پروژه              | ✅ ایجاد شده   |
| Docker Compose (Kafka + ClickHouse) | ✅ آماده |
| ماژول Safety & Idempotency | ✅ اسکلت آماده |
| Behavioral AI Engine      | ✅ اسکلت آماده |
| Collectors (Base)         | ✅ آماده       |
| Configuration             | ✅ آماده       |
| Main Entry Point          | ✅ آماده       |
| Collectors واقعی (Binance/OKX/Bybit) | 🔄 در حال توسعه |
| RL Agent                  | 🔄 برنامه‌ریزی شده |
| Dashboard                 | 🔄 برنامه‌ریزی شده |

---

## ساختار فعلی پروژه

```
quant-smart-money-tracker/
├── infrastructure/
│   └── docker-compose.yml          # Kafka + Zookeeper + ClickHouse + Kafka-UI
├── src/
│   ├── __init__.py
│   ├── main.py                     # نقطه ورود اصلی
│   ├── config.py                   # تنظیمات با pydantic-settings
│   ├── collectors/
│   │   ├── __init__.py
│   │   └── base.py                 # Abstract Collector + Position/Leaderboard models
│   ├── ai_engine/
│   │   ├── __init__.py
│   │   └── behavioral.py           # Transformer + Anomaly + Trust Score
│   └── safety/
│       ├── __init__.py
│       └── idempotency.py          # ExecutionState, Maturity, Evidence Hash
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
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### ۳. تنظیم متغیرهای محیطی
```bash
cp .env.example .env
# سپس فایل .env را با کلیدهای API خود پر کنید
```

### ۴. راه‌اندازی زیرساخت (Kafka + ClickHouse)
```bash
cd infrastructure
docker compose up -d
```

- Kafka UI: http://localhost:8080
- ClickHouse: http://localhost:8123

### ۵. اجرای برنامه (اسکلت فعلی)
```bash
python -m src.main
```

---

## معماری سیستم (خلاصه)

### جریان داده
1. **Dynamic Leaderboard Discovery Engine** → پیدا کردن تریدرهای برتر
2. REST Polling + WebSocket → جمع‌آوری پوزیشن‌ها
3. **Stream Normalizer** → یکسان‌سازی داده
4. **Apache Kafka** → Event Bus
5. **ClickHouse** → ذخیره‌سازی سری زمانی با تأخیر بسیار پایین

### لایه‌های پیشرفته
- **Behavioral AI Engine**: مدل Transformer + Autoencoder برای تشخیص الگو و ناهنجاری
- **Trust Score پویا**: وزن‌دهی هوشمند به هر تریدر برتر
- **Idempotency + Shadow Mode**: جلوگیری از سفارش تکراری و تست ایمن سیگنال‌ها
- **Circuit Breaker**: محافظت در برابر سیگنال‌های انبوه مشکوک

---

## نقشه راه (Roadmap)

### فاز ۱ (فعلی) – Foundation
- [x] معماری و مستندات
- [x] ساختار پروژه + Docker
- [x] Safety & Idempotency
- [x] Behavioral AI Skeleton
- [ ] Collectors واقعی برای Binance / OKX / Bybit

### فاز ۲ – Core Engine
- [ ] Stream Normalizer + Kafka Producer/Consumer
- [ ] ذخیره در ClickHouse با schema بهینه
- [ ] محاسبه دقیق PnL/ROI
- [ ] تولید سیگنال پایه

### فاز ۳ – Intelligence
- [ ] آموزش مدل Transformer روی داده‌های واقعی
- [ ] RL Copy-Optimization Agent
- [ ] Multi-Source Fusion (On-chain + Sentiment)

### فاز ۴ – Production Ready
- [ ] Dashboard تعاملی
- [ ] سیستم هشدار چندکاناله
- [ ] Backtesting Engine
- [ ] اجرای واقعی با Shadow Mode و Risk Gates

---

## مشارکت

پروژه در مراحل اولیه توسعه است. پیشنهادها، Issue و Pull Request خوش‌آمد هستند.

---

## مجوز

MIT License – آزاد برای استفاده تجاری و غیرتجاری.

---

**ساخته‌شده با همکاری Grok**  
Repository: https://github.com/hamidhayatijozani/quant-smart-money-tracker
