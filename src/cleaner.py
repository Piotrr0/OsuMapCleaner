import urllib.request
import time
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import json
from dataclasses import dataclass
import os
import re

@dataclass
class Beatmap:  
    id: int
    difficulty_name: str
    difficulty_rating: float

def delete_maps(song_path, beatmap):
    if beatmap.difficulty_rating < difficulty_rating_threshold:
        if os.path.isdir(song_path):
            song_files = [file for file in os.listdir(song_path) if file.endswith(".osu")]
            for song_file in song_files:
                if beatmap.difficulty_name in song_file:
                    print(f"Deleting: {song_file}")

def get_songs(songs_path):
    return os.listdir(songs_path)

def get_id(song_dir):    
    match = re.match(r'(\d+)', song_dir)
    return match.group(1) if match else None

def web_scrap(song_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    req = urllib.request.Request(song_url, headers=headers)
    
    sleep_time = 15

    while True:
        try:
            response = urllib.request.urlopen(req)
            web_content = response.read()
            break 
        except HTTPError as e:
            if e.code == 429:
                print(f"Received HTTP 429: Too Many Requests. Retrying after {sleep_time} seconds...")
                attempts += 1
                time.sleep(sleep_time)  
            else:
                print(f"HTTP error occurred: {e}")
                return []
        except URLError as e:
            print(f"URL error occurred: {e}")
            return []

    soup = BeautifulSoup(web_content, 'html.parser')
    script_tag = soup.find('script', id='json-beatmapset', type='application/json')

    if script_tag:
        json_data = script_tag.string
        if json_data:
            parsed_json = json.loads(json_data)
            beatmaps = []
            for bm in parsed_json['beatmaps']:
                beatmap_id = bm.get("id")
                difficulty_rating = bm.get("difficulty_rating")
                difficulty_name = bm.get("version")
                
                beatmap_instance = Beatmap(beatmap_id, difficulty_name, difficulty_rating)
                beatmaps.append(beatmap_instance)
            return beatmaps  
    else:
        print("No JSON content found.")
        return []

difficulty_rating_threshold = 2
downloaded_songs = 0
osu_songs_path = "songs_path" #usually C:\Users<PC user>\AppData\Local\osu!/Songs
url = "https://osu.ppy.sh/beatmapsets/"

def clean_maps():
    global downloaded_songs
    songs = get_songs(osu_songs_path)
    
    for song in songs:
        song_id = get_id(song)
        if song_id:
            song_url = url + song_id
            beatmaps = web_scrap(song_url)
            downloaded_songs += 1
            print(f"{downloaded_songs}/{len(songs)}")  
            for beatmap in beatmaps:
                song_path = os.path.join(osu_songs_path, song)
                delete_maps(song_path, beatmap) 
            
