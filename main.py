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
logged = 0
id_lez_corrente = "" #salva id lezione per evitare problemi
id_lez = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21",
         "22","23","24","25","26"]
id_posto = ["p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15","p16","p17","p18","p19","p20"]
id_cancella = ["c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12","c13","c14","c15","c16","c17","c18","c19","c20",
                "c21","c22","c23","c24","c25","c26"]

@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(chat_id,'Inserisci matricola, 6 numeri')
    global flag
    flag[message.chat.id] = 0

def db_check_mat(matricola: int,message):
    cursor.execute("SELECT COUNT(password) FROM studenti WHERE matricola LIKE ?",(matricola[message.chat.id],))
    if cursor.fetchone()[0] == 1:
        global flag
        flag[chat_id] = 1
        bot.send_message(message.chat.id,'Matricola trovata! Inserire password: ')
    else:
        bot.send_message(message.chat.id,'Matricola errata, riprova')

def db_check_psw(matricola: int,psw,message):
    cursor.execute("SELECT password FROM studenti WHERE matricola LIKE ?",(matricola[message.chat.id],))
    if psw == cursor.fetchone()[0]:
        msg = bot.send_message(message.chat.id,'Password corretta! Benvenuto '+matricola[chat_id])
        global logged
        logged = 1
        homepage(message)
    else:
        bot.send_message(message.chat.id,'Password errata')

@bot.message_handler(content_types = ["text"])
def login(message):
    if flag[chat_id] == 0:
        if len(message.text) == 6 and message.text.isnumeric():
            bot.reply_to(message, "Matricola inserita: "+message.text)
            global matricola
            matricola[chat_id] = message.text
            db_check_mat(matricola,message)
        else:
            bot.reply_to(message, "La matricola che hai inserito non è di 6 numeri")
    elif logged == 0:
        db_check_psw(matricola,message.text,message)
    else:
        bot.reply_to(message, "Utilizza soltanto i bottoni")
        homepage(message)


def homepage(message):
    markup_home = types.InlineKeyboardMarkup()
    markup_home.row_width = 1
    markup_home.add(types.InlineKeyboardButton("Visualizza tutti i corsi", callback_data="lezioni"),
                            types.InlineKeyboardButton("Visualizza le tue prenotazioni", callback_data="prenotazioni"))
    markup_home.add(types.InlineKeyboardButton("Esci",callback_data="esci"))
    bot.send_message(chat_id,"Questa è la tua homepage "+str(matricola[chat_id])+" seleziona un comando: ",reply_markup=markup_home)

@bot.callback_query_handler(func=lambda query: query.data == "lezioni")
def scelta_lezioni(message):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Corsi del primo anno", callback_data="primo"),
                            types.InlineKeyboardButton("Corsi del secondo anno", callback_data="secondo"))
    markup.add(types.InlineKeyboardButton("Torna indietro", callback_data="indietro_home"))
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
    bot.send_message(chat_id,"Lista delle lezioni del primo anno, cliccane una per prenotarti e avere informazioni aggiuntive: ",reply_markup=markup_secondo)

@bot.callback_query_handler(func=lambda call: call.data == "indietro")
def indietro(call):
    scelta_lezioni(call)

@bot.callback_query_handler(func=lambda call: call.data == "indietro_lez1")
def indietro1(call):
    lista_lezioni_primo(call)

@bot.callback_query_handler(func=lambda call: call.data == "indietro_home")
def indietro2(call):
    homepage(call)

@bot.callback_query_handler(func=lambda call: call.data == "indietro_lez2")
def indietro3(call):
    lista_lezioni_secondo(call)


