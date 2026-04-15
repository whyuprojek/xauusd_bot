import matplotlib.pyplot as plt

def generate_chart(df, data, filename="chart.png"):
    plt.figure(figsize=(10, 6))
    plt.plot(df['close'].tail(50).values, color='gold', label='XAUUSD')
    
    # Draw Resistance (White) & Support (Red)
    snr = data.get('snr_zones', {})
    for uz, lz in snr.get('resistance', []):
        plt.axhline(y=lz, color='white', linestyle='--', alpha=0.6)
    for uz, lz in snr.get('support', []):
        plt.axhline(y=uz, color='red', linestyle='--', alpha=0.6)
        
    plt.title(f"XAUUSD Analysis - {data['status']}")
    plt.savefig(filename)
    plt.close()