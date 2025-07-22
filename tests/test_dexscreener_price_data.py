import requests
from talos.utils.dexscreener import DexscreenerClient
from talos.models.dexscreener import DexscreenerData

def test_arb_data():
    client = DexscreenerClient()
    
    print("Testing ARB data fetch...")
    try:
        arb_data = client.get_arb_data()
        print(f"✅ ARB Price: ${arb_data.price_usd}")
        print(f"✅ ARB 24h Change: {arb_data.price_change_h24}%")
        print(f"✅ ARB 24h Volume: ${arb_data.volume_h24:,.0f}")
        return arb_data
    except Exception as e:
        print(f"❌ Error fetching ARB data: {e}")
        return None

def test_talos_data():
    client = DexscreenerClient()
    
    print("\nTesting TALOS data fetch...")
    try:
        talos_data = client.get_talos_data()
        print(f"✅ TALOS Price: ${talos_data.price_usd}")
        print(f"✅ TALOS 24h Change: {talos_data.price_change_h24}%")
        print(f"✅ TALOS 24h Volume: ${talos_data.volume_h24:,.0f}")
        return talos_data
    except Exception as e:
        print(f"❌ Error fetching TALOS data: {e}")
        return None

def test_relative_performance():
    client = DexscreenerClient()
    
    print("\nTesting relative performance calculation...")
    try:
        talos_data = client.get_talos_data()
        arb_data = client.get_arb_data()
        
        relative_performance = round(talos_data.price_change_h24 - arb_data.price_change_h24, 2)
        
        print(f"✅ TALOS 24h Change: {talos_data.price_change_h24}%")
        print(f"✅ ARB 24h Change: {arb_data.price_change_h24}%")
        print(f"✅ Relative Performance (T vs ARB): {relative_performance}%")
        
        if relative_performance > 0:
            print(f"✅ TALOS is outperforming ARB by {relative_performance}%")
        else:
            print(f"✅ TALOS is underperforming ARB by {abs(relative_performance)}%")
            
        return relative_performance
    except Exception as e:
        print(f"❌ Error calculating relative performance: {e}")
        return None

if __name__ == "__main__":
    test_arb_data()
    test_talos_data()
    test_relative_performance()