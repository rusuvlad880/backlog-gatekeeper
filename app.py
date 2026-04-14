import customtkinter as ctk
import database
import requests
import io
from PIL import Image


#Set the overall theme and color of the app

ctk.set_appearance_mode("dark")

BG_COLOR = "#0B1117" #bottom layer
SIDEBAR_COLOR = "#111827"
SURFACE_COLOR = "#1F2937" # floating layer
CARD_COLOR = "#1F2937" # game cards color
INPUT_COLOR = "#374151" # text boxes and dropdowns

ACCENT_COLOR = "#8B5CF6" #primary buttons
ACCENT_HOVER = "#7C3AED" # button hover state

PLAY_COLOR = "#10B981"
PLAY_HOVER = "#059669"
DELETE_COLOR = "#F43F5E"
DELETE_HOVER = "#E11D48"

TEXT_MAIN = "#F8FAFC"
TEXT_SUB = "#94A3B8"
FONT_MAIN = ("Segoe UI", 14)
FONT_HEADING = ("Seague UI", 28, "bold")

#Create the main window

app = ctk.CTk()
app.geometry ("1100x700")
app.title("Backlog Gatekeeper")

app.configure(fg_color=BG_COLOR)

login_screen = ctk.CTkFrame(app, fg_color="transparent")
dashboard_screen = ctk.CTkFrame(app, fg_color="transparent")

current_image_url = ""

image_cache = {}

# SCREEN 1: LOGIN

login_box = ctk.CTkFrame(login_screen, width=400, height=500)
login_box.pack(expand=True)

login_title = ctk.CTkLabel(login_box, text="Gatekeeper Acces", font=("Arial", 28, "bold"))
login_title.pack(pady=(40, 20))

email_entry = ctk.CTkEntry(login_box, placeholder_text="Email Address", width=250)
email_entry.pack(pady=10)

password_entry = ctk.CTkEntry(login_box, placeholder_text="Password", show="*", width=250)
password_entry.pack(pady=10)

error_label = ctk.CTkLabel(login_box, text="", text_color="red")
error_label.pack()

def handle_auth(action):
    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        error_label.configure(text="Please fill in both fields.")
        return
    
    try:
        if action == "login":
            database.login_user(email, password)
        elif action == "register":
            database.register_user(email, password)

        login_screen.pack_forget()
        dashboard_screen.pack(fill="both", expand=True)
        load_games()

    except Exception as e:
        print(f"Auth Error: {e}")
        error_label.configure(text="Authentication Failed. Try again.")

login_btn = ctk.CTkButton(login_box, text="Login", command=lambda: handle_auth("login"), width=250)
login_btn.pack(pady=(20, 10))

register_btn = ctk.CTkButton(login_box, text="Create Account", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: handle_auth("register"), width=250)
register_btn.pack(pady=(0, 40))

# SCREEN 2 DASHBOARD

# GLOBAL NAVIGATION SIDEBAR

global_sidebar = ctk.CTkFrame(dashboard_screen, width=180, corner_radius=0, fg_color="#070A10") 
global_sidebar.pack(side="left", fill="y")

app_logo = ctk.CTkLabel(global_sidebar, text="GATEKEEPER", font=FONT_HEADING, text_color=ACCENT_COLOR)
app_logo.pack(pady=(30, 40))

# CONTENT CONTAINER
content_container = ctk.CTkFrame(dashboard_screen, fg_color="transparent")
content_container.pack(side="right", fill="both", expand=True)

# 3 PAGES
library_page = ctk.CTkFrame(content_container, fg_color="transparent")
social_page = ctk.CTkFrame(content_container, fg_color="transparent")
settings_page = ctk.CTkFrame(content_container, fg_color="transparent")

