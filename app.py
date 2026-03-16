import customtkinter as ctk
import database

# Just to be sure that the table exists before the app starts

database.create_table()

#Set the overall theme and color of the app

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

#Create the main window

app = ctk.CTk()
app.geometry ("500x350")
app.title("Backlog Gatekeeper")

#Welcome Label

welcome_label = ctk.CTkLabel(app, text="Welcome to the Backlog Gatekeeper!", font=("Arial", 20, "bold"))
welcome_label.pack(pady=40)

title_entry = ctk.CTkEntry(app, placeholder_text="Game Title", width=250)
title_entry.pack(pady=10)

platform_entry = ctk.CTkEntry(app, placeholder_text="Platform you own the game", width=250)
platform_entry.pack(pady=10)

status_entry = ctk.CTkEntry(app, placeholder_text="Status of your game", width=250)
status_entry.pack(pady=10)

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

    else:
        print("Please fill in all the fields!")

add_button = ctk.CTkButton(app, text="Save Game", command=save_button_clicked)
add_button.pack(pady=20)

#Run

if __name__ == "__main__":
    app.mainloop()