#!/usr/bin/python

import telebot
from telebot import types
import sqlite3

API_TOKEN = '5510728878:AAHhIitKWRAkv_A2xKH4ecGbzxzNuux7WDk'

bot = telebot.TeleBot(API_TOKEN)
conn = sqlite3.connect('database_progetto.db',check_same_thread=False)
cursor = conn.cursor()
flag = {}
matricola = {}
chat_id = 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global chat_id
    chat_id = message.chat.id
    msg = bot.send_message(chat_id,'Inserisci matricola, 6 numeri')
    global flag
    flag[message.chat.id] = 0

def db_check_mat(matricola: int,message):
    cursor.execute("SELECT COUNT(password) FROM studenti WHERE matricola LIKE ?",(matricola[message.chat.id],))
    #conn.commit()
    if cursor.fetchone()[0] == 1:
        global flag
        flag[message.chat.id] = 1
        bot.send_message(message.chat.id,'Matricola trovata! Inserire password: ')
    else:
        bot.send_message(message.chat.id,'Matricola errata, riprova')

def db_check_psw(matricola: int,psw,message):
    cursor.execute("SELECT password FROM studenti WHERE matricola LIKE ?",(matricola[message.chat.id],))
    if psw == cursor.fetchone()[0]:
        homepage(message)
    else:
        bot.send_message(message.chat.id,'Password errata')

@bot.message_handler(content_types = ["text"])
def login(message):
    if flag[message.chat.id] == 0:
        if len(message.text) == 6 and message.text.isnumeric():
            bot.reply_to(message, "Matricola inserita: "+message.text)
            global matricola
            matricola[message.chat.id] = message.text
            db_check_mat(matricola,message)
        else:
            bot.reply_to(message, "La matricola che hai inserito non è di 6 numeri")
    else:
        db_check_psw(matricola,message.text,message)

def homepage(message):
    msg = bot.send_message(message.chat.id,'Password corretta! Benvenuto '+matricola[message.chat.id])
    markup_home = types.InlineKeyboardMarkup()
    markup_home.row_width = 2
    markup_home.add(types.InlineKeyboardButton("Visualizza tutti i corsi", callback_data="lezioni"),
                            types.InlineKeyboardButton("Visualizza le tue prenotazioni", callback_data="prenotazioni"))
    markup_home.add(types.InlineKeyboardButton("Esci",callback_data="esci"))
    bot.send_message(chat_id,"Scegli: ",reply_markup=markup_home)

@bot.callback_query_handler(func=lambda query: query.data == "lezioni")
def scelta_lezioni(message):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Corsi del primo anno", callback_data="primo"),
                            types.InlineKeyboardButton("Corsi del secondo anno", callback_data="secondo"))
    bot.send_message(chat_id,"Scegli quali corsi visualizzare: ",reply_markup=markup)


@bot.callback_query_handler(func=lambda query: query.data == "primo")
def lista_lezioni_primo(call):
    cursor.execute('SELECT descrizione,data_ora FROM lezioni WHERE aula LIKE "I1"')
    roba = cursor.fetchall()
    markup_primo = types.InlineKeyboardMarkup()
    markup_primo.row_width = 1
    a = 1
    for i in roba:
        markup_primo.add(types.InlineKeyboardButton(i[0]+" "+i[1],callback_data=a))
        a = a + 1
    markup_primo.add(types.InlineKeyboardButton("Torna indietro",callback_data="indietro"))
    bot.send_message(chat_id,"Lista delle lezioni del primo anno, cliccane una per prenotarti o avere informazioni aggiuntive: ",reply_markup=markup_primo)


@bot.callback_query_handler(func=lambda call: call.data == "secondo")
def lista_lezioni_secondo(call):
    cursor.execute('SELECT descrizione,data_ora FROM lezioni WHERE aula LIKE "A0"')
    roba = cursor.fetchall()
    markup_secondo = types.InlineKeyboardMarkup()
    markup_secondo.row_width = 1
    a = 12
    for i in roba:
        markup_secondo.add(types.InlineKeyboardButton(i[0]+" "+i[1],callback_data=a))
        a = a + 1
    markup_secondo.add(types.InlineKeyboardButton("Torna indietro",callback_data="indietro"))
    bot.send_message(chat_id,"Lista delle lezioni del primo anno, cliccane una per prenotarti o avere informazioni aggiuntive: ",reply_markup=markup_secondo)

@bot.callback_query_handler(func=lambda call: call.data == "indietro")
def indietro(call):
    scelta_lezioni(call)

bot.infinity_polling()
