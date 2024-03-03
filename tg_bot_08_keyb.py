from aiogram import Bot, Dispatcher, types
import asyncio
import requests
from bs4 import BeautifulSoup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import textwrap
from PIL import ImageFont, Image, ImageDraw
from io import BytesIO
import emoji
from transformers import GPT2LMHeadModel, GPT2Tokenizer 

token = "6221685456:AAGY_pnsyHSAI9Hm9ZTDI2-uycHYSjfe5-E"

# Запускаем бота
bot = Bot(token=token)
dp = Dispatcher(bot)

headers = {
    "accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64",
}

# Кнопки рабочего стола, настройки и кнопка продолжить ввиде стрелки, кнопка назад на рабочий стол
inline_cit_arrow = InlineKeyboardButton(
    text=f'Продолжить {emoji.emojize(":right_arrow:")}',
    callback_data='foris_A'
    )

inline_cit_N = InlineKeyboardButton(
    text=f'Настройки - {emoji.emojize(":gear:")}',
    callback_data='foris_N'
    )

inline_btn_b = InlineKeyboardButton(
    text='← Вернуться',
    callback_data='buttonb'
    )

inline_kb_cit_N = InlineKeyboardMarkup().add(inline_cit_arrow, inline_cit_N)

# 4 вида клавы для настроек, в завивсимости, что выберет пользователь, клавиатура будет меняться
inline_cit_rus = InlineKeyboardButton(
    text='Русский язык',
    callback_data='foris_r'
    )
inline_cit_eng = InlineKeyboardButton(
    text='Английский',
    callback_data='foris_e'
    )
inline_cit_esp = InlineKeyboardButton(
    text='Испанский',
    callback_data='foris_c'
    )
inline_cit_sticker_m = InlineKeyboardButton(
    text='Sticker',
    callback_data='foris_s'
    )
inline_cit_msg_m = InlineKeyboardButton(
    text='Msg',
    callback_data='foris_m'
    )

#keyboards
inline_kb_cit_v1 = InlineKeyboardMarkup().add(inline_cit_rus, inline_cit_msg_m, inline_btn_b)
inline_kb_cit_v2 = InlineKeyboardMarkup().add(inline_cit_rus, inline_cit_sticker_m, inline_btn_b)
inline_kb_cit_v3 = InlineKeyboardMarkup().add(inline_cit_eng, inline_cit_msg_m, inline_btn_b)
inline_kb_cit_v4 = InlineKeyboardMarkup().add(inline_cit_eng, inline_cit_sticker_m, inline_btn_b)
inline_kb_cit_v5 = InlineKeyboardMarkup().add(inline_cit_esp, inline_cit_msg_m, inline_btn_b)
inline_kb_cit_v6 = InlineKeyboardMarkup().add(inline_cit_esp, inline_cit_sticker_m, inline_btn_b)

# Условные обозначения 
v1 = inline_kb_cit_v1
v2 = inline_kb_cit_v2
v3 = inline_kb_cit_v3
v4 = inline_kb_cit_v4
v5 = inline_kb_cit_v5
v6 = inline_kb_cit_v6

langs = {0: "r", 1: "e", 2: "c"}
type_msg = {0: "m", 1: "s"}

var1 = [langs[0], "m", v1]
var2 = [langs[0], "s", v2]
var3 = [langs[1], "m", v3]
var4 = [langs[1], "s", v4]
var5 = [langs[2], "m", v5]
var6 = [langs[2], "s", v6]


keyboard_N = v1

# Включаем и записываем в баззу данных
db_filename = "test.db"
try:
    dbconn = sqlite3.connect(db_filename)
except sqlite3.Error:
    print(sqlite3.Error)

cur = dbconn.cursor()

@dp.message_handler(commands="stats")
async def stats(msg: types.Message):
    cur.execute('''
            select userid, ps, count(*)
            from user_logs
            group by userid, ps
                ''')
    data = cur.fetchall()
    print(data)
    mes = ''
    
    for userid, ps, cnt in data:
        mes += f'{userid} - {ps}:{cnt}\n' 
    await bot.send_message(msg.from_user.id, mes)