def load_social_page():
    # 1. Clear the page so we have a blank canvas
    for widget in social_page.winfo_children():
        widget.destroy()
        
    # 2. Ask the database if this user has a profile
    profile = database.get_profile()
    
    if profile is None:
        # --- THE CLAIM USERNAME SCREEN ---
        setup_frame = ctk.CTkFrame(social_page, fg_color="transparent")
        setup_frame.pack(expand=True)
        
        ctk.CTkLabel(setup_frame, text="Welcome to the Network.", font=("Segoe UI", 32, "bold")).pack(pady=(0, 10))
        ctk.CTkLabel(setup_frame, text="Claim your unique username to start adding friends.", font=FONT_MAIN, text_color=TEXT_SUB).pack(pady=(0, 30))
        
        username_var = ctk.StringVar()
        user_entry = ctk.CTkEntry(setup_frame, placeholder_text="Enter a username...", textvariable=username_var, width=300, height=45, fg_color=INPUT_COLOR, border_width=0, font=FONT_MAIN)
        user_entry.pack(pady=(0, 20))
        
        def attempt_claim():
            desired_name = username_var.get().strip()
            if desired_name:
                success = database.create_profile(desired_name)
                if success:
                    print(f"Successfully claimed {desired_name}!")
                    load_social_page() # Reload the page to show the actual hub!
                else:
                    print("That username is taken or an error occurred.")
                    
        ctk.CTkButton(setup_frame, text="Claim Username", width=300, height=45, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, font=("Segoe UI", 16, "bold"), command=attempt_claim).pack()

    else:
        # --- THE ACTUAL SOCIAL HUB ---
        my_username = profile['username']
        
        header_frame = ctk.CTkFrame(social_page, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(header_frame, text=f"Welcome back, {my_username}!", font=("Segoe UI", 32, "bold"), text_color=TEXT_MAIN).pack(side="left")

        pending_requests = database.get_pending_requests()
        
        if pending_requests:
            inbox_frame = ctk.CTkFrame(social_page, fg_color="transparent")
            inbox_frame.pack(fill="x", padx=40, pady=(0, 20))
            
            ctk.CTkLabel(inbox_frame, text="📥 Incoming Friend Requests", font=("Segoe UI", 20, "bold"), text_color=ACCENT_COLOR).pack(anchor="w", pady=(0, 10))
            
            for req in pending_requests:
                req_row = ctk.CTkFrame(inbox_frame, fg_color=CARD_COLOR, corner_radius=8)
                req_row.pack(fill="x", pady=5)
                
                ctk.CTkLabel(req_row, text=f"{req['username']} wants to be friends!", font=FONT_MAIN, text_color=TEXT_MAIN).pack(side="left", padx=20, pady=15)
                
                def accept_cmd(rid=req['request_id']):
                    if database.accept_friend_request(rid):
                        print(f"Accepted {req['username']}!")
                        load_social_page() # Instantly reload the page to hide the accepted request!
                
                # A slick green button for accepting!
                acc_btn = ctk.CTkButton(req_row, text="Accept", width=80, fg_color="#10B981", hover_color="#059669", command=accept_cmd)
                acc_btn.pack(side="right", padx=20)

        # ==========================================
        #          MY FRIENDS LIST
        # ==========================================
        my_friends = database.get_friends_list()
        
        friends_frame = ctk.CTkFrame(social_page, fg_color="transparent")
        friends_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        ctk.CTkLabel(friends_frame, text="👥 My Friends", font=("Segoe UI", 20, "bold"), text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 10))
        
        # 1. WE DEFINE THE POP-UP FUNCTION OUTSIDE THE LOOP!
        def open_friend_shelf(friend_id, friend_name):
            shelf_window = ctk.CTkToplevel(app)
            shelf_window.title(f"{friend_name}'s Digital Shelf")
            shelf_window.geometry("800x500")
            shelf_window.configure(fg_color=BG_COLOR)
            shelf_window.attributes("-topmost", True)
            
            ctk.CTkLabel(shelf_window, text=f"📚 {friend_name}'s Backlog", font=("Segoe UI", 24, "bold"), text_color=ACCENT_COLOR).pack(pady=20)
            
            their_games = database.get_friend_games(friend_id)
            
            if not their_games:
                ctk.CTkLabel(shelf_window, text=f"{friend_name} doesn't have any games yet!", font=FONT_MAIN, text_color=TEXT_SUB).pack(pady=50)
                return
                
            grid_frame = ctk.CTkScrollableFrame(shelf_window, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            row_idx, col_idx = 0, 0
            for game in their_games:
                g_card = ctk.CTkFrame(grid_frame, fg_color=CARD_COLOR, width=220, height=200, corner_radius=10)
                g_card.grid_propagate(False)
                g_card.grid(row=row_idx, column=col_idx, padx=15, pady=15)
                
                # 2. Fetch and draw the Steam image!
                if game.get('image_url'):
                    try:
                        import urllib.request
                        from PIL import Image
                        import io
                        
                        # Request the image from the web
                        req = urllib.request.Request(game['image_url'], headers={'User-Agent': 'Mozilla/5.0'})
                        raw_data = urllib.request.urlopen(req).read()
                        img_data = Image.open(io.BytesIO(raw_data))
                        
                        # Convert it into a CustomTkinter image
                        cover_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(180, 85))
                        img_label = ctk.CTkLabel(g_card, image=cover_image, text="")
                        img_label.pack(pady=(15, 0))
                    except Exception as e:
                        print(f"Error loading image for {game['title']}: {e}")
                        # Fallback if image fails to load
                        ctk.CTkLabel(g_card, text="🖼️ No Image", font=FONT_MAIN, text_color=TEXT_SUB).pack(pady=(15, 0))
                else:
                    ctk.CTkLabel(g_card, text="🖼️ No Image", font=FONT_MAIN, text_color=TEXT_SUB).pack(pady=(15, 0))
                        
                # 3. Draw the Title and Status below the image
                ctk.CTkLabel(g_card, text=game['title'], font=("Segoe UI", 14, "bold"), text_color=TEXT_MAIN, wraplength=180).pack(pady=(10, 5))
                
                status_color = PLAY_COLOR if game['status'] == "Playing" else TEXT_SUB
                ctk.CTkLabel(g_card, text=game['status'], font=("Segoe UI", 12), text_color=status_color).pack()
                
                # 4. Grid math (3 columns)
                col_idx += 1
                if col_idx > 2: 
                    col_idx = 0
                    row_idx += 1

        # 2. NOW WE RUN THE LOOP
        if my_friends:
            for f in my_friends:
                f_card = ctk.CTkFrame(friends_frame, fg_color=CARD_COLOR, corner_radius=8, height=60)
                f_card.pack(fill="x", pady=5)
                
                ctk.CTkLabel(f_card, text=f['username'], font=FONT_MAIN, text_color=TEXT_MAIN).pack(side="left", padx=20, pady=15)
                
                # 3. WE USE LAMBDA TO SAFELY PASS THE SPECIFIC FRIEND'S DATA!
                view_btn = ctk.CTkButton(f_card, text="View Shelf", width=100, fg_color=INPUT_COLOR, hover_color=SIDEBAR_COLOR, 
                                         command=lambda fid=f['friend_id'], fname=f['username']: open_friend_shelf(fid, fname))
                view_btn.pack(side="right", padx=20)
        else:
            ctk.CTkLabel(friends_frame, text="It's a bit lonely here. Search for friends below!", font=FONT_MAIN, text_color=TEXT_SUB).pack(anchor="w")

        # ==========================================
        #          FRIEND SEARCH ENGINE
        # ==========================================


        search_frame = ctk.CTkFrame(social_page, fg_color="transparent")
        search_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        friend_search_var = ctk.StringVar()
        friend_search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 Search for friends by username...", textvariable=friend_search_var, width=350, height=35, fg_color=INPUT_COLOR, border_width=0)
        friend_search_entry.pack(side="left", padx=(0, 10))
        
        # This is the box where the search results will appear!
        results_frame = ctk.CTkScrollableFrame(social_page, fg_color="transparent", height=250)
        results_frame.pack(fill="x", padx=40, pady=10)

        def perform_friend_search():
            # 1. Clear old results
            for widget in results_frame.winfo_children():
                widget.destroy()
                
            query = friend_search_var.get().strip()
            if not query:
                return
                
            # 2. Ask the database!
            results = database.search_users(query)
            
            if not results:
                ctk.CTkLabel(results_frame, text="No users found.", font=FONT_MAIN, text_color=TEXT_SUB).pack(pady=20)
                return
                
            # 3. Draw the User Cards
            for user in results:
                user_row = ctk.CTkFrame(results_frame, fg_color=CARD_COLOR, corner_radius=8)
                user_row.pack(fill="x", pady=5)
                
                ctk.CTkLabel(user_row, text=user['username'], font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=20, pady=15)
                
                add_btn = ctk.CTkButton(user_row, text="Add Friend", width=100, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, 
                                        command=lambda fid=user['user_id']: send_request(fid))
                add_btn.pack(side="right", padx=20)

        def send_request(friend_id):
            success = database.send_friend_request(friend_id)
            if success:
                print("Friend request sent successfully!")
            else:
                print("Failed! You might already be friends or have a pending request.")

        search_btn = ctk.CTkButton(search_frame, text="Search", width=100, height=35, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, command=perform_friend_search)
        search_btn.pack(side="left")


