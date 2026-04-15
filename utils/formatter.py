def format_market_output(data, price):
    best = data.get('best_setup')
    snr = data.get('snr_zones', {})
    
    output = [
        f"🕒 <b>PROFESSIONAL ANALYSIS XAUUSD</b>",
        f"━━━━━━━━━━━━━━━━━━",
        f"💰 <b>Harga:</b> {price:.2f} | <b>H4:</b> {data['h4_pos']}",
        f"📊 <b>Bias:</b> {data['bias']}\n",
        f"📦 <b>Zona H4 SNR (Filtered):</b>"
    ]

    for i, (uz, lz) in enumerate(snr.get('resistance', [])):
        output.append(f"⚪ RES {i+1}: {lz:.2f} – {uz:.2f}")
    for i, (uz, lz) in enumerate(snr.get('support', [])):
        output.append(f"🔴 SUP {i+1}: {lz:.2f} – {uz:.2f}")

    output.append(f"\n🎯 <b>M5 SND ZONES (Detail):</b>")
    for z in data.get('all_snd', [])[:3]:
        emoji = "🟢 BUY" if z['type'] == "BUY" else "🔴 SELL"
        output.append(f"{emoji}: {z['lz']:.2f}-{z['uz']:.2f} (Touch: {z['touch']})")

    if best:
        output.append(f"\n⭐ <b>BEST SETUP:</b>")
        output.append(f"Type: {best['type']} | Conf: {'✅' if best['confluence'] else '❌'}")
    
    output.append(f"\n🚦 <b>Status: {data['status']}</b>")
    output.append(f"🔥 <b>Confidence: {data['confidence']}%</b>")
    output.append(f"━━━━━━━━━━━━━━━━━━\n📝 <i>{data['reason']}</i>")
    
    return "\n".join(output)