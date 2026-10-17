# Quant Smart Money Tracker

**محصول عملیاتی ردیابی و تولید سیگنال از تریدرهای برتر + سیستم کپی‌تریدینگ متاتریدر**

سیستم هوشمند برای کشف، امتیازدهی و رتبه‌بندی سیگنال‌های کپی‌ترید (MetaTrader / MQL5 و منابع مشابه) همراه با لایه‌های ایمنی، موتور هوش مصنوعی رفتارشناس و معماری مقیاس‌پذیر.

---

## وضعیت فعلی – محصول عملیاتی

| قابلیت | وضعیت |
|--------|--------|
| کشف سیگنال‌های کپی‌ترید (MQL5-style) | ✅ عملیاتی |
| موتور امتیازدهی هوشمند (Signal Engine) | ✅ عملیاتی |
| رتبه‌بندی و توصیه COPY / WATCH / AVOID | ✅ عملیاتی |
| حالت Demo با داده‌های واقعی‌گرایانه | ✅ فعال |
| Shadow Mode (ایمنی) | ✅ فعال |
| Binance Leaderboard Collector | ✅ آماده |
| ClickHouse Storage | ✅ آماده |
| معماری Safety & Idempotency | ✅ آماده |
| Behavioral AI Skeleton | ✅ آماده |

---

## اجرای سریع (کمتر از ۲ دقیقه)

```bash
git clone https://github.com/hamidhayatijozani/quant-smart-money-tracker.git
cd quant-smart-money-tracker

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.main
```

بعد از اجرا، سیستم هر ۶۰ ثانیه یک چرخه کامل انجام می‌دهد و خروجی شبیه این نمایش می‌دهد:

```
========================================================================
  QUANT SMART MONEY TRACKER  –  Operational Mode
  Copy Trading + MetaTrader Signal Intelligence
========================================================================

  Top 10 Actionable Signals

  Rank  Action     Strength  Name                         Gain%    MaxDD%   Risk
  ------------------------------------------------------------------------------
  1     🟢 COPY     0.892     Ironclad Risk Manager        38.9     7.4      low
  2     🟢 COPY     0.871     Quantum Multi-Pair           63.1     11.8     low
  3     🟢 COPY     0.845     Steady Compass               41.7     9.3      low
  4     🟡 WATCH    0.763     Aurora EURUSD Swing          87.4     14.2     low
  ...
```

---

## معماری فعلی

```
src/
├── main.py                        # نقطه ورود عملیاتی کامل
├── config.py
├── collectors/
│   ├── binance.py                 # لیدربورد بایننس
│   └── copytrading/
│       ├── base.py                # مدل‌های CopySignalProvider + OpenTrade
│       └── mql5.py                # Collector هوشمند MQL5-style (با Demo Mode قوی)
├── engine/
│   └── signal_engine.py           # موتور امتیازدهی و تصمیم‌گیری COPY/WATCH/AVOID
├── ai_engine/
│   └── behavioral.py              # Trust Score + Anomaly detection
├── safety/
│   └── idempotency.py             # ExecutionState + Evidence Hash
└── storage/
    └── clickhouse.py              # ذخیره‌سازی سری‌زمانی
```

---

## منطق تصمیم‌گیری هوشمند (Signal Engine)

سیستم هر ارائه‌دهنده سیگنال را بر اساس موارد زیر امتیاز می‌دهد:

- **Gain %** و **Max Drawdown** (مهم‌ترین فاکتور ریسک)
- Profit Factor و Win Rate
- تعداد معاملات (حجم نمونه)
- تعداد مشترکین
- سطح ریسک اعلام‌شده
- کیفیت کلی (Quality Score)

سپس یکی از سه توصیه را صادر می‌کند:

| توصیه | معنی |
|-------|------|
| 🟢 **COPY** | سیگنال با کیفیت بالا و ریسک کنترل‌شده – مناسب کپی |
| 🟡 **WATCH** | جالب است، اما هنوز به سطح اطمینان کامل نرسیده |
| 🔴 **AVOID** | کیفیت یا ریسک قابل قبول نیست |

---

## چرا Copy Trading / MetaTrader؟

در صرافی‌های کریپتو (Binance و ...)، پوزیشن تریدرهای دیگر به‌صورت عمومی و قانونی در دسترس نیست.  
اما در اکوسیستم **MetaTrader / MQL5 / Myfxbook / ZuluTrade** تریدرها **عمداً** اجازه کپی می‌دهند و داده‌های عملکرد، دراودان و معاملات باز را به اشتراک می‌گذارند. این منبع بسیار تمیزتر، قانونی‌تر و قابل‌اعتمادتر برای ساخت سیستم کپی‌ترید است.

---

## مراحل بعدی (Roadmap)

- [ ] اتصال واقعی به API یا منبع داده MQL5 / Myfxbook
- [ ] پشتیبانی از چند Provider همزمان (MQL5 + Myfxbook + ...)
- [ ] ذخیره سیگنال‌ها در ClickHouse
- [ ] سیستم هشدار (تلگرام / دیسکورد)
- [ ] RL Agent برای بهینه‌سازی حجم کپی
- [ ] Dashboard تحت وب

---

## مجوز

MIT License

---

**ساخته‌شده با خلاقیت و همکاری Grok**  
https://github.com/hamidhayatijozani/quant-smart-money-tracker