# Запуск с кнопки старт 
@dp.message_handler(commands="start")
async def start(msg: types.Message):
    global keyboard_N, text_for_N
    userid = msg.from_user.id
    print(userid)
    data = ()
    cur.execute('''
            select lang, typemsg
            from setting
            where userid = %s
            ''' % userid)
    
    data = cur.fetchone()
    print(data)
    
    if data is None:
        cur.execute('''
                insert into setting (userid)
                values (%s)
                ''' % userid)
        dbconn.commit()
    else:
        
        if data[0] == 'e' and data[1] == 'msg':
            keyboard_N = v3
        elif data[0] == 'e' and data[1] == 'sticker':
            keyboard_N = v4
        elif data[0] == 'r' and data[1] == 'msg':
            keyboard_N = v1
        elif data[0] == 'r' and data[1] == 'sticker':
            keyboard_N = v2
        #elif data[0] == 'esp' and data[1] == 'txt':
         #   keyboard_N = v1
       # elif data[0] == 'rus' and data[1] == 'sticker':
        #    keyboard_N = v2


        dbconn.commit()
        
    await msg.answer(emoji.emojize(":waving_hand:")
                     + f", {msg.from_user.first_name}. Добро пожаловать в телеграмм бота, который выдает цитаты на разные темы и на разных языках.\n Внизу ты можешь выбрать в настройках нужную тебе конфигурацию отправки сообщения, поэтому рекомендую ознакомится, перед тем как получить уже полноценную цитату в том или ином виде.",
                     reply_markup=inline_kb_cit_N)

# Форис N - обозначает настройки, в настройках нам нужно изменить язык и каким методом отправлять сообщение
# FIXME: emoji doesnt work: russia and USA flags
text_for_N=  f"Здесь ты можешь выбрать настройки отправки цитат: Первая кнопка предназначена для выбора соответствующего языка(" + emoji.emojize(":Russia:") + ", " + emoji.emojize(":United_States:") + ", " + emoji.emojize(":Spain:") + ")." + "\n" + "Вторая кнопка предлагает выбрать способ отправки сообщения: в виде сообщения или стикера"

@dp.callback_query_handler(text='foris_N')
async def process_callback_button1(callback_query: types.CallbackQuery):
    global keyboard_N, text_for_N
    await bot.edit_message_text(
        f"{text_for_N}",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=keyboard_N
        )

@dp.callback_query_handler(text='foris_A')
async def process_callback_button1(callback_query: types.CallbackQuery):
    global keyboard_N, v1, v2, v3, v4
    userid = callback_query.from_user.id
    cur.execute('''
            select count(*) from user_logs
            where userid = %s
            ''' % userid)

    data, = cur.fetchone()

    #FIXME: advertisment work incorrect
    if data % 10 == 0:
        await bot.send_message(userid, "Реклама")

    if keyboard_N == v1 or keyboard_N == v2:
        await bot.edit_message_text(
            "Выбери следующее действие",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=inline_kb1
            )
    elif keyboard_N == v3 or keyboard_N == v4:
        await bot.edit_message_text(
            "Выбери следующее действие",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=inline_kb2
            )
        
    else:
        await bot.edit_message_text(
            "Выбери следующее действие",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=inline_kb2
            )
        
