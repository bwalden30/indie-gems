import os
import json
import requests
import random
from groq import Groq
# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
THEMES = [
    "Atmospheric", "Roguelike", "Metroidvania", "Puzzle", 
    "Psychological Horror", "Simulation", "Pixel Art", 
    "Tactical", "Cyberpunk", "Cozy", "Surreal", "Dark Fantasy",
    "Sci-Fi", "Adventure", "RPG", "Strategy"
]
def fetch_hidden_gems():
    today_theme = random.choice(THEMES)
    print(f"Target Theme: {today_theme} 💎")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    # We define a list of search attempts from most specific to most general
    search_attempts = [
        f"{today_theme} indie", # Attempt 1: Specific theme + indie
        today_theme,           # Attempt 2: Just the theme
        "indie"                # Attempt 3: General indie fallback
    ]
    
    for attempt in search_attempts:
        print(f"Trying search term: '{attempt}'...")
        search_url = f"https://store.steampowered.com/api/storesearch/?term={attempt}&l=english&cc=US"
        
        try:
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            games = data.get("items", [])
            if games and len(games) >= 3: # Only accept if we get at least 3 games
                print(f"Success! Found {len(games)} games using '{attempt}'.")
                return [{
                    "id": game["id"],
                    "title": game["name"],
                    "tags": [today_theme, "Indie"],
                    "rating": 0.90
                } for game in games[:5]]
            else:
                print(f"Not enough games found for '{attempt}' ({len(games) if games else 0} found). Trying fallback...")
        except Exception as e:
            print(f"Error during search '{attempt}': {e}")
            
    return []
def get_ai_description(game):
    client = Groq(api_key=GROQ_API_KEY)
    theme = game['tags'][0]
    prompt = f"Write a 2-sentence viral marketing pitch for a 'Hidden Gem' game called {game['title']}. The theme is {theme}. Make it sound mysterious and exciting."
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
def main():
    gems = fetch_hidden_gems()
    if not gems:
        print("Critical Error: No games found even after fallback. Skipping update.")
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
