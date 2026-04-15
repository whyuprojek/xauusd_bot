import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np


# ===============================
# 📊 CANDLE
# ===============================
def _draw_candles(ax, df):
    for i in range(len(df)):
        o = df['open'].iloc[i]
        c = df['close'].iloc[i]
        h = df['high'].iloc[i]
        l = df['low'].iloc[i]

        color = '#22c55e' if c >= o else '#ef4444'

        ax.plot([i, i], [l, h], linewidth=1, color=color)

        ax.add_patch(
            plt.Rectangle(
                (i - 0.3, min(o, c)),
                0.6,
                abs(c - o),
                color=color
            )
        )


# ===============================
# 💰 PRICE
# ===============================
def _draw_price_line(ax, price, length):
    ax.axhline(price, color='#e11d48', linewidth=1.2)

    ax.text(
        length + 1,
        price,
        f"{price:.2f}",
        color='white',
        fontsize=9,
        bbox=dict(facecolor='#e11d48', edgecolor='none', pad=2)
    )


# ===============================
# 🔥 ZIGZAG STRUCTURE (IMPROVED)
# ===============================
def _get_zigzag(df):

    highs = df['high'].values
    lows = df['low'].values

    points = []

    for i in range(2, len(df)-2):

        if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
            points.append((i, highs[i], "H"))

        elif lows[i] < lows[i-1] and lows[i] < lows[i+1]:
            points.append((i, lows[i], "L"))

    if len(points) < 3:
        return None

    return points[-6:]  # lebih stabil


# ===============================
# 📐 BUILD CHANNEL (CORE ENGINE)
# ===============================
def _build_channel(df):

    zz = _get_zigzag(df)

    if not zz or len(zz) < 3:
        return None

    # ambil struktur terakhir valid
    for i in range(len(zz)-2):

        p1, p2, p3 = zz[i], zz[i+1], zz[i+2]

        # H-L-H → DOWN
        if p1[2] == "H" and p2[2] == "L" and p3[2] == "H":

            slope = (p3[1] - p1[1]) / (p3[0] - p1[0])
            intercept = p1[1] - slope * p1[0]

            x = np.arange(len(df))
            upper = slope * x + intercept

            offset = p2[1] - (slope * p2[0] + intercept)
            lower = upper + offset

            return {
                "upper": upper,
                "lower": lower,
                "mid": (upper + lower) / 2,
                "trend": "DOWN",
                "len": len(df)
            }

        # L-H-L → UP
        elif p1[2] == "L" and p2[2] == "H" and p3[2] == "L":

            slope = (p3[1] - p1[1]) / (p3[0] - p1[0])
            intercept = p1[1] - slope * p1[0]

            x = np.arange(len(df))
            lower = slope * x + intercept

            offset = p2[1] - (slope * p2[0] + intercept)
            upper = lower + offset

            return {
                "upper": upper,
                "lower": lower,
                "mid": (upper + lower) / 2,
                "trend": "UP",
                "len": len(df)
            }

    return None


# ===============================
# 🔥 SCALE CHANNEL → KE M5 (FIX ERROR)
# ===============================
def _scale_channel(channel, target_length):

    if not channel:
        return None

    src_len = channel["len"]

    x_old = np.linspace(0, target_length - 1, src_len)
    x_new = np.arange(target_length)

    upper = np.interp(x_new, x_old, channel["upper"])
    lower = np.interp(x_new, x_old, channel["lower"])
    mid = (upper + lower) / 2

    return {
        "upper": upper,
        "lower": lower,
        "mid": mid,
        "trend": channel["trend"]
    }


# ===============================
# 🔥 CHANNEL + CLONING
# ===============================
def _draw_cloned_channel(ax, channel, length):

    if not channel:
        return

    x = np.arange(length)

    upper = channel["upper"]
    lower = channel["lower"]
    mid = channel["mid"]

    height = np.abs(upper - lower)

    # MAIN
    ax.plot(x, upper, '--', color='white', alpha=0.9)
    ax.plot(x, lower, '--', color='white', alpha=0.9)
    ax.plot(x, mid, ':', color='white', alpha=1)

    # CLONE
    for i in range(1, 4):
        ax.plot(x, upper + height*i, '--', color='white', alpha=0.25)
        ax.plot(x, lower - height*i, '--', color='white', alpha=0.25)


# ===============================
# 🔥 BREAKOUT
# ===============================
def _detect_breakout(df, channel):

    if not channel:
        return None

    close = df['close'].iloc[-1]

    if close > channel["upper"][-1]:
        return "UP"

    if close < channel["lower"][-1]:
        return "DOWN"

    return None


# ===============================
# 🎯 MAIN
# ===============================
def generate_chart(df_m5, df_m30, df_h4, data, filename="chart.png"):

    df = df_m5.tail(120).copy()
    length = len(df)

    fig, ax = plt.subplots(figsize=(12, 6))

    # ===============================
    # 🎨 DARK MODE
    # ===============================
    ax.set_facecolor("#0b0f17")
    fig.patch.set_facecolor("#0b0f17")

    # ===============================
    # SCALE (AUTO FOCUS)
    # ===============================
    price = df['close'].iloc[-1]
    ax.set_ylim(price - 50, price + 50)

    # ===============================
    # DRAW CANDLE
    # ===============================
    _draw_candles(ax, df)

    # ===============================
    # 🔥 CHANNEL TF BESAR (FIX)
    # ===============================
    base_df = df_m30 if df_m30 is not None and not df_m30.empty else df_h4

    raw_channel = _build_channel(base_df.tail(150))
    channel = _scale_channel(raw_channel, length)

    _draw_cloned_channel(ax, channel, length)

    # ===============================
    # BREAKOUT VISUAL
    # ===============================
    breakout = _detect_breakout(df, channel)

    if breakout == "UP":
        ax.text(5, price + 20, "BREAK ↑", color='lime')

    elif breakout == "DOWN":
        ax.text(5, price - 20, "BREAK ↓", color='red')

    # ===============================
    # PRICE LINE
    # ===============================
    _draw_price_line(ax, price, length)

    # ===============================
    # STYLE
    # ===============================
    ax.set_xlim(0, length + 5)
    ax.set_xticks([])
    ax.grid(color='#1f2937', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()