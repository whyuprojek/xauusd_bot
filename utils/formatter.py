def format_market_output(data, price):

    sup = data.get("nearest_support")
    res = data.get("nearest_resistance")
    target = data.get("next_target")
    status = data.get("status", "WAIT")
    reason = data.get("reason", "")
    m30 = data.get("m30_pos", "-")
    setup = data.get("setup")

    h4_up = data.get("h4_break_up")
    h4_down = data.get("h4_break_down")

    output = []

    # ===============================
    # HEADER
    # ===============================
    output.append("🕒 <b>Developer Wahyu-Project</b>")
    output.append("━━━━━━━━━━━━━━━━━━")
    output.append(f"💰 <b>Harga:</b> {price:.2f}")

    # ===============================
    # STRUCTURE (SNR USER)
    # ===============================
    output.append("\n📊 <b>STRUKTUR SNR:</b>")

    if res:
        output.append(f"🔴 Resistance: {res:.2f}")
    else:
        output.append("🔴 Resistance: -")

    if sup:
        output.append(f"🟢 Support: {sup:.2f}")
    else:
        output.append("🟢 Support: -")

    if sup and res:
        output.append(f"<i>Harga berada di antara {sup:.2f} - {res:.2f}</i>")

    # ===============================
    # H4 VALIDATION (IMPORTANT)
    # ===============================
    output.append("\n📊 <b>H4 CLOSE:</b>")

    if h4_up:
        output.append(f"✅ Break VALID ke atas")
        if target:
            output.append(f"🎯 Target berikutnya: {target}")

    elif h4_down:
        output.append(f"🔻 Break VALID ke bawah")
        if target:
            output.append(f"🎯 Target berikutnya: {target}")

    else:
        output.append("⏳ Belum ada konfirmasi close H4")

    # ===============================
    # M30 POSITION
    # ===============================
    output.append("\n📏 <b>M30 CHANNEL:</b>")
    output.append(f"Posisi: {m30}")

    # ===============================
    # SND
    # ===============================
    output.append("\n📦 <b>M5 SND:</b>")

    if setup:
        if setup["type"] == "BUY":
            output.append(f"🟢 B-R-B: {setup['lz']:.2f} - {setup['uz']:.2f}")
        else:
            output.append(f"🔴 R-B-R: {setup['lz']:.2f} - {setup['uz']:.2f}")
    else:
        output.append("<i>Belum ada SND valid</i>")

    # ===============================
    # STATUS
    # ===============================
    output.append(f"\n🚦 <b>STATUS:</b> {status}")

    # ===============================
    # ANALISIS (GAYA KAMU)
    # ===============================
    output.append("━━━━━━━━━━━━━━━━━━")
    output.append("📝 <b>ANALISIS:</b>")

    if h4_up and target:
        text = f"Harga sudah CLOSE H4 di atas resistance. Potensi lanjut ke {target}."
    elif h4_down and target:
        text = f"Harga sudah CLOSE H4 di bawah support. Potensi turun ke {target}."
    elif sup and res:
        text = f"Harga masih bergerak di antara {sup:.2f} dan {res:.2f}. Tunggu konfirmasi close H4 atau SND di area SNR."
    else:
        text = reason

    output.append(f"<i>{text}</i>")

    return "\n".join(output)