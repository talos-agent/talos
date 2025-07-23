def test_prompt_formatting():
    print("Testing prompt formatting with real Dexscreener data...")
    try:
        # Import the prompt manager and get the prompt
        from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
        from talos.utils.dexscreener import DexscreenerClient
        
        prompt_manager = FilePromptManager("src/talos/prompts")
        prompt = prompt_manager.get_prompt("yield_management")
        
        if not prompt:
            print("❌ Prompt not found")
            return False
            
        # Get real data from Dexscreener
        client = DexscreenerClient()
        talos_data = client.get_talos_data()
        arb_data = client.get_arb_data()
        
        # Calculate relative performance
        relative_performance = round(talos_data.price_change_h24 - arb_data.price_change_h24, 2)
        
        print(f"✅ TALOS Price: ${talos_data.price_usd}")
        print(f"✅ TALOS 24h Change: {talos_data.price_change_h24}%")
        print(f"✅ ARB 24h Change: {arb_data.price_change_h24}%")
        print(f"✅ Relative Performance: {relative_performance}%")
        
        # Real data for testing
        test_data = {
            "price": talos_data.price_usd,
            "change": talos_data.price_change_h24,
            "volume": talos_data.volume_h24,
            "relative_performance": relative_performance,
            "sentiment": 75.0,  # Mock sentiment for testing
            "staked_supply_percentage": 0.5,  # Mock staked supply for testing
            "ohlcv_data": '{"test": "data"}'  # Mock OHLCV for testing
        }
        
        # Format the prompt
        formatted_prompt = prompt.format(**test_data)
        
        print("\n✅ Prompt formatted successfully!")
        print("\n--- Formatted Prompt Preview ---")
        print(formatted_prompt[:800] + "..." if len(formatted_prompt) > 800 else formatted_prompt)
        print("--- End Preview ---")
        
        # Check if relative performance is included
        if "Relative Performance (T vs ARB):" in formatted_prompt:
            print("✅ Relative performance data correctly included in prompt")
        else:
            print("❌ Relative performance data not found in prompt")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing prompt formatting: {e}")
        return False

if __name__ == "__main__":
    test_prompt_formatting() 