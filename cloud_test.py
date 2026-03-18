import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load the hidden keys from your .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Create the connection
supabase: Client = create_client(url, key)

# Try to insert a test game directly into the cloud!
try:
    data, count = supabase.table("games").insert({
        "title": "Halo: Combat Evolved", 
        "platform": "Xbox", 
        "status": "Finished"
    }).execute()
    
    print("SUCCESS! Handshake complete.")
    print("Here is the data the cloud sent back:", data[1])
except Exception as e:
    print("Uh oh, something went wrong:", e)