#PLACEHOLDER FOR SETTINGS
ctk.CTkLabel(settings_page, text="⚙️ Settings & Sync", font=FONT_HEADING).pack(pady=50)
ctk.CTkLabel(settings_page, text="Steam OAuth Login and App Preferences will go here.", font=FONT_MAIN, text_color=TEXT_SUB).pack()

def switch_page(page_name):
    library_page.pack_forget()
    social_page.pack_forget()
    settings_page.pack_forget()

    if page_name == "Library":
        library_page.pack(fill="both", expand=True)
    elif page_name == "Social":
        social_page.pack(fill="both", expand=True)
    elif page_name == "Settings":
        settings_page.pack(fill="both", expand=True)

# NAV BUTTONS

nav_btn_lib = ctk.CTkButton(global_sidebar, text="📚 My Library", font=FONT_MAIN, fg_color="transparent", text_color=TEXT_MAIN, hover_color=SIDEBAR_COLOR, anchor="w", command=lambda: switch_page("Library"))
nav_btn_lib.pack(pady=10, padx=10, fill="x")

nav_btn_soc = ctk.CTkButton(global_sidebar, text="🌐 Social Hub", font=FONT_MAIN, fg_color="transparent", text_color=TEXT_MAIN, hover_color=SIDEBAR_COLOR, anchor="w", 
                            command=lambda: [load_social_page(), switch_page("Social")])
