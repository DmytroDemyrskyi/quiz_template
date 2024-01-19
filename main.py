import random
import time

import requests
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import telebot
from telebot import types

TOKEN = 'your_token'

bot = telebot.TeleBot(TOKEN)

Base = declarative_base()


class MainTable(Base):
    __tablename__ = "test_table"
    userid = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    phone = Column(String)
    data_time = Column(Integer)
    status = Column(String)
    error = Column(String)
    step = Column(String)
    age = Column(String)


engine = create_engine(
    "your_connect_credentials",
)

Session = sessionmaker(bind=engine)
session = Session()


def generate_random_ip():
    min_ip = "101.99.128.0"
    max_ip = "101.99.255.255"

    min_ip = int(''.join(format(int(x), '02x') for x in min_ip.split('.')), 16)
    max_ip = int(''.join(format(int(x), '02x') for x in max_ip.split('.')), 16)

    random_ip = random.randint(min_ip, max_ip)

    generated_ip = '.'.join(str((random_ip >> (8 * i)) & 0xFF) for i in range(3, -1, -1))

    return generated_ip


def sender(user_id):
    with Session() as session:
        result = session.query(MainTable).filter_by(userid=user_id).first()

    first_name = result.name
    last_name = result.lastname
    phone = result.phone
    ip = generate_random_ip()

    url = 'https://api.example.com/api/leads/'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = {
        'domain_name': 'telegram.me',
        'first_name': first_name,
        'last_name': last_name,
        'ip': ip,
        'phone': phone,
        'answers': '',
        'click_id': f"pybot{random.randint(10000000, 99999999)}",
        'utm_campaign': '',
        'utm_content': '',
        'utm_medium': '',
        'utm_source': '',
        'utm_term': '',
        'offer': '32104660860125185',
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print("Request successfully executed")
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")


def state_controller(user_id, firstname):
    unix_time = int(time.time())
    with Session() as session:
        try:
            data = {
                'user_id': user_id,
                'name': firstname,
                'lastname': '',
                'phone': '',
                'data_time': unix_time,
                'status': 'Start',
                'error': '',
                'step': 'None',
                'age': '',
            }

            existing_record = (
                session.query(MainTable)
                .filter_by(userid=data["user_id"])
                .first()
            )
            if existing_record:
                step_value = existing_record.step
                print('___')
                print("Step value:", step_value)
                return step_value
            else:
                unix_time = int(time.time())
                print(data)
                new_record = MainTable(
                    userid=data["user_id"],
                    name=data["name"],
                    lastname=data["lastname"],
                    phone="-",
                    data_time=unix_time,
                    status=data["status"],
                    error="",
                    step=data["step"],
                    age=data["age"],
                )
                session.add(new_record)
                session.commit()
                step_value = data["step"]
                return step_value
        except Exception as e:
            print("Error:", str(e))


@bot.message_handler(commands=['restart'])
def handle_start(message):
    user_id = message.from_user.id
    firstname = message.from_user.username
    step_value = state_controller(user_id, firstname)

    with Session() as session:
        session.query(MainTable).filter_by(userid=user_id).update(
            {MainTable.step: 'None', MainTable.status: 'Start'})
        session.commit()


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    firstname = message.from_user.username
    step_value = state_controller(user_id, firstname)

    if step_value == "None":
        bot.send_photo(message.chat.id, open('images/start.png', 'rb'))

        text = "Embark on a journey of discovery! Click 'Next' to start the quiz."

        inline_keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Next", callback_data="Next")
        inline_keyboard.add(button)

        bot.send_message(message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'Start'})
            session.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    firstname = call.message.from_user.username
    step_value = state_controller(user_id, firstname)
    if call.data == "Next" and step_value == "Start":
        bot.send_message(call.message.chat.id, "Step 1 of 6")
        bot.send_photo(call.message.chat.id, open('images/1.png', 'rb'))

        text = "Which ancient civilization could have built these ruins?"

        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Maya", callback_data="Maya"),
            types.InlineKeyboardButton(text="Roman Empire", callback_data="Roman Empire"),
            types.InlineKeyboardButton(text="Ancient Egypt", callback_data="Ancient Egypt"),
            types.InlineKeyboardButton(text="Atlantis", callback_data="Atlantis"),
        ]
        inline_keyboard.add(*buttons)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        bot.send_message(call.message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update(
                {MainTable.step: 'quest-1', MainTable.status: 'In progress'})
            session.commit()

    if call.data in ["Maya", "Roman Empire", "Ancient Egypt", "Atlantis"] and step_value == "quest-1":
        bot.send_message(call.message.chat.id, "Step 2 of 6")
        bot.send_photo(call.message.chat.id, open('images/2.png', 'rb'))

        text = "Which animal is depicted in this photo?"

        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Lion", callback_data="Lion"),
            types.InlineKeyboardButton(text="Tiger", callback_data="Tiger"),
            types.InlineKeyboardButton(text="Jaguar", callback_data="Jaguar"),
            types.InlineKeyboardButton(text="Cheetah", callback_data="Cheetah"),
        ]
        inline_keyboard.add(*buttons)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        bot.send_message(call.message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'quest-2'})
            session.commit()

    if call.data in ["Lion", "Tiger", "Jaguar", "Cheetah"] and step_value == "quest-2":
        bot.send_message(call.message.chat.id, "Step 3 of 6")
        bot.send_photo(call.message.chat.id, open('images/3.png', 'rb'))

        text = "In which country is this castle located?"

        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="France", callback_data="France"),
            types.InlineKeyboardButton(text="Germany", callback_data="Germany"),
            types.InlineKeyboardButton(text="Scotland", callback_data="Scotland"),
            types.InlineKeyboardButton(text="Spain", callback_data="Spain"),

        ]
        inline_keyboard.add(*buttons)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        bot.send_message(call.message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'quest-3'})
            session.commit()

    if call.data in ["France", "Germany", "Scotland", "Spain"] and step_value == "quest-3":
        bot.send_message(call.message.chat.id, "Step 4 of 6")
        bot.send_photo(call.message.chat.id, open('images/4.png', 'rb'))

        text = "What is the name of this type of flower?"

        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Rose", callback_data="Rose"),
            types.InlineKeyboardButton(text="Tulip", callback_data="Tulip"),
            types.InlineKeyboardButton(text="Orchid", callback_data="Orchid"),
            types.InlineKeyboardButton(text="Peony", callback_data="Peony"),
        ]
        inline_keyboard.add(*buttons)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        bot.send_message(call.message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'quest-4'})
            session.commit()

    if call.data in ["Rose", "Tulip", "Orchid", "Peony"] and step_value == "quest-4":
        bot.send_message(call.message.chat.id, "Step 5 of 6")
        bot.send_photo(call.message.chat.id, open('images/5.png', 'rb'))

        text = "Which historical event occurred at this location?"

        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Fall of the Berlin Wall", callback_data="Fall of the Berlin Wall"),
            types.InlineKeyboardButton(text="Signing of the Declaration of Independence",
                                       callback_data="Signing of the Declaration of Independence"),
            types.InlineKeyboardButton(text="Coronation of Elizabeth II", callback_data="Coronation of Elizabeth II"),
            types.InlineKeyboardButton(text="Apollo 11 Moon Landing", callback_data="Apollo 11 Moon Landing"),

        ]
        inline_keyboard.add(*buttons)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        bot.send_message(call.message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'quest-5'})
            session.commit()

    if call.data in ["Fall of the Berlin Wall", "Signing of the Declaration of Independence",
                     "Coronation of Elizabeth II", "Apollo 11 Moon Landing"] and step_value == "quest-5":
        bot.send_message(call.message.chat.id, "Step 6 of 6")
        bot.send_photo(call.message.chat.id, open('images/6.png', 'rb'))

        text = "Which element is represented in this chemical model?"

        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Carbon", callback_data="Carbon"),
            types.InlineKeyboardButton(text="Oxygen", callback_data="Oxygen"),
            types.InlineKeyboardButton(text="Hydrogen", callback_data="Hydrogen"),
            types.InlineKeyboardButton(text="Nitrogen", callback_data="Nitrogen"),
        ]
        inline_keyboard.add(*buttons)

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        bot.send_message(call.message.chat.id, text, reply_markup=inline_keyboard)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'quest-6'})
            session.commit()

    if call.data in ["Carbon", "Oxygen", "Hydrogen", "Nitrogen"] and step_value == "quest-6":
        bot.send_message(call.message.chat.id,
                         "Congratulations on completing the quiz! Please enter your name to save your results")

        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update({MainTable.step: 'wait-name'})
            session.commit()


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    firstname = message.from_user.username

    step_value = state_controller(user_id, firstname)

    if step_value == "wait-name":
        bot.send_message(message.chat.id, "Enter your last name")

        name = message.text

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update(
                {MainTable.step: 'wait-lastname', MainTable.name: name})
            session.commit()

    if step_value == "wait-lastname":
        bot.send_message(message.chat.id, "Enter your phone number")

        lastname = message.text

        with Session() as session:
            session.query(MainTable).filter_by(userid=user_id).update(
                {MainTable.step: 'wait-phone', MainTable.lastname: lastname})
            session.commit()

    if step_value == "wait-phone":

        phone = message.text

        phone = ''.join(filter(str.isdigit, str(phone)))

        if 8 <= len(phone) <= 15:
            with Session() as session:
                session.query(MainTable).filter_by(userid=user_id).update(
                    {MainTable.step: 'Final', MainTable.status: 'Done', MainTable.phone: phone})
                session.commit()

            sender(user_id)
            bot.send_message(message.chat.id,
                             "Thank you for completing our quiz and sharing your information. Your input is greatly appreciated!")
        else:
            bot.send_message(message.chat.id, "Enter your correct phone number")

            with Session() as session:
                session.query(MainTable).filter_by(userid=user_id).update(
                    {MainTable.step: 'wait-phone', MainTable.status: 'Done',
                     MainTable.phone: phone})
                session.commit()


bot.polling(none_stop=True)
