import os
import json
import requests
import random
from groq import Groq
# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Expanded list of themes for maximum variety
THEMES = [
    "Atmospheric", "Roguelike", "Metroidvania", "Puzzle", 
    "Psychological Horror", "Simulation", "Pixel Art", 
    "Tactical", "Cyberpunk", "Cozy", "Surreal", "Dark Fantasy",
    "Sci-Fi", "Adventure", "RPG", "Strategy", "Stealth", "Deckbuilder"
]
def fetch_single_theme_gems(theme, count=2):
    """Helper to fetch a few games for a specific theme."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    search_url = f"https://store.steampowered.com/api/storesearch/?term={theme} indie&l=english&cc=US"
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        
        return [{
            "id": item["id"],
            "title": item["name"],
            "theme": theme
        } for item in items[:count]]
    except Exception as e:
        print(f"Error fetching {theme}: {e}")
        return []
def fetch_diverse_gems():
    print("🎲 Generating Today's Variety Pack...")
    
    # 1. Pick 4 random themes for today
    selected_themes = random.sample(THEMES, 4)
    print(f"Today's Themes: {', '.join(selected_themes)}")
    
    all_gems = []
    seen_ids = set()
    # 2. Collect gems from each theme
    for theme in selected_themes:
        gems = fetch_single_theme_gems(theme, count=3)
        for g in gems:
            if g["id"] not in seen_ids:
                all_gems.append(g)
                seen_ids.add(g["id"])
    # 3. Fallback: If we have fewer than 5, fill the rest with general 'indie' gems
    if len(all_gems) < 5:
        print("Not enough diverse gems. Filling with general indie masterpieces...")
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://store.steampowered.com/api/storesearch/?term=indie&l=english&cc=US", headers=headers)
        fallback_items = res.json().get("items", [])
        for item in fallback_items:
            if item["id"] not in seen_ids:
                all_gems.append({"id": item["id"], "title": item["name"], "theme": "Indie"})
                seen_ids.add(item["id"])
                if len(all_gems) >= 10: break
    # Return a final capped list of 10 games
    return all_gems[:10]
def get_ai_description(game):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Write a 2-sentence viral marketing pitch for a 'Hidden Gem' game called {game['title']}. The genre/theme is {game['theme']}. Make it sound mysterious and exciting."
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
def main():
    gems = fetch_diverse_gems()
    if not gems:
        print("Critical Error: No games found. Skipping update.")
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
    print(f"Successfully updated games.json with {len(processed_games)} diverse gems!")
if __name__ == "__main__":
    main()
