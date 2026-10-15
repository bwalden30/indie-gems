import os
import json
import requests
import random
from groq import Groq
# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# A list of high-value tags to ensure variety every day
THEMES = [
    "Atmospheric", "Roguelike", "Metroidvania", "Puzzle", 
    "Psychological Horror", "Simulation", "Pixel Art", 
    "Tactical", "Cyberpunk", "Cozy", "Surreal", "Dark Fantasy"
]
def fetch_hidden_gems():
    # Pick a random theme for today
    today_theme = random.choice(THEMES)
    print(f"Today's Theme: {today_theme} 💎")
    print(f"Scanning Steam for {today_theme} hidden gems...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    # Search for the theme + 'indie' to keep the niche focus
    search_term = f"{today_theme} indie"
    search_url = f"https://store.steampowered.com/api/storesearch/?term={search_term}&l=english&cc=US"
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        games = data.get("items", [])
        if games:
            print(f"Found {len(games)} potential gems for {today_theme}!")
            return [{
                "id": game["id"],
                "title": game["name"],
                "tags": [today_theme, "Indie"],
                "rating": 0.90
            } for game in games[:5]]
        else:
            print(f"No games found for theme: {today_theme}")
            
    except Exception as e:
        print(f"Error fetching from Steam: {e}")
    
    return []
def get_ai_description(game):
    client = Groq(api_key=GROQ_API_KEY)
    # The prompt now includes the theme for better, more tailored pitches
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
    print(f"Successfully updated games.json with {len(processed_games)} real {gems[0]['tags'][0]} games!")
if __name__ == "__main__":
    main()
