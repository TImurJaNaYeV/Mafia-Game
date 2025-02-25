import telebot
import random
import dataForServies
from time import sleep

bot = telebot.TeleBot("6533000770:AAExKnnEUJRvTgY0OnFPBzKeLFp-I0nIPDc")
state = "await"

class Mafia_Game():
    def __init__(self):
        self.admin_id = 1861478708
        self.state = "await"
        self.no_keyboard = telebot.types.ReplyKeyboardRemove()
        dataForServies.reset_game()
        bot.send_message(self.admin_id, 'Invite players to the game :)', reply_markup=self.admin_panel(["/invite"]))

    def is_admin(self, id):
        return self.admin_id == id

    def get_others(self, id):
        others = []
        for p in dataForServies.get_users():
            if p['id'] != id:
                others.append(p)
        return others

    def all_not_you(self, id):
        others = self.get_others(id)
        keyboard_menu = telebot.types.ReplyKeyboardMarkup(True)
        for o in others:
            keyboard_menu.add(telebot.types.KeyboardButton(o["username"]))
        return keyboard_menu
    
    def msg_all(self, msg, keyboard = None, participation = None, alive = None, role = None):
        if keyboard == None:
            keyboard = self.no_keyboard
        players = dataForServies.get_users(participation, alive, role)
        for i in players:
            bot.send_message(i['id'], msg, reply_markup=keyboard)
    
    def admin_panel(self, commands):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        for c in commands:
            keyboard.add(telebot.types.KeyboardButton(c))
        return keyboard
game = Mafia_Game()

@bot.message_handler(commands=["reg"])
def reg(msg):
    user_id = msg.from_user.id
    user_name = msg.from_user.first_name
    dataForServies.add_player(user_id, user_name)
    bot.send_message(user_id, "You had been succesfully registered", reply_markup=game.no_keyboard)
    

# delets players from db
@bot.message_handler(commands=["clear"], func=lambda msg: game.state == "await")
def clear_players(msg):
    user_id = msg.from_user.id
    if game.is_admin(user_id):
        bot_reply = "Hello Master, I'm going to delete all users from the game"
        dataForServies.clear_players()
    else:
        bot_reply = "You are not my Master"
    bot.send_message(user_id, bot_reply, reply_markup=game.no_keyboard)

@bot.message_handler(commands=["invite"], func=lambda msg: game.state == "await")
def send_invites(msg):
    # menu 
    user_id = msg.from_user.id
    if game.is_admin(user_id):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        btn1 = telebot.types.KeyboardButton("Accept")
        btn2 = telebot.types.KeyboardButton("Decline")
        keyboard.add(btn1, btn2)
        game.msg_all("Do you want to participate in Mafia", keyboard)
        game.state = "invite"
        bot.send_message(user_id,"The invites had been sent successfully", reply_markup=game.admin_panel(["Accept", "Decline", "/start"]))
    else:
        bot.send_message(user_id,"You are not my Master", reply_markup=game.no_keyboard)

# starts the game and tells the players their role
@bot.message_handler(commands=["start"], func=lambda msg: game.state == "invite")
def start_game(msg):
    user_id = msg.from_user.id
    if game.is_admin(user_id):
        dataForServies.set_roles()
        players = dataForServies.get_users(1, 1)
        game.msg_all("Game has began")
        for p in players:
            bot.send_message(p['id'], "Your role is " + p['role'], reply_markup=game.no_keyboard)
        game.state = 'play.night.mafia'
        game.msg_all('Mafia type in [/choose] to get the list of players to kill:)', role='mafia')
    else:
        bot.send_message(user_id,"You are not my Master", reply_markup=game.no_keyboard)

@bot.message_handler(commands=["next"])
def next(msg):
    user_id = msg.from_user.id
    if game.is_admin(user_id):
        if game.state == 'play.night.mafia':
            game.state = "play.night.sheriff"
            game.msg_all("sheriff's night shift has begun")
            game.msg_all('sheriff type in [/choose] to get the list of players to check:)', role='sheriff')
        elif game.state == 'play.night.sheriff':
            game.votes = {}
            players = dataForServies.get_users(1)
            for p in players:
                game.votes[p['username']] = 0
            game.voted = []
            game.state = "play.day.vote"
            game.msg_all("The trial for the sheriff's suspect has begun")
            game.msg_all('Players type in [/vote] to get the list of players to vote out:)', alive=1)
        elif game.state == 'play.day.vote':
            exclude = {'username': None, 'votes': 0}
            for player in game.votes:
                if game.votes[player] > exclude['votes']:
                    exclude['username'] = player
                    exclude['votes'] = game.votes[player]
            is_mafia = 'was a mafia' if dataForServies.is_mafia(exclude['username']) else 'was an inocent'
            game.msg_all(f"{exclude['username']} was voted out and he(she) {is_mafia}")
            dataForServies.kill(exclude["username"])
            mafias_amount = len(dataForServies.get_users(alive=1, role="mafia"))
            players_amount = len(dataForServies.get_users(alive=1))
            if players_amount / 2 == mafias_amount:
                game.msg_all("Mafia has won :0", participation=1)
                game.__init__()
            elif mafias_amount == 0:
                game.msg_all("HAHAHH Mafia has lost L :)", participation=1)
                game.__init__()
            else:
                game.msg_all("Mafia is still in town 😈", alive=1)
                game.state = 'play.night.mafia'
                game.msg_all('Mafia type in [/choose] to get the list of players to kill:)', role='mafia')
    else:   
        bot.send_message(user_id,"You are not my Master", reply_markup=game.no_keyboard)

