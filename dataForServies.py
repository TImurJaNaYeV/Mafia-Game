import sqlite3
import random


def add_table():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("ALTER TABLE players ADD COLUMN participation INTEGER CHECK(participation IN (0,1))")
    connect.commit()
    connect.close()

# adds users to DB
def add_player(id: int, username: str):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("INSERT INTO players (id, username, alive, participation) VALUES (?, ?, ?, ?)", [id, username, 1, 0])
    connect.commit()
    connect.close()

#creates roles
def set_roles():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    amount = player_count()
    mafia_amount = amount // 4
    if amount == 3:
        roles = ["mafia", "sheriff", "civillian"]
    else:
        roles = ["mafia"] * mafia_amount + ["sheriff"] + ["civillian"] * (amount - mafia_amount - 1)
    
        if amount >= 6:
            roles.remove("civillian")
            roles.append("doctor")
    random.shuffle(roles)
    print(roles)
    cursor.execute("SELECT id FROM players")
    players = cursor.fetchall()
    for id, role in zip(players, roles):
        cursor.execute("UPDATE players SET role = ? WHERE id = ?", [role, id[0]])
    connect.commit()
    connect.close()

#resets game
def reset_game():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("SELECT id FROM players")
    players = cursor.fetchall()
    for id in players:
        cursor.execute("UPDATE players SET role = Null, alive = 1, participation = 0 WHERE id = ?", [id[0]])
    connect.commit()
    connect.close()


# counts players
def player_count():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    connect.commit()
    connect.close()
    return len(players)

# counts players
def player_count_part():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM players WHERE participation = 1")
    players = cursor.fetchall()
    connect.commit()
    connect.close()
    return len(players)

# finds players role by id
def get_user(id: int = None, username: str = None):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM players WHERE id = (?) OR username = (?)", [id, username])
    player = cursor.fetchone()
    columns = [d[0] for d in cursor.description] 
    connect.close()
    try:
        return dict(zip(columns, player))
    except:
        return None


# deletes players from DB 
def clear_players():
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("DELETE FROM players")
    connect.commit()
    connect.close()

# gets all the info about all players
def get_users(participation = None, alive = None, role = None):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    request = []
    if participation != None:
        request.append(f"participation = {participation}")
    if alive != None:
        request.append(f"alive = {alive}")
    if role != None:
        request.append(f'role = "{role}"')
    if len(request) > 0:
        request = " WHERE " + " AND ".join(request)
    else:
        request = ""
    cursor.execute("SELECT * FROM players" + request)
    players = cursor.fetchall()
    columns = [d[0] for d in cursor.description] 
    connect.close()
    try:
        return [dict(zip(columns, p)) for p in players]
    except:
        return None

# kills players
def kill(name: str):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("UPDATE players SET alive = 0 WHERE username = (?)", [name])
    connect.commit()
    connect.close()

#check for mafia
def is_mafia(name: str):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("SELECT role FROM players WHERE username = (?)", [name])
    role = cursor.fetchone()[0]
    connect.commit()
    connect.close()
    return role == "mafia"

# changes participation 
def change_participation(id: int):
    connect = sqlite3.connect("data.db")
    cursor = connect.cursor()
    cursor.execute("UPDATE players SET participation = 1 WHERE id = (?)", [id])
    connect.commit()
    connect.close()