# Начинает перебирать варианты кнопок и их расположение
@dp.callback_query_handler(text_startswith='foris_')
async def settings_N(callback_query: types.CallbackQuery):
    global keyboard_N, text_for_N, var1, var2, var3, var4, var5, var6, v1, v2, v3, v4, v5, v6, text_for_N, langs
    userid = callback_query.from_user.id
    data = ()
    cur.execute("select lang, typemsg from setting where userid = %s" % userid)
    data = cur.fetchone()
    code = callback_query.data[-1]

    print(callback_query.message)
    
    if code == "r" or code == "e" or code == "c":
        number = [number + 1 for number in langs if langs[number] == code]
        number[0] %= 3
        
        print(number, langs[number[0]])
        
        type_m = keyboard_N["inline_keyboard"][0][1]["callback_data"][-1:]
        
        if langs[number[0]] and type_m in var1:
            keyboard_N = v1
        elif langs[number[0]] and type_m in var2:
            keyboard_N = v2
        elif langs[number[0]] and type_m in var3:
            keyboard_N = v3
        elif langs[number[0]] and type_m in var4:
            keyboard_N = v4
        elif langs[number[0]] and type_m in var5:
            keyboard_N = v5
        elif langs[number[0]] and type_m in var6:
            keyboard_N = v6

        print(langs[number[0]], userid)
        await callback_query.message.edit_text(f"{text_for_N}", reply_markup=keyboard_N)
        cur.execute("update setting set lang=%s where userid=%s" % langs[number[0]], userid)

    elif code == "m" or code == "s":
        number = [number + 1 for number in langs if langs[number] == code]
        if number[0] == 2:
            number = 0

        if keyboard_N[0] and type_msg[numner[0]] in var1:
            keyboard_N = v1
        if keyboard_N[0] and type_msg[numner[0]] in var2:
            keyboard_N = v2
        if keyboard_N[0] and type_msg[numner[0]] in var3:
            keyboard_N = v3
        if keyboard_N[0] and type_msg[numner[0]] in var4:
            keyboard_N = v4
        if keyboard_N[0] and type_msg[numner[0]] in var5:
            keyboard_N = v5
        if keyboard_N[0] and type_msg[numner[0]] in var6:
            keyboard_N = v6

        await callback_query.message.edit_text(f"{text_for_N}", reply_markup=keyboard_N)
        cur.execute("update setting set typemsg=%s where userid=%s" % type_msg[number[0]], userid)

    dbconn.commit()

@dp.callback_query_handler(text_startswith='buttonb')
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        text="Выбери следующее действие",
        reply_markup=inline_kb_cit_N
        )

# Создаём кнопки для русского
inline_btn_1 = InlineKeyboardButton(
    text='Рандомная цитата',
    callback_data='button1'
    )
inline_btn_2 = InlineKeyboardButton(
    text='Цитата из книги',
    callback_data='button2'
    )
inline_btn_3 = InlineKeyboardButton(
    text='Цитата с юмором',
    callback_data='button3'
    )
inline_btn_4 = InlineKeyboardButton(
    text='Цитата из стихотворения',
    callback_data='button4'
    )
inline_btn_5 = InlineKeyboardButton(
    text='Цитата из фильма',
    callback_data='button5'
    )
inline_btn_6 = InlineKeyboardButton(
    text='Пословицы и поговорки',
    callback_data='button6'
    )

# Создаем кнопки для английского
inline_btn_7 = InlineKeyboardButton(
    text='Рандомная цитата',
    callback_data='button7'
    )
inline_btn_8 = InlineKeyboardButton(
    text='Цитата из книги',
    callback_data='button8'
    )
inline_btn_9 = InlineKeyboardButton(
    text='Цитата из фильма',
    callback_data='button9'
    )
inline_btn_10 = InlineKeyboardButton(
    text='Историческая цитата',
    callback_data='button10'
    )
inline_btn_11 = InlineKeyboardButton(
    text='Лучшая цитата',
    callback_data='button11'
    )
inline_btn_12 = InlineKeyboardButton(
    text='Цитата успеха',
    callback_data='button12'
    )
inline_btn_13 = InlineKeyboardButton(
    text='Цитата с юмором',
    callback_data='button13'
    )

inline_btn_T = InlineKeyboardButton(
    text='Translate (Перевести цитату)',
    callback_data='button_T'
    )

# Создаём вторую клавиатуру для кнопок уже непосредственно с цитатами, подраздел 2
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1).add(inline_btn_2).add(inline_btn_3).add(inline_btn_4).add(inline_btn_5).add(inline_btn_6).add(inline_btn_b)

inline_kb2 = InlineKeyboardMarkup().add(inline_btn_7).add(inline_btn_8).add(inline_btn_9).add(inline_btn_10).add(inline_btn_11).add(inline_btn_12).add(inline_btn_13).add(inline_btn_b)

# FIXME: ESPA 
inline_kb3 = InlineKeyboardMarkup().add(inline_btn_7).add(inline_btn_8).add(inline_btn_9).add(inline_btn_10).add(inline_btn_11).add(inline_btn_12).add(inline_btn_13).add(inline_btn_b)