@bot.message_handler(func=lambda msg: game.state == "invite")
def participation_choice(msg):
    user_id = msg.from_user.id
    user_msg = msg.text
    if user_msg == "Accept":
        dataForServies.change_participation(user_id)
        bot.send_message(game.admin_id, f"{dataForServies.player_count_part()}/{dataForServies.player_count()} joined", reply_markup=game.admin_panel(["Accept", "Decline", "/start"]))
    elif user_msg == "Decline":
        bot.send_message(user_id,"okay your loss", reply_markup=game.no_keyboard)
    else:
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        btn1 = telebot.types.KeyboardButton("Accept")
        btn2 = telebot.types.KeyboardButton("Decline")
        keyboard.add(btn1, btn2)
        bot.send_message(user_id, "So will you play?", reply_markup=keyboard)

# Mafia tells who to kill
@bot.message_handler(commands=["choose"], func=lambda msg: game.state == "play.night.mafia")
def mafia_choice(msg):
    user_id = msg.from_user.id
    user_role = dataForServies.get_user(user_id)['role']
    print(dataForServies.get_user(user_id))
    if "mafia" == user_role:
        keyboard = game.all_not_you(user_id)
        bot.send_message(user_id, "Choose your prey:", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "It's not your turn.", reply_markup=game.no_keyboard)

@bot.message_handler(func=lambda msg: game.state == "play.night.mafia")
def mafia_kill(msg):
    user_id = msg.from_user.id
    user_msg = msg.text
    user_role = dataForServies.get_user(user_id)['role']
    if "mafia" == user_role:
        dataForServies.kill(user_msg)
        bot.send_message(user_id, "You have succesfully executed ur prey", reply_markup=game.no_keyboard)
        bot.send_message(game.admin_id,"Mafia has made its move", reply_markup=game.admin_panel(["/next"]))
        
    else:
        bot.send_message(user_id, "It's not your turn.", reply_markup=game.no_keyboard)

@bot.message_handler(commands=["choose"], func=lambda msg: game.state == "play.night.sheriff")
def mafia_choice(msg):
    user_id = msg.from_user.id
    user_role = dataForServies.get_user(user_id)['role']
    if "sheriff" == user_role:
        keyboard = game.all_not_you(user_id)
        bot.send_message(user_id, "Choose who you want to check:", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "It's not your turn.", reply_markup=game.no_keyboard)

# sheriff suspects a player
@bot.message_handler(func=lambda msg: game.state == "play.night.sheriff")
def mafia_msg_bot(msg):
    user_id = msg.from_user.id
    user_msg = msg.text
    user_role = dataForServies.get_user(user_id)['role']
    if "sheriff" == user_role:
        sheriff_guess = dataForServies.is_mafia(user_msg)
        if sheriff_guess:
            bot.send_message(user_id, "The sheriff had successfuly located the mafia", reply_markup=game.no_keyboard)
        else:
            bot.send_message(user_id, "The sheriff had failed to located the mafia", reply_markup=game.no_keyboard)
        bot.send_message(game.admin_id, "Sheriff had closed his case", reply_markup=game.admin_panel(["/next"]))

@bot.message_handler(commands=["vote"], func=lambda msg: game.state == "play.day.vote")
def get_vote_list(msg):
    user_id = msg.from_user.id
    user_data = dataForServies.get_user(user_id)
    print(user_data)
    if user_data['alive'] == 1:
        keyboard = game.all_not_you(user_id)
        bot.send_message(user_id, "Choose who you think is the Mafia!", reply_markup=keyboard)

@bot.message_handler(func=lambda msg: game.state == "play.day.vote")
def vote(msg):
    user_id = msg.from_user.id
    user_data = dataForServies.get_user(user_id)
    if user_data['alive'] == 1 and user_data['username'] not in game.voted:
        game.votes[msg.text] += 1
        game.voted.append(user_data['username'])
        bot.send_message(user_id, "Thank you for voting", reply_markup=game.no_keyboard)
        bot.send_message(game.admin_id, f"{len(game.voted)}/{len(dataForServies.get_users(alive=1))} have voted", reply_markup=game.admin_panel(["/next"]))
            
# chatting pre-game
@bot.message_handler()
def blablabla(msg):
    chat_id = msg.chat.id
    user_msg = msg.text
    bot_reply = user_msg
    bot.send_message(chat_id, bot_reply, reply_markup=game.no_keyboard)
bot.polling(True)
