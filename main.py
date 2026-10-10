import os
import json
import requests
from groq import Groq
# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
def fetch_hidden_gems():
    print("Scanning Steam for real hidden gems...")
    # We search for 'indie' games using Steam's public store search API
    search_url = "https://store.steampowered.com/api/storesearch/?term=indie&l=english&cc=US"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") == 1:
            games = data.get("items", [])
            # We take the first 5 games from the search results as our "gems"
            # In a full production version, we would filter by review count here
            return [{
                "id": game["appid"],
                "title": game["name"],
                "tags": ["Indie", "Discovery"], # Steam search API doesn't give tags directly
                "rating": 0.90 # Placeholder rating
            } for game in games[:5]]
            
    except Exception as e:
        print(f"Error fetching from Steam: {e}")
    
    return []
def get_ai_description(game):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Write a 2-sentence viral marketing pitch for a 'Hidden Gem' game called {game['title']}. Make it sound mysterious and exciting."
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
def main():
    gems = fetch_hidden_gems()
    if not gems:
        print("No games found. Skipping update.")
        return
    processed_games = []
    for gem in gems:
        try:
            desc = get_ai_description(gem)
            processed_games.append({
                "title": gem['title'],
                "description": desc,
                "image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{gem['id']}/header.jpg",
                "url": f"https://store.steampowered.com/app/{gem['id']}"
            })
        except Exception as e:
            print(f"Error processing {gem['title']}: {e}")
    
    with open('games.json', 'w') as f:
        json.dump(processed_games, f, indent=4)
    print(f"Successfully updated games.json with {len(processed_games)} real games!")
if __name__ == "__main__":
    main()