inline_kb_T = InlineKeyboardMarkup().add(inline_btn_7).add(inline_btn_8).add(inline_btn_9).add(inline_btn_10).add(inline_btn_11).add(inline_btn_12).add(inline_btn_13).add(inline_btn_T).add(inline_btn_b)

# Обработчик кнопок второй клавиатуры    
@dp.callback_query_handler(text_startswith='button') 
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    global keyboard_N, v1, v2, v3, v4
    
    name_user = callback_query.from_user.first_name
    
    try:
        code = int(callback_query.data[-2:])
    except:
        if callback_query.data[-1].isdigit():
            code = int(callback_query.data[-1])
        else:
            code = callback_query.data[-1]

    if code == 1:
        data_sq(callback_query.from_user.id, "Русская кнопка")

        url = 'http://api.forismatic.com/api/1.0/'
        payload = {'method': 'getQuote', 'format': 'json', 'lang': 'ru'} 
        res = requests.get(url, params=payload)
        res = res.json()
        res = res["quoteText"]

        await send_quotes(res, code, callback_query)
      
    elif code == 2:
        data_sq(callback_query.from_user.id, "Русская кнопка")
        
        headers = {"content-type": "application/json"}
        response = requests.post(url='https://randomall.ru/api/gens/6381', json={}, headers=headers)
        text = response.json()["msg"]
        await send_quotes(text, code, callback_query)
        
    elif code == 3:
        data_sq(callback_query.from_user.id, "Русская кнопка")

        url = 'https://randstuff.ru/joke/'
        response = requests.post(url=url)
        soup = BeautifulSoup(response.text, "html.parser")
        citata = soup.find("table", class_="text")
        citata = citata.text
        citata1 = citata.replace('<table class="text"><tr><td>', '').replace("</td></tr></table>", '')
        
        await send_quotes(citata1, code, callback_query)
        
    elif code == 4:
        text =  request_to_citaty_info("quote_poetry")
        print(text)
        await send_quotes(text, code, callback_query)

    elif code == 5:
        text = request_to_citaty_info("quote_film")
        await send_quotes(text, code, callback_query)
        
    elif code == 6:
        text = request_to_citaty_info("po")
        await send_quotes(text, code, callback_query)

    elif code == "T":
        translation = translate(callback_query.message.text)
        await bot.edit_message_text(
            translation,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=inline_kb2
            )
    
    elif code == 7:
        data_sq(callback_query.from_user.id, "Английская кнопка")

        url = 'https://favqs.com/api/qotd'
        payload = {'method': 'getQuote', 'format': 'json', 'lang': 'ru'} 
        text = requests.get(url, params=payload)
        text = text.json()
        text = text['quote']['body']

        await send_quotes(text, code, callback_query)

    elif code == 8:
        url = 'https://www.litquotes.com/Random-Quote.php'
        response = requests.post(url=url)
        soup = BeautifulSoup(response.text, "html.parser")
        citata = soup.find("div", class_="purple")
        citata = citata.text

        number_1  = citata.rfind(' - ')
        citata = citata[:number_1]
        
        await send_quotes(citata, code, callback_query)
    
    elif code == 9:
        await english_quotes("movies", code,  callback_query)

    elif code == 10:
        await english_quotes("history", code, callback_query)

    elif code == 11:
        await english_quotes("best", code, callback_query)

    elif code == 12:
        await english_quotes("success", code, callback_query)

    elif code == 13:
        await english_quotes("humor", code,  callback_query)

    else:
        pass

async def send_quotes(message, code, callback_query):
    global keyboard_N

    if code <= 6:
        r_m = inline_kb1
    else:
        r_m = inline_kb_T

    if keyboard_N == v2 or keyboard_N == v4 or keyboard_N == v6:
        sticker = sticker_made(message, '')
        await bot.edit_message_text(
            "===============",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id
            )
        await bot.send_sticker(
            callback_query.from_user.id,
            sticker
            )
        await bot.send_message(
            callback_query.from_user.id,
            "===============",
            reply_markup=r_m
            )
    else:
        if 'Выбери' in callback_query.message["text"]:
            await bot.edit_message_text(
                "===============",
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id
                )
        else:
            await bot.edit_message_text(
                "==============",
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id
                )

        await bot.send_message(callback_query.from_user.id, message)
        await bot.send_message(callback_query.from_user.id, "===============", reply_markup=r_m)

        