nav_btn_soc.pack(pady=10, padx=10, fill="x")

nav_btn_set = ctk.CTkButton(global_sidebar, text="⚙️ Settings", font=FONT_MAIN, fg_color="transparent", text_color=TEXT_MAIN, hover_color=SIDEBAR_COLOR, anchor="w", command=lambda: switch_page("Settings"))
nav_btn_set.pack(pady=10, padx=10, fill="x")

def perform_logout():
    # Tell the cloud we are leaving, hide the dashboard, and show the login screen!
    database.supabase.auth.sign_out()
    dashboard_screen.pack_forget()
    login_screen.pack(fill="both", expand=True)

logout_btn = ctk.CTkButton(global_sidebar, text="🚪 Log Out", font=FONT_MAIN, fg_color="transparent", text_color=TEXT_SUB, hover_color="#E11D48", anchor="w", command=perform_logout)
logout_btn.pack(side="bottom", pady=20, padx=10, fill="x")

# Library default
library_page.pack(fill="both", expand=True)

sidebar = ctk.CTkFrame(library_page, width=250, corner_radius=0, fg_color=SIDEBAR_COLOR)
sidebar.pack(side="left", fill="y")

sidebar_title = ctk.CTkLabel(sidebar, text="Add New Game", font=("Arial", 20, "bold"))
sidebar_title.pack(pady=(30, 10))

steam_search_entry = ctk.CTkEntry(sidebar, placeholder_text="Search Steam...", width=200, fg_color=INPUT_COLOR, border_width=0)
steam_search_entry.pack(pady=5)

