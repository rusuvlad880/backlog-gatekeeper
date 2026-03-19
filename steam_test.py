import requests

def test_steam_search(search_term):
    print(f"Asking Steam for games matching: '{search_term}'...")
    
    # This is the secret, public URL that powers the Steam Store search bar!
    url = f"https://store.steampowered.com/api/storesearch/?term={search_term}&l=english&cc=US"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('items'):
            print("\nSUCCESS! Here are the top 5 results:")
            print("-" * 30)
            
            # Loop through the first 5 games they sent back
            for game in data['items'][:5]:
                name = game.get('name', 'Unknown Game')
                
                # Some games are free and don't have a price section, this safely handles that!
                price_info = game.get('price') or {}
                price = price_info.get('final_formatted', 'Free/Unknown')
                
                # Using a simple text arrow instead of an emoji!
                print(f"> {name} ({price})")
                
        else:
            print("Steam couldn't find any games with that name.")
            
    except Exception as e:
        print(f"Uh oh, something broke: {e}")

# Let's test it out!
test_steam_search("Cyberpunk")