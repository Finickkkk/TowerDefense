from config import TOKEN
from telebot.types import Message, ReplyKeyboardMarkup as rkm, ReplyKeyboardRemove as rkr
from data_base import *
import telebot
import asyncio
import random

bot = telebot.TeleBot(TOKEN)
temp = {}
clear = rkr()


class Tower:
    def __init__(self):
        self.hp = 100
        self.damage = 35

    def info(self, user_id, m: Message):
        player = db.read("user_id", user_id)
        txt = f"{player[1]}, у башни, которую ты защищаешь {player[2]} прочности и {player[-1]} единиц атаки"
        print(1, 2, sep="__", end="!!!")
        bot.send_message(m.chat.id, txt)


class Enemy:
    enemies = {
        "волна скелетов": [random.randint(50, 80), random.randint(25, 30)],
        "волна призраков": [random.randint(35, 50), random.randint(17, 33)],
        "волна зомби": [random.randint(50, 60), random.randint(25, 30)],
        "лич": [random.randint(60, 75), random.randint(30, 35)]
    }

    def __init__(self):
        self.name = random.choice(list(self.enemies))
        self.hp = self.enemies[self.name][0]
        self.damage = self.enemies[self.name][1]


tower = Tower()


@bot.message_handler(["start"])
def start(m: Message):
    if is_new_player(m):
        temp[m.chat.id] = {}
        reg_1(m)
    else:
        menu(m)


@bot.message_handler(["menu"])
def menu(m: Message):
    txt = "Ты в главном меню, выбери, что хочешь сделать\n\n/defence - защищать башню\n/stats - характеристики"
    bot.send_message(m.chat.id, txt)


@bot.message_handler(["stats"])
def stats(m: Message):
    tower.info(m.chat.id, m)
    asyncio.run(asyncio.sleep(3))
    menu(m)


@bot.message_handler(["defence"])
def defence(m: Message):
    enemy = Enemy()
    bot.send_message(m.chat.id, f"Держись, на тебя нападает {enemy.name}. У врага {enemy.hp}❤️ и {enemy.damage}⚔️")
    fight_handler(m, enemy)


def fight_handler(m: Message, enemy: Enemy):
    if attack_enemy(m, enemy):
        if attack_tower(m, enemy):
            fight_handler(m, enemy)
        else:
            asyncio.run(asyncio.sleep(2))
            kb = rkm(True)
            kb.row("Укрепить стены", "Выставить стражников")
            bot.send_message(m.chat.id, f"Укрепи стены для восстановления башни или выстави стражников для "
                                        f"улучшения защиты", reply_markup=kb)
            bot.register_next_step_handler(m, reg_3, kb)


def attack_tower(m: Message, enemy: Enemy):
    player = db.read("user_id", m.chat.id)
    asyncio.run(asyncio.sleep(1))
    enemy.hp -= player[3]
    if enemy.hp <= 0:
        bot.send_message(m.chat.id, "Ты отбился от этой волны, не расслабляйся, скоро прибудет еще волна")
        return False
    else:
        bot.send_message(m.chat.id, f"{enemy.name} - ❤️{round(enemy.hp, 1)}")
        return True


def attack_enemy(m: Message, enemy: Enemy):
    player = db.read("user_id", m.chat.id)
    asyncio.run(asyncio.sleep(1))
    player[2] -= enemy.damage
    db.write(player)
    if player[2] <= 0:
        bot.send_message(m.chat.id, "Ты и твоя башня повержены, прощай")
        asyncio.run(asyncio.sleep(3))
        db.delete_row("user_id", m.chat.id)
        start(m)
        return
    else:
        bot.send_message(m.chat.id, f"У тебя ❤️{round(player[2], 1)}")
        return True


def is_new_player(m: Message):
    players = db.read_all()
    for player in players:
        if player[0] == m.chat.id:
            return False
    return True


def reg_1(m: Message):
    bot.send_message(m.chat.id, "Привет, ты попал в игру. Как тебя зовут?")
    bot.register_next_step_handler(m, reg_2)


def reg_2(m: Message):
    db.write([m.chat.id, m.text, tower.hp, tower.damage])
    bot.send_message(m.chat.id, "Вы успешно зарегистрированы")
    asyncio.run(asyncio.sleep(3))
    menu(m)


def reg_3(m: Message, kb):
    player = db.read("user_id", m.chat.id)
    if m.text == "Укрепить стены":
        player[2] += random.randint(50, 70)
        db.write(player)
        bot.send_message(m.chat.id, f"Ты укрепил стены, теперь прочность твоей башни: {player[2]}❤️",
                         reply_markup=clear)
        defence(m)
    elif m.text == "Выставить стражников":
        player[3] += random.randint(20, 30)
        db.write(player)
        bot.send_message(m.chat.id, f"Ты поставил стражников, теперь атака твоей башни: {player[3]}⚔️",
                         reply_markup=clear)
        defence(m)
    else:
        bot.send_message(m.chat.id, "Нажми на кнопку", reply_markup=kb)
        bot.register_next_step_handler(m, reg_3, kb)


bot.infinity_polling()