steam_cache = {}

def perform_steam_search():
    search_term = steam_search_entry.get().strip()
    if not search_term:
        steam_dropdown.set("Type a game first!")
        return
    
    steam_dropdown.set("Searching...") # Give the user visual feedback!
    
    try:
        import requests
        url = f"https://store.steampowered.com/api/storesearch/?term={search_term}&l=english&cc=US"
        data = requests.get(url).json()

        if data.get('items'):
            steam_cache.clear() # Clear the old search memory
            game_names = []
            
            for item in data['items']:
                name = item['name']
                # Save the image URL to our memory bank
                steam_cache[name] = item.get('tiny_image', '') 
                game_names.append(name)
                
            # Boom! We update the dropdown list with the new games!
            steam_dropdown.configure(values=game_names)
            steam_dropdown.set("Select your game...")
        else:
            steam_dropdown.set("No games found.")
            steam_dropdown.configure(values=["No games found."])
            
    except Exception as e:
        print(f"Steam API Error: {e}")

def select_steam_game(choice):
    global current_image_url
    
    # If they actually clicked a game (and not a "Searching..." message)
    if choice in steam_cache:
        current_image_url = steam_cache[choice] # Grab the image from memory
        
        # Auto-fill the boxes!
        title_entry.delete(0, ctk.END)
        title_entry.insert(0, choice)
        
        platform_entry.delete(0, ctk.END)
        platform_entry.insert(0, "PC (Steam)")
        
        # Clean up the UI
        steam_search_entry.delete(0, ctk.END)
        steam_dropdown.set("Search Results...") 
        steam_dropdown.configure(values=["Search Results..."])

# The Search Button
steam_btn = ctk.CTkButton(sidebar, text="Search Steam", command=perform_steam_search, width=200, fg_color=INPUT_COLOR, hover_color=SIDEBAR_COLOR, border_color=ACCENT_COLOR, border_width=1)
steam_btn.pack(pady=5)

# THE NEW DYNAMIC DROPDOWN MENU!
steam_dropdown = ctk.CTkOptionMenu(sidebar, values=["Search Results..."], width=200, command=select_steam_game, 
                                   fg_color=INPUT_COLOR, button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER, dropdown_fg_color=SIDEBAR_COLOR)
steam_dropdown.pack(pady=(0, 20))

title_entry = ctk.CTkEntry(sidebar, placeholder_text="Game Title", width=200, fg_color=INPUT_COLOR, border_width=0)
title_entry.pack(pady=10)

platform_entry = ctk.CTkEntry(sidebar, placeholder_text="Platform (e.g., PC)", width=200, fg_color=INPUT_COLOR, border_width=0)
platform_entry.pack(pady=10)

status_dropdown = ctk.CTkOptionMenu(sidebar, values=["Backlog", "Playing", "Finished"], width=200, 
                                    fg_color=INPUT_COLOR, button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER, dropdown_fg_color=SIDEBAR_COLOR)
status_dropdown.pack(pady=10)
status_dropdown.set("Backlog")

def save_button_clicked():
    global current_image_url
    
    title = title_entry.get().strip()
    platform = platform_entry.get().strip()
    status = status_dropdown.get()

    if title and platform and status:
        try:
            # --- THE SILENT IMAGE FETCHER ---
            final_image_url = current_image_url
            if not final_image_url:
                # They typed it manually! Let's try to grab an image silently in the background.
                try:
                    import requests
                    url = f"https://store.steampowered.com/api/storesearch/?term={title}&l=english&cc=US"
                    res = requests.get(url).json()
                    if res.get('items'):
                        final_image_url = res['items'][0].get('tiny_image', "")
                except:
                    pass # If Steam fails, we just save it without an image.

            database.add_game(title, platform, status, final_image_url)
            print(f"Success! Saved {title} to the cloud.")
            
            title_entry.delete(0, ctk.END)
            platform_entry.delete(0, ctk.END)
            status_dropdown.set("Backlog")
            current_image_url = "" 
            
            load_games() 
            
        except Exception as e:
            print(f"DATABASE ERROR: {e}") 
    else:
        print("Please fill out all boxes.")

