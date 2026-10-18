"""
Quant Smart Money Tracker - Web Application
Beautiful, mobile-friendly dashboard for Copy Trading signals.
"""

import streamlit as st
import asyncio
from datetime import datetime
import pandas as pd

# Import project modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.copytrading import MQL5Collector
from src.engine import SignalEngine

# Page config
st.set_page_config(
    page_title="Quant Smart Money Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better mobile experience
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .signal-card {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border: 1px solid #e0e0e0;
    }
    .copy-badge {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .watch-badge {
        background-color: #ffc107;
        color: #333;
        padding: 0.2rem 0.6rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .avoid-badge {
        background-color: #dc3545;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .metric-box {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def get_signals(min_gain: float, max_dd: float, min_trades: int, top_n: int):
    """Fetch and rank signals (sync wrapper)."""
    collector = MQL5Collector(demo_mode=True)
    engine = SignalEngine()

    async def _run():
        providers = await collector.fetch_top_providers(
            min_gain=min_gain,
            max_drawdown=max_dd,
            min_trades=min_trades,
            limit=30,
        )
        return engine.rank_signals(providers, top_n=top_n)

    return asyncio.run(_run())


def main():
    # Header
    st.markdown('<div class="main-header">📈 Quant Smart Money Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">سیستم هوشمند کشف و رتبه‌بندی سیگنال‌های کپی‌ترید (MetaTrader / MQL5)</div>', unsafe_allow_html=True)

    # Sidebar filters
    with st.sidebar:
        st.header("⚙️ فیلترها")
        min_gain = st.slider("حداقل سود (%)", 0.0, 100.0, 20.0, 5.0)
        max_dd = st.slider("حداکثر دراودان (%)", 5.0, 50.0, 28.0, 1.0)
        min_trades = st.number_input("حداقل تعداد معاملات", 10, 500, 80, 10)
        top_n = st.slider("تعداد سیگنال‌های برتر", 5, 20, 10)

        st.markdown("---")
        st.markdown("**وضعیت سیستم**")
        st.success("🟢 Demo Mode فعال")
        st.info("🛡️ Shadow Mode فعال")
        st.caption(f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")

        if st.button("🔄 به‌روزرسانی سیگنال‌ها", use_container_width=True):
            st.cache_data.clear()

    # Main content
    with st.spinner("در حال دریافت و رتبه‌بندی سیگنال‌ها..."):
        try:
            signals = get_signals(min_gain, max_dd, min_trades, top_n)
        except Exception as e:
            st.error(f"خطا در دریافت سیگنال‌ها: {e}")
            return

    if not signals:
        st.warning("هیچ سیگنالی با فیلترهای فعلی پیدا نشد. فیلترها را کمی بازتر کنید.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    copy_count = sum(1 for s in signals if s.recommended_action == "COPY")
    watch_count = sum(1 for s in signals if s.recommended_action == "WATCH")
    avoid_count = sum(1 for s in signals if s.recommended_action == "AVOID")
    avg_strength = sum(s.strength for s in signals) / len(signals)

    col1.metric("🟢 COPY", copy_count)
    col2.metric("🟡 WATCH", watch_count)
    col3.metric("🔴 AVOID", avoid_count)
    col4.metric("میانگین قدرت", f"{avg_strength:.2f}")

    st.markdown("---")

    # Signals table
    st.subheader("🏆 سیگنال‌های رتبه‌بندی شده")

    # Prepare dataframe
    data = []
    for i, s in enumerate(signals, 1):
        action_emoji = {"COPY": "🟢 COPY", "WATCH": "🟡 WATCH", "AVOID": "🔴 AVOID"}.get(
            s.recommended_action, s.recommended_action
        )
        data.append({
            "رتبه": i,
            "توصیه": action_emoji,
            "قدرت": round(s.strength, 3),
            "نام سیگنال": s.name,
            "سود %": round(s.gain_percent, 1),
            "دراودان %": round(s.max_drawdown, 1),
            "ریسک": s.risk_level,
            "مشترکین": s.subscribers,
        })

    df = pd.DataFrame(data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "قدرت": st.column_config.ProgressColumn(
                "قدرت",
                help="قدرت سیگنال از 0 تا 1",
                min_value=0,
                max_value=1,
            ),
        }
    )

    st.markdown("---")

    # Detailed cards for top signals
    st.subheader("📋 جزئیات سیگنال‌های برتر")

    for i, s in enumerate(signals[:5], 1):
        with st.expander(f"#{i}  {s.name}  —  {s.recommended_action}", expanded=(i <= 2)):
            c1, c2, c3 = st.columns(3)
            c1.metric("قدرت سیگنال", f"{s.strength:.3f}")
            c2.metric("سود کل", f"{s.gain_percent:.1f}%")
            c3.metric("حداکثر دراودان", f"{s.max_drawdown:.1f}%")

            st.markdown(f"**سطح ریسک:** `{s.risk_level}`  |  **تعداد مشترکین:** `{s.subscribers}`")
            st.markdown("**دلایل امتیازدهی:**")
            for reason in s.reasoning:
                st.markdown(f"- {reason}")

            if s.recommended_action == "COPY":
                st.success("این سیگنال برای کپی کردن توصیه می‌شود (در حالت Shadow Mode).")
            elif s.recommended_action == "WATCH":
                st.warning("این سیگنال را زیر نظر بگیرید.")
            else:
                st.error("این سیگنال توصیه نمی‌شود.")

    # Footer
    st.markdown("---")
    st.caption("Quant Smart Money Tracker • ساخته‌شده با Grok • حالت Demo فعال است")


if __name__ == "__main__":
    main()
