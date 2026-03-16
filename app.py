import customtkinter as ctk
import database

# Just to be sure that the table exists before the app starts

database.create_table()

#Set the overall theme and color of the app

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

#Create the main window

app = ctk.CTk()
app.geometry ("500x650")
app.title("Backlog Gatekeeper")

#Welcome Label

welcome_label = ctk.CTkLabel(app, text="Welcome to the Backlog Gatekeeper!", font=("Arial", 20, "bold"))
welcome_label.pack(pady=20)

title_entry = ctk.CTkEntry(app, placeholder_text="Game Title", width=250)
title_entry.pack(pady=10)

platform_entry = ctk.CTkEntry(app, placeholder_text="Platform you own the game", width=250)
platform_entry.pack(pady=10)

status_entry = ctk.CTkEntry(app, placeholder_text="Status of your game", width=250)
status_entry.pack(pady=10)

game_list_frame = ctk.CTkScrollableFrame(app, width=350, height=200, label_text="My Backlog")
game_list_frame.pack(pady=20)

def change_theme_event(new_appearance_mode: str):
    ctk.set_appearance_mode(new_appearance_mode)

theme_option_menu=ctk.CTkOptionMenu(
    app,
    values=["System", "Dark", "Light"],
    command=change_theme_event
)
theme_option_menu.pack(pady=10)
theme_option_menu.set("System")

def mark_as_done(game_id):
    database.delete_game(game_id)
    print(f"Game {game_id} removed from backlog!")
    load_games()

def load_games():
    for widget in game_list_frame.winfo_children():
        widget.destroy()

    games = database.get_all_games()

    for game in games:
        game_id = game[0]
        game_text = f"{game[1]} - {game[2]} [{game[3]}]"

        row_frame = ctk.CTkFrame(game_list_frame, fg_color='transparent')
        row_frame.pack(fill="x", pady=2)

        label =ctk.CTkLabel(row_frame, text=game_text)
        label.pack(anchor="w", padx=10)

        done_button =ctk.CTkButton(row_frame, text="Done", width=50, fg_color="#C62828", hover_color="#B71C1C",
                                   command=lambda id=game_id: mark_as_done(id))
        done_button.pack(side="right", padx=10)

def save_button_clicked():

    title = title_entry.get()
    platform = platform_entry.get()
    status = status_entry.get()

    if title and platform and status:
        database.add_game(title, platform, status)
        print(f"Success! Saved {title} to the database.")

        title_entry.delete(0, ctk.END)
        platform_entry.delete(0, ctk.END)
        status_entry.delete(0, ctk.END)

        load_games()
    else:
        print("Please fill in all the fields!")

add_button = ctk.CTkButton(app, text="Save Game", command=save_button_clicked)
add_button.pack(pady=20)

load_games()

#Run

if __name__ == "__main__":
    app.mainloop()