save_btn = ctk.CTkButton(sidebar, text="Save to Backlog", command=save_button_clicked, width=200, 
                         fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, font=FONT_MAIN, corner_radius=8)
save_btn.pack(pady=20)

def change_theme_event(new_appearance_mode: str):
    ctk.set_appearance_mode(new_appearance_mode)

theme_option_menu = ctk.CTkOptionMenu(sidebar, values=["System", "Dark", "Light"], command=change_theme_event,
                                      fg_color=INPUT_COLOR, button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER, dropdown_fg_color=SIDEBAR_COLOR)
theme_option_menu.pack(side="bottom", pady=(0, 20))

theme_label = ctk.CTkLabel(sidebar, text="Theme Preferences:")
theme_label.pack(side="bottom", pady=(0, 5))
theme_option_menu.set("System")

main_area = ctk.CTkFrame(library_page, fg_color="transparent")
main_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

dashboard_title = ctk.CTkLabel(main_area, text="My Digital Shelf", font=("Arial", 32, "bold"))
dashboard_title.pack(anchor="w", pady=(0, 20))

stats_frame = ctk.CTkFrame(main_area, fg_color="transparent")
stats_frame.pack(fill="x", pady=(0, 20), anchor="w")

stats_label = ctk.CTkLabel(stats_frame, text="Total: 0 | Playing: 0 | Finished: 0", font=("Arial", 16))
stats_label.pack(side="left")

progress_bar = ctk.CTkProgressBar(stats_frame, width=200, fg_color="#333333", progress_color="#2E7D32")
progress_bar.pack(side="left")
progress_bar.set(0) # Starts at 0%

progress_label = ctk.CTkLabel(stats_frame, text="0% Completed", font=("Arial", 14, "bold"), text_color="#2E7D32")
progress_label.pack(side="left", padx=15)

search_sort_frame = ctk.CTkFrame(main_area, fg_color="transparent")
search_sort_frame.pack(fill="x", pady=(10, 10))

search_var = ctk.StringVar() 

search_entry = ctk.CTkEntry(search_sort_frame, placeholder_text="🔍 Search your library...", textvariable=search_var, width=350, height=35,
                            fg_color=INPUT_COLOR, border_width=0) 
search_entry.pack(side="left")

sort_var = ctk.StringVar(value="Newest First") # Default sorting
sort_dropdown = ctk.CTkOptionMenu(search_sort_frame, values=["Newest First", "Alphabetical (A-Z)", "Platform"], variable=sort_var, command=lambda _: load_games(),
                                  fg_color=SURFACE_COLOR, button_color=ACCENT_COLOR, button_hover_color=ACCENT_HOVER, dropdown_fg_color=SIDEBAR_COLOR)
sort_dropdown.pack(side="right")

tabview = ctk.CTkTabview(main_area, fg_color=SIDEBAR_COLOR, segmented_button_selected_color=ACCENT_COLOR, segmented_button_selected_hover_color=ACCENT_HOVER)
tabview.pack(fill="both", expand=True)

tab_backlog = tabview.add("Backlog")
tab_playing = tabview.add("Playing")
tab_finished = tabview.add("Finished")

scroll_frames = {
    "Backlog": ctk.CTkScrollableFrame(tab_backlog, fg_color="transparent"),
    "Playing": ctk.CTkScrollableFrame(tab_playing, fg_color="transparent"),
    "Finished": ctk.CTkScrollableFrame(tab_finished, fg_color="transparent")
}

for frame in scroll_frames.values():
    frame.pack(fill="both", expand=True)

def change_status(game_id, new_status):
    database.update_game_status(game_id, new_status)
    load_games()

def remove_game(game_id):
    database.delete_game(game_id)
    load_games()

