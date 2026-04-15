import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np


# ===============================
# 📊 CANDLE STYLE (LEBIH TV)
# ===============================
def _draw_candles(ax, df):
    for i in range(len(df)):
        o = df['open'].iloc[i]
        c = df['close'].iloc[i]
        h = df['high'].iloc[i]
        l = df['low'].iloc[i]

        color = '#22c55e' if c >= o else '#ef4444'

        # wick
        ax.plot([i, i], [l, h], linewidth=1, color=color, zorder=2)

        # body
        ax.add_patch(
            plt.Rectangle(
                (i - 0.3, min(o, c)),
                0.6,
                abs(c - o),
                color=color,
                zorder=3
            )
        )


# ===============================
# 🔴 SNR SMART FILTER
# ===============================
def _draw_snr(ax, data):
    levels = data.get("all_snr", [])
    price = data.get("price")

    if not levels or price is None:
        return

    # 🔥 hanya ambil dekat harga
    filtered = [lvl for lvl in levels if abs(lvl - price) <= 120]

    for lvl in filtered:
        ax.axhline(lvl, linestyle='--', linewidth=1, alpha=0.4, color='#94a3b8')

        ax.text(
            len(filtered) + 2,
            lvl,
            f"{lvl:.2f}",
            color='#cbd5f5',
            fontsize=8,
            verticalalignment='center'
        )


# ===============================
# 🔵 RANGE AKTIF
# ===============================
def _highlight_active_range(ax, data, length):
    sup = data.get("nearest_support")
    res = data.get("nearest_resistance")

    if sup and res:
        ax.fill_between(
            range(length),
            sup,
            res,
            color='#2563eb',
            alpha=0.08
        )


# ===============================
# 📦 SND ZONE
# ===============================
def _draw_snd(ax, data, length):
    setup = data.get("setup")
    if not setup:
        return

    lz = setup['lz']
    uz = setup['uz']
    color = '#22c55e' if setup['type'] == "BUY" else '#ef4444'

    ax.fill_between(
        range(length),
        lz,
        uz,
        color=color,
        alpha=0.25
    )


# ===============================
# 💰 PRICE LINE (TRADINGVIEW STYLE)
# ===============================
def _draw_price_line(ax, price, length):
    ax.axhline(price, linewidth=1.2, color='#e11d48')

    ax.text(
        length + 1,
        price,
        f" {price:.2f}",
        color='white',
        fontsize=9,
        verticalalignment='center',
        bbox=dict(facecolor='#e11d48', edgecolor='none', pad=2)
    )


# ===============================
# 📐 CHANNEL LEBIH MIRIP MANUAL
# ===============================
def _draw_channel(ax, df):
    if len(df) < 30:
        return

    x = np.arange(len(df))
    highs = df['high'].values
    lows = df['low'].values

    # ambil swing
    high_idx = np.argmax(highs[-40:])
    low_idx = np.argmin(lows[-40:])

    high_val = highs[-40:][high_idx]
    low_val = lows[-40:][low_idx]

    slope = (df['close'].iloc[-1] - df['close'].iloc[0]) / len(df)
    base = slope * x + df['close'].iloc[0]

    upper = base + (high_val - base.max())
    lower = base - (base.min() - low_val)

    ax.plot(x, base, color='white', linewidth=1)
    ax.plot(x, upper, color='white', linestyle='--', alpha=0.6)
    ax.plot(x, lower, color='white', linestyle='--', alpha=0.6)


# ===============================
# 🎯 MAIN GENERATE
# ===============================
def generate_chart(df, data, filename="chart.png"):

    df = df.tail(120).copy()
    length = len(df)

    fig, ax = plt.subplots(figsize=(12, 6))

    # ===============================
    # 🎨 DARK MODE
    # ===============================
    ax.set_facecolor("#0b0f17")
    fig.patch.set_facecolor("#0b0f17")

    for spine in ax.spines.values():
        spine.set_color('#1f2937')

    ax.tick_params(colors='#9ca3af')

    # ===============================
    # 🔥 AUTO SCALE (INI FIX UTAMA)
    # ===============================
    high = df['high'].max()
    low = df['low'].min()

    ax.set_ylim(low - 5, high + 5)

    ax.margins(x=0)

    # ===============================
    # DRAW
    # ===============================
    _draw_candles(ax, df)
    _draw_snr(ax, data)
    _highlight_active_range(ax, data, length)
    _draw_snd(ax, data, length)
    _draw_channel(ax, df)

    price = df['close'].iloc[-1]
    _draw_price_line(ax, price, length)

    # ===============================
    # STYLE
    # ===============================
    ax.set_title(f"XAUUSD | {price:.2f}", color='white')

    ax.set_xlim(0, length + 5)
    ax.set_xticks([])

    ax.grid(color='#1f2937', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()