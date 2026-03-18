import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def create_table():
    pass

def add_game(title, platform, status):

    supabase.table("games").insert({
        "title": title, 
        "platform": platform, 
        "status": status
    }).execute()

def get_all_games():

    response = supabase.table("games").select("*").execute()

    games_list = []
    for row in response.data:
        games_list.append((row['id'], row['title'], row['platform'], row['status']))

    return games_list

def delete_game(game_id):

    supabase.table("games").delete().eq("id", game_id).execute()

if __name__ == '__main__':
    print("Cloud database script ready!")