async def request_to_citaty_info(type_r):
    data_sq(callback_query.from_user.id, "Русская кнопка")

    name_user = callback_query.from_user.first_name
    url = 'https://citaty.info/random'
    payload = {"form-select": type_r} 
    response = requests.post(url=url, headers=headers, json=payload)
    soup = BeautifulSoup(response.text, "html.parser")
    citata = soup.find("div", class_="field-item even last").find_all("p")
    citata = citata[0].text
    
    return citata

async def english_quotes(category, code, callback_query):
    global keyboard_N
    category = category
    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
    response = requests.get(
        api_url,
        headers={'X-Api-Key': 'IAlxp6bOnax1CdLgmPuRjA==wcTeujpGsrdkZXnD'}
        )

    if response.status_code == requests.codes.ok:
        result = response.text
    else:
        print("Error:", response.status_code, response.text)

    message = (result[result.find(":") + 3: result.find("author") - 4])
    last_msg = callback_query.message.text

    await send_quotes(message, code, callback_query)
@dp.message_handler()
async def echo_message(msg: types.Message):
    name_user = msg.from_user.username
    text = msg.text

    # sticker = sticker_made(text, name_user)
    # FIXME: bot send sticker in the form of stream of bytes
    await bot.send_sticker(
        msg.from_user.id,
        sticker_made(text, name_user)
        )

def translate(message):
    global keyboard_N, v1, v2, v3, v4
    from translate import Translator
    if keyboard_N == v3:
        translator = Translator(from_lang='en', to_lang='ru')
        translation = translator.translate(message)
        return translation
    
# FIXME: Doesnt work
def sticker_made(text, author):
    AVATAR_SIZE = 50
    AVATAR_MARGIN = 5
    BUBBLE_X_START = AVATAR_SIZE + AVATAR_MARGIN
    BUBBLE_RADIUS = 10 # отступ от начала
    BUBBLE_PADDING = BUBBLE_RADIUS # отступ до конца 
    TEXT_X_START= BUBBLE_X_START + BUBBLE_PADDING
    DEFAULT_EMOJI="\U0001F4AC"  # :speech_balloon:

    text = textwrap.wrap(text, width=30)

    # Импортируем шрифт, кегль 26
    FONT_SIZE=26
    OPEN_SANS = ImageFont.truetype('arial.ttf', FONT_SIZE)

    # Получаем высоту шрифта
    (font_width, font_height), (offset_x, offset_y) = OPEN_SANS.font.getsize(text[0])

    # Рассчитываем высоту картинки
    height = font_height * (len(text) + 1) + 2 * BUBBLE_RADIUS + offset_y * 2

    width = 512 - AVATAR_SIZE

    if height > 512:
        raise OverflowError("Image too big")

    # Создаем изображение
    img = Image.new('RGBA', (width, height), color=(255, 255, 255, 0))

    draw = ImageDraw.Draw(img)

    ascent, descent = OPEN_SANS.getmetrics()

    draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill="blue")


    draw.rounded_rectangle((BUBBLE_X_START, 0, width, height), fill="white", radius=BUBBLE_RADIUS)

    draw.text(
            (TEXT_X_START, BUBBLE_PADDING), 
            author, 
            fill="red", 
            font=OPEN_SANS
        )

    offset = BUBBLE_PADDING + font_height
    for line in text:
        draw.text((TEXT_X_START, offset), line, fill="brown", font=OPEN_SANS)
        offset += font_height

    sticker = BytesIO()
    img.save(sticker, 'PNG')
    sticker.seek(0)

    return sticker

def data_sq(userid, name_of_button):
    """
    Log user actions in database

    Parameters
    ----------
        userid : int
            user id
        name_of_button : str
            name of button that was clicked by the user
    """
    cur.execute('''
            insert into user_logs (Userid, ps)
            values (?, ?)
            ''', (userid, name_of_button))
    
    dbconn.commit()

async def main():
    """
    Runs server main loop
    """

    await dp.start_polling(bot)

asyncio.run(main())