def load_games(*args): 
    for frame in scroll_frames.values():
        for widget in frame.winfo_children():
            widget.destroy()
            
    all_games = database.get_all_games()
    
    total_games = len(all_games)
    playing_count = sum(1 for game in all_games if game[3] == "Playing")
    finished_count = sum(1 for game in all_games if game[3] == "Finished")
    
    stats_label.configure(text=f"Total: {total_games}  |  Playing: {playing_count}  |  Finished: {finished_count}")
    
    if total_games > 0:
        completion_percentage = finished_count / total_games
    else:
        completion_percentage = 0
        
    progress_bar.set(completion_percentage)
    progress_label.configure(text=f"{int(completion_percentage * 100)}% Completed")
    
    current_search = search_var.get().lower()
    games_to_display = []
    
    for game in all_games:
        title = game[1].lower()
        platform = game[2].lower()
        if current_search == "" or current_search in title or current_search in platform:
            games_to_display.append(game)

    current_sort = sort_var.get()

    if current_sort == "Alphabetical (A-Z)":
        # We force Python to look specifically at the Title (index 1) and make it lowercase for fair sorting
        games_to_display = sorted(games_to_display, key=lambda x: x[1].lower())
    elif current_sort == "Platform":
        # Sorts by Platform first, then alphabetical Title
        games_to_display = sorted(games_to_display, key=lambda x: (x[2].lower(), x[1].lower()))
    else: # "Newest First"
        games_to_display.reverse()
    

    tab_cols = {"Backlog": 0, "Playing": 0, "Finished": 0}
    tab_rows = {"Backlog": 0, "Playing": 0, "Finished": 0}
    MAX_COLS = 3 

    for game in games_to_display:
        game_id, title, platform, status, img_link = game[0], game[1], game[2], game[3], game[4]
        
        if status not in scroll_frames:
            status = "Backlog"
            
        card_frame = ctk.CTkFrame(scroll_frames[status], width=220, height=200, corner_radius=15, fg_color=CARD_COLOR)
        card_frame.grid_propagate(False) 
        card_frame.grid(row=tab_rows[status], column=tab_cols[status], padx=15, pady=15)
        
        if img_link: 
            try:
                if img_link not in image_cache:
                    img_data = requests.get(img_link).content 
                    img = Image.open(io.BytesIO(img_data)) 
                    ctk_img = ctk.CTkImage(img, size=(190, 85)) 
                    image_cache[img_link] = ctk_img 
                
                cached_img = image_cache[img_link]
                img_label = ctk.CTkLabel(card_frame, image=cached_img, text="")
                img_label.image = cached_img
                img_label.pack(pady=(10, 5))
            except Exception as e:
                print(f"Failed to load image for {title}: {e}")
        
        title_label = ctk.CTkLabel(card_frame, text=title, font=("Arial", 14, "bold"), wraplength=200)
        title_label.pack(pady=(0, 0))
        
        plat_label = ctk.CTkLabel(card_frame, text=platform, font=("Arial", 12), text_color="gray")
        plat_label.pack(pady=(0, 10))
        
        if status == "Backlog":
            btn = ctk.CTkButton(card_frame, text="Start Playing", fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, command=lambda id=game_id: change_status(id, "Playing"))
        elif status == "Playing":
            btn = ctk.CTkButton(card_frame, text="Finish Game", fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, command=lambda id=game_id: change_status(id, "Finished"))
        elif status == "Finished":
            btn = ctk.CTkButton(card_frame, text="Delete", fg_color="#C62828", hover_color="#B71C1C", command=lambda id=game_id: remove_game(id))
            
        btn.pack(side="bottom", pady=(0, 15))


        tab_cols[status] += 1
        if tab_cols[status] >= MAX_COLS: 
            tab_cols[status] = 0        
            tab_rows[status] += 1        
search_timer = None

def on_search_update(*args):
    global search_timer

    if search_timer is not None:
        app.after_cancel(search_timer)

    search_timer = app.after(300, load_games)

search_var.trace_add("write", load_games)

# START APP

login_screen.pack(fill="both", expand=True)

if __name__ == "__main__":
    app.mainloop()
