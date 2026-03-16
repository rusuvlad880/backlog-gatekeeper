import sqlite3

def create_table():

    #Creates file called backlog.db if it doesn't exist and connects to it

    conn = sqlite3.connect('backlog.db')
    cursor = conn.cursor()

    #SQL command creates games table with 4 columns

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            platform TEXT NOT NULL,
            status TEXT NOT NULL       
        )
    ''')

    #Save changes and close the connection
    conn.commit()
    conn.close()

def add_game(title, platform, status):

    conn = sqlite3.connect('backlog.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO games (title, platform, status)
        VALUES (?, ?, ?)
    ''', (title, platform, status))
    conn.commit()
    conn.close()

def get_all_games():
    conn = sqlite3.connect('backlog.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()
    conn.close()
    return games

if __name__ == '__main__':
    create_table()
    print("Database and 'games' table created succesfully!")
