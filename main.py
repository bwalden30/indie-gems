import os
import json
import requests
from groq import Groq

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
STEAM_API_KEY = os.environ.get("STEAM_API_KEY") # Optional, using public API for some calls

def fetch_hidden_gems():
    print("Scanning Steam for hidden gems...")
    # Note: Steam's public search API allows us to find games by tags/sort
    # For a production version, we'd use a more robust scraper or the Steamworks API
    # Here we simulate the filter: High rating, Low review count
    url = "https://store.steampowered.com/api/applist/v2" # Just to get IDs
    # In a real scenario, we use a custom search or a site like SteamDB
    # For this demo, we'll use a curated list of high-potential IDs or a search query
    # Let's simulate the discovery of 3 gems for the first run
    return [
        {"id": "123456", "title": "Example Indie 1", "tags": ["Atmospheric", "Puzzle"], "reviews": 120, "rating": 0.92},
        {"id": "654321", "title": "Example Indie 2", "tags": ["Roguelike", "Hardcore"], "reviews": 80, "rating": 0.88},
        {"id": "987654", "title": "Example Indie 3", "tags": ["Story Rich", "Indie"], "reviews": 210, "rating": 0.95},
    ]

def get_ai_description(game):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Write a 2-sentence viral marketing pitch for a 'Hidden Gem' game called {game['title']}. Tags: {game['tags']}. It has a {game['rating']*100}% positive rating. Make it sound mysterious and exciting."
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def main():
    gems = fetch_hidden_gems()
    processed_games = []
    
    for gem in gems:
        desc = get_ai_description(gem)
        processed_games.append({
            "title": gem['title'],
            "description": desc,
            "image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{gem['id']}/header.jpg",
            "url": f"https://store.steampowered.com/app/{gem['id']}"
        })
    
    with open('games.json', 'w') as f:
        json.dump(processed_games, f, indent=4)
    print("Successfully updated games.json")

if __name__ == "__main__":
    main()