@bot.callback_query_handler(func=lambda call: call.data in id_lez)#gestire tutti i numeri non solo 1 per prenotazione
def lezione(call):
    cursor.execute('SELECT * FROM lezioni WHERE id LIKE ?',(call.data,))
    roba = cursor.fetchall()
    global id_lez_corrente
    id_lez_corrente = call.data
    lez_info(roba)
    markup_lez = types.InlineKeyboardMarkup()
    markup_lez.row_width = 2
    if int(call.data) > 11:
        markup_lez.add(types.InlineKeyboardButton("Torna indietro",callback_data="indietro_lez1"))
    else:
        markup_lez.add(types.InlineKeyboardButton("Torna indietro",callback_data="indietro_lez2"))
    cursor.execute('SELECT COUNT(posto) FROM prenotazioni WHERE matricola LIKE ? and id_lezione LIKE ?',(matricola[chat_id],id_lez_corrente,))
    if cursor.fetchone()[0] == 0:
        markup_lez.add(types.InlineKeyboardButton("Prenotati",callback_data="prenotazione"))
    else:
        markup_lez.add(types.InlineKeyboardButton("Cancella prenotazione",callback_data="c"+id_lez_corrente))#gestire!!!!!!!!
    bot.send_message(chat_id,"Scegli: ",reply_markup=markup_lez)

def lez_info(roba):
    bot.send_message(chat_id,"Corso: "+str(roba[0][1])+"\nData e ora inizio: "+str(roba[0][2])+"\nAula: "+str(roba[0][3])+"\nDocente: "+str(roba[0][4])+"\nPosti disponibili: "+str(roba[0][5]))


@bot.callback_query_handler(func=lambda call: call.data == "prenotazione")
def prenotazione(call):
    markup_pren = types.InlineKeyboardMarkup()
    cursor.execute('SELECT posto FROM prenotazioni WHERE id_lezione LIKE ?',(id_lez_corrente,))
    roba = cursor.fetchall()
    postii = []
    for i in roba:
        postii.append(i[0])
    for i in range(1,21):
        if i not in postii:
            markup_pren.add(types.InlineKeyboardButton(str(i),callback_data="p"+str(i)))
    markup_pren.row_width = 5
    markup_pren.add(types.InlineKeyboardButton("Torna indietro",callback_data=id_lez_corrente))
    bot.send_message(chat_id,"Scegli un posto disponibile: ",reply_markup=markup_pren)

@bot.callback_query_handler(func=lambda call: call.data in id_posto)
def nuova_prenotazione(call):
    call.data = call.data.replace('p', '')
    cursor.execute('INSERT INTO prenotazioni (matricola, id_lezione, posto) VALUES (?,?,?)',(matricola[chat_id],id_lez_corrente,call.data,))
    conn.commit()
    cursor.execute('UPDATE lezioni SET posti_disponibili = posti_disponibili - 1 WHERE id LIKE ? and posti_disponibili > 0',(id_lez_corrente,))
    conn.commit()
    bot.send_message(chat_id,"Posto numero " + call.data+ " prenotato!")
    homepage(call)


@bot.callback_query_handler(func=lambda call: call.data == "prenotazioni")
def prenotazioni(call):
    cursor.execute('SELECT * FROM prenotazioni WHERE matricola LIKE ? ',(matricola[chat_id],))
    roba = cursor.fetchall()
    markup_canc = {}
    a = 0
    for i in roba:
        cursor.execute('SELECT * FROM lezioni WHERE id LIKE ?',(i[2],))
        info = cursor.fetchall()
        lez_info(info)
        bot.send_message(chat_id,"Il tuo posto prenotato è il numero: "+str(i[3]))
        markup_canc[a] = types.InlineKeyboardMarkup()
        markup_canc[a].row_width = 1
        markup_canc[a].add(types.InlineKeyboardButton("Cancella prenotazione",callback_data="c"+str(i[2])))#GESTIONE DA FARE
        bot.send_message(chat_id,"-",reply_markup=markup_canc[a])
        a = a + 1
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(types.InlineKeyboardButton("Torna indietro",callback_data="indietro_home"))
    bot.send_message(chat_id,"-",reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in id_cancella)
def cancella(call):
    call.data = call.data.replace('c', '')
    cursor.execute('DELETE FROM prenotazioni WHERE matricola LIKE ? and id_lezione LIKE ?',(matricola[chat_id],call.data,))
    conn.commit()
    cursor.execute('UPDATE lezioni SET posti_disponibili = posti_disponibili + 1 WHERE id LIKE ? and posti_disponibili < 20',(call.data,))
    conn.commit()
    bot.send_message(chat_id,"Prenotazione cancellata")
    homepage(call)


@bot.callback_query_handler(func=lambda call: call.data == "esci")
def esci(call):
    bot.send_message(chat_id,"Logout effettuato, premere /start")
    global logged
    logged = 0

bot.infinity_polling()
