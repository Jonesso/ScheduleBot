import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import requests
from bs4 import BeautifulSoup
import json
import PIL.Image as Image
import matplotlib
import matplotlib.pyplot as plt
import re
import datetime
import math
import random
from pprint import pprint

# Test bot on https://vk.com/club195096600


# start session
vk_session = vk_api.VkApi(token='28cea37f8313fb3127847454f0cd20c18c136d378aefa5334ce0193b47ab20606aef94fccac81503d2509')
vk = vk_session.get_api()
upload = VkUpload(vk_session)
longpoll = VkLongPoll(vk_session)

# images
attachments = []
photo = upload.photo_messages(photos='src/kitty.jpg')[0]
attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
kitties = ['src/kitty_love.jpg', 'src/kitty_love2.jpg', 'src/kitty_love3.jpg', 'src/kitty_love4.jpg', 'src/kitty_love5.jpg',
           'src/kitty_love6.jpg', 'src/kitty_love6.jpg', 'src/kitty_love7.jpg', 'src/kitty_love8.jpg', 'src/kitty_love9.jpg',
           'src/kitty_love10.jpg']
doggo = upload.photo_messages(photos='src/dog_love.jpg')[0]

# weather API
weather_api_key = "ada08f64c3f4dfc5e5b043a59ed2bc6f"
weather_s = "{description}, температура: {temp_min}-{temp_max}\u00b0С\n" \
            "Давление: {pressure} мм рт.ст., влажность: {humidity}%\n" \
            "Ветер: {wind_character}, {wind_speed} м/с, {wind_direction}\n"
eng_to_rus = {"Thunderstorm": "гроза", "Drizzle": "морось", "Rain": "дождь", "Snow": "снег",
              "Mist": "туман", "Smoke": "смог", "Haze": "дымка", "Fog": "туман",
              "Dust": "пыль", "Sand": "песчаная буря", "Ash": "пепел",
              "Squall": "шквалистый ветер", "Tornado": "ураган",
              "Clouds": "облачно", "Clear": "ясно"}

# coronavirus table
corona_site = "https://coronavirusstat.ru/country/russia/"
covid_page = requests.get(corona_site)
soup = BeautifulSoup(covid_page.text, "html.parser")
table_rows = soup.findAll("table")[0].find("tbody").findAll("tr")

# MIREA schedule
weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
todays_date = datetime.date.today()
group_regex = r"И[АВКНМ]{1}БО-[0-9]{2}-1[7-9]{1}"
current_group = ""
base_schedule_str = "Расписание на {weekday}, {date}:\n"


def is_group(group):
    return re.search(group_regex, group, re.IGNORECASE) is not None


# schedule for each course
with open("course1_sch.json", "r") as read_file:
    first_course_schedule = json.load(read_file)
with open("course2_sch.json", "r") as read_file:
    second_course_schedule = json.load(read_file)
with open("course2_sch.json", "r") as read_file:
    third_course_schedule = json.load(read_file)

# week num
mirea_site = "https://www.mirea.ru"
mirea_page = requests.get(mirea_site)
soup3 = BeautifulSoup(mirea_page.text, "html.parser")
week_str = soup3.find("div", {"class": "date_text"}).text
nums = [int(s) for s in re.findall(r'\b\d+\b', week_str)]  # find nums in string
current_week = nums[1]
oddity = 1 if current_week % 2 == 0 else 0


def choose_random_kitty():
    kitty_ph = upload.photo_messages(photos=random.choice(kitties))[0]
    return "photo{}_{}".format(kitty_ph["owner_id"], kitty_ph["id"])


def greeting(vk_event):
    # print('New from {}, text = {}'.format(vk_event.user_id, vk_event.text))
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message='Привет, ' + vk.users.get(user_id=vk_event.user_id)[0]['first_name'],
        keyboard=keyboard.get_keyboard(),
        attachment="photo{}_{}".format(doggo["owner_id"], doggo["id"])
    )


def instructions(vk_event):
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message='Инструкция по работе с ботом:\n'
                'Этот бот умеет показывать статистику по COVID-19, выдавать расписание студентов института ИТ в РТУ МИРЭА и сообщать о погоде. '
                'Для каждого раздела есть свои команды. Чтобы увидеть список доступных команд (кнопки) в любое время, отправьте сообщение "бот".\n\n'
                'Список команд бота:\n\n'
                '"Ковид" - статистика по заболеваниям в России за последние сутки и график заболевамости за последние 10 дней,\n\n'
                'Название группы в формате "ИXБО-XX-XX" - основная группа, по которой будет выдаваться расписание (необходимо набирать каждый раз при заходе в диалог с ботом),\n\n'
                '"Какая группа?" - основная группа на данный момент,\n\n'
                '"Какая неделя?" - номер текущей недели, \n\n'
                '"Расписание на сегодня", "Расписание на завтра", "Расписание на эту неделю", "Расписание на следующую неделю" - подробное расписание занятий на соответствующий период,\n\n'
                '"Бот <группа>" - изменить основную группу и показать ее расписание на выбранный период,\n\n'
                '"Бот <день недели>" - расписание для нечетной и четной недели в соответствующий день у основной группы,\n\n'
                '"Бот <день недели> <группа>" - расписание для нечетной и четной недели в соответствующий день у указанной группы,\n\n'
                '"Погода" - погода в Москве на выбранный период времени.\n\n'

                'Если команда не будет совпадать со списком перечисленных, бот кинет обидку. Удачи!',
    )


def show_functions(vk_event):
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Показать...",
        keyboard=keyboard.get_keyboard()
    )


def weather_keyboard(vk_event):
    temp_keyboard = VkKeyboard(one_time=True)
    temp_keyboard.add_button(label='сейчас', color=VkKeyboardColor.PRIMARY)
    temp_keyboard.add_button(label='сегодня', color=VkKeyboardColor.POSITIVE)
    temp_keyboard.add_button(label='завтра', color=VkKeyboardColor.POSITIVE)
    temp_keyboard.add_line()
    temp_keyboard.add_button(label='на 5 дней', color=VkKeyboardColor.POSITIVE)
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Показать погоду в Москве",
        keyboard=temp_keyboard.get_keyboard()
    )


def unknown(vk_event):
    vk.messages.send(
        user_id=vk_event.user_id,
        attachment=','.join(attachments),
        random_id=get_random_id(),
        message='Неизвестная команда. Чтобы посмотреть список допустимых команд, отправьте "инструкция" или "бот"'
    )


def covid_plot(days, cured, active, deaths):
    matplotlib.use('TkAgg')
    plt.style.use('seaborn-dark')
    figure = plt.figure()
    plt.plot(days, cured, color="#7ECE37", label="Вылечено")
    plt.plot(days, active, color="#8B0000", label="Активных")
    plt.plot(days, deaths, color="#000000", label="Умерло")
    plt.tick_params(axis='x', labelrotation=15)
    plt.title("Россия - детальная статистика - коронавирус")
    plt.xlabel("Даты")
    plt.ylabel("Кол-во человек")
    plt.grid()
    plt.legend()
    figure.savefig('covid.png')
    figure.clear()


def send_covid_info(vk_event, request_res=table_rows):
    base_string = "По состоянию на {current_date}\n" \
                  "Случаев: {all_cases} ({new_cases} за сегодня)\n" \
                  "Активных: {all_active} ({new_active} за сегодня)\n" \
                  "Вылечено: {all_cured} ({new_cured} за сегодня)\n" \
                  "Умерло: {all_deaths} ({new_deaths} за сегодня)"

    cases = []
    active = []
    cured = []
    dead = []
    new_today = []
    dates = []
    now = datetime.datetime.now().strftime("%d-%m %H:%M")

    for row in request_res:
        all_nums = row.findAll("td")
        dates.append(row.find("th").get_text())
        for i in range(len(all_nums)):
            total, new, percent = all_nums[i].get_text().split()
            if row == request_res[0]:
                new_today.append(new)

            if i == 0:
                active.append(int(total))
            elif i == 1:
                cured.append(int(total))
            elif i == 2:
                dead.append(int(total))
            elif i == 3:
                cases.append(int(total))

    final_str = base_string.format(current_date=now, all_cases=cases[0], new_cases=new_today[3], all_active=active[0],
                                   new_active=new_today[0], all_cured=cured[0], new_cured=new_today[1],
                                   all_deaths=dead[0], new_deaths=new_today[2])

    covid_plot(dates[::-1], cured[::-1], active[::-1], dead[::-1])
    graph = upload.photo_messages(photos='covid.png')[0]

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=final_str,
        attachment="photo{}_{}".format(graph["owner_id"], graph["id"])
    )


def wind_degrees_to_name(degree):
    if 0 <= degree < 45 or degree == 360:
        return "северный"
    elif 45 <= degree < 90:
        return "северо-восточный"
    elif 90 <= degree < 135:
        return "восточный"
    elif 135 <= degree < 180:
        return "юго-восточный"
    elif 180 <= degree < 225:
        return "южный"
    elif 225 <= degree < 270:
        return "юго-западный"
    elif 270 <= degree < 315:
        return "западный"
    elif 315 <= degree < 360:
        return "северо-западный"


def wind_speed_to_desc(speed):
    if 0 <= speed < 0.3:
        return "штиль"
    elif 0.3 <= speed < 3.3:
        return "легкий"
    elif 3.4 <= speed < 5.5:
        return "слабый"
    elif 5.5 <= speed < 10.8:
        return "умеренный"
    elif 10.8 <= speed < 20.8:
        return "сильный"
    elif 20.8 <= speed < 32.7:
        return "шторм"
    elif speed >= 32.7:
        return "ураган"


def pressure_in_mm(pressure):
    return math.floor(pressure * 100 / 133)


def current_weather(vk_event):
    weather_site = "http://api.openweathermap.org/data/2.5/weather?q=moscow&appid=" + weather_api_key + "&units=metric&lang=ru"
    weather_response = requests.get(weather_site)
    weather_info = weather_response.json()

    new_s = weather_s.format(description=weather_info["weather"][0]["description"].capitalize(),
                             temp_min=round(weather_info["main"]["temp_min"]),
                             temp_max=round(weather_info["main"]["temp_max"]),
                             pressure=pressure_in_mm(weather_info["main"]["pressure"]),
                             humidity=weather_info["main"]["humidity"],
                             wind_character=wind_speed_to_desc(weather_info["wind"]["speed"]),
                             wind_speed=round(weather_info["wind"]["speed"]),
                             wind_direction=wind_degrees_to_name(weather_info["wind"]["deg"]))

    image = requests.get("http://openweathermap.org/img/w/" + weather_info["weather"][0]["icon"] + ".png", stream=True)

    with open("single.png", "wb") as f:
        f.write(image.content)

    weather_pic = upload.photo_messages(photos='single.png')[0]
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Погода в Москве: {main}\n".format(main=eng_to_rus[weather_info["weather"][0]["main"]]),
        attachment="photo{}_{}".format(weather_pic["owner_id"], weather_pic["id"])
    )
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=new_s
    )


def day_weather(vk_event, next_day=False):
    weath = ""
    weather_site = "http://api.openweathermap.org/data/2.5/forecast?q=moscow&appid=" + weather_api_key + "&units=metric&lang=ru"
    weather_response = requests.get(weather_site)
    weather_info = weather_response.json()
    start_index = 0
    img = Image.new('RGB', (200, 50))
    pic_x = 0

    if next_day:
        for i in range(9):
            if int(weather_info["list"][i]["dt_txt"].split()[1].split(':')[0]) == 0 and i != 0:
                start_index = i

    for daytime in range(start_index, start_index + 7, 2):
        hour = int(weather_info["list"][daytime]["dt_txt"].split()[1].split(':')[0])
        if 0 <= hour < 6:
            weath += "------------------НОЧЬ------------------\n"
        elif 6 <= hour < 12:
            weath += "------------------УТРО------------------\n"
        elif 12 <= hour < 18:
            weath += "------------------ДЕНЬ------------------\n"
        elif 18 <= hour < 24:
            weath += "------------------ВЕЧЕР------------------\n"

        image = requests.get(
            "http://openweathermap.org/img/w/" + weather_info["list"][daytime]["weather"][0]["icon"] + ".png",
            stream=True)
        with open("file_.png", "wb") as f:
            f.write(image.content)
        img_pt = Image.open("file_.png")
        img.paste(img_pt, (pic_x, 0))
        pic_x += 50

        weath += weather_s.format(
            description=weather_info["list"][daytime]["weather"][0]["description"].capitalize(),
            temp_min=round(weather_info["list"][daytime]["main"]["temp_min"]),
            temp_max=round(weather_info["list"][daytime]["main"]["temp_max"]),
            pressure=pressure_in_mm(weather_info["list"][daytime]["main"]["pressure"]),
            humidity=weather_info["list"][daytime]["main"]["humidity"],
            wind_character=wind_speed_to_desc(weather_info["list"][daytime]["wind"]["speed"]),
            wind_speed=round(weather_info["list"][daytime]["wind"]["speed"]),
            wind_direction=wind_degrees_to_name(weather_info["list"][daytime]["wind"]["deg"]))
        weath += "\n"

    # pprint(weather_info)

    img.save("day_weather.png")
    weather_pic = upload.photo_messages(photos='day_weather.png')[0]

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Погода в Москве на {day}".format(day="завтра" if next_day else "сегодня"),
        attachment="photo{}_{}".format(weather_pic["owner_id"], weather_pic["id"])
    )

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=weath
    )


def week_weather(vk_event):
    weather = ""
    weather_site = "http://api.openweathermap.org/data/2.5/forecast?q=moscow&appid=" + weather_api_key + "&units=metric&lang=ru"
    weather_response = requests.get(weather_site)
    weather_info = weather_response.json()
    # pprint(weather_info)
    night_start_index = 0
    day_start_index = 0
    start_pic_x = 0

    img = Image.new('RGB', (250, 50))

    for i in range(9):
        if int(weather_info["list"][i]["dt_txt"].split()[1].split(':')[0]) == 0:
            night_start_index = i
        if int(weather_info["list"][i]["dt_txt"].split()[1].split(':')[0]) == 12:
            day_start_index = i

    for day in range(day_start_index, len(weather_info["list"]), 8):
        weather += "/ " + str(round(weather_info["list"][day]["main"]["temp"])) + "\u00b0С /"

        image = requests.get(
            "http://openweathermap.org/img/w/" + weather_info["list"][day]["weather"][0]["icon"] + ".png",
            stream=True)
        with open("file.png", "wb") as f:
            f.write(image.content)
        img_part = Image.open("file.png")
        img.paste(img_part, (start_pic_x, 0))
        start_pic_x += 50

    img.save("week_weather.png")
    weather_pic = upload.photo_messages(photos='week_weather.png')[0]

    weather += " ДЕНЬ\n"

    for night in range(night_start_index, len(weather_info["list"]), 8):
        weather += "/  " + str(round(weather_info["list"][night]["main"]["temp"])) + "\u00b0С /"

    weather += " НОЧЬ"

    period_end = todays_date + datetime.timedelta(days=5)

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Погода в Москве c {start_day} до {end_day}".format(start_day=todays_date.strftime("%d.%m"),
                                                                    end_day=period_end.strftime("%d.%m")),
        attachment="photo{}_{}".format(weather_pic["owner_id"], weather_pic["id"])
    )

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=weather
    )


def set_current_group(vk_event, group):
    global current_group
    current_group = str(group).upper()
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Я запомнил, что ты из группы " + current_group
    )


def print_current_group(vk_event):
    if current_group == "":
        s = "Сначала введите номер группы"
    else:
        s = "Показываю расписание группы " + current_group.upper()

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=s
    )


def print_current_week(vk_event):
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message='Идёт ' + str(current_week) + ' неделя'
    )


def choose_schedule(group):
    if group.endswith("19"):
        return first_course_schedule
    elif group.endswith("18"):
        return second_course_schedule
    elif group.endswith("17"):
        return third_course_schedule


def day_schedule(group, day=todays_date, for_next_week=False):
    current_weekday = day.weekday()
    current_weekday_s = weekdays[current_weekday]
    inner_oddity = oddity
    if for_next_week:
        inner_oddity = 1 if oddity == 0 else 0

    s = base_schedule_str.format(
        weekday=current_weekday_s.replace("а", "у") if current_weekday_s.endswith("а") else current_weekday_s,
        date=day.strftime('%d.%m.%Y'))

    if group == "":
        s = "Сначала введите номер группы"
    else:
        curr_schedule = choose_schedule(group)

        lesson_num = 0
        try:
            if current_weekday != 6:  # not Sunday
                for i in range(6):  # amount of lessons
                    lesson_num += 1
                    day_info = list(curr_schedule[group.upper()][current_weekday_s][i][inner_oddity].values())
                    s += str(lesson_num) + ") " + ', '.join(day_info) + '\n'
            else:
                s += curr_schedule[group.upper()][current_weekday_s]
        except KeyError:
            s = "Группы не существует или для нее отсутствует расписание. " \
                "Пожалуйста, отправьте корректное название группы"
    return s


def print_day_schedule(vk_event, group, day=todays_date, next_week=False):
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=day_schedule(group, day, for_next_week=next_week)
    )


def print_week_schedule(vk_event, group, next_week=False):
    msg = ""
    if next_week:
        dates = [todays_date + datetime.timedelta(days=i) for i in
                 range(7 - todays_date.weekday(), 14 - todays_date.weekday())]
    else:
        dates = [todays_date + datetime.timedelta(days=i) for i in
                 range(0 - todays_date.weekday(), 7 - todays_date.weekday())]

    for day in dates:
        if msg != "Сначала введите номер группы\n":
            msg += day_schedule(group, day=day, for_next_week=next_week) + '\n'

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=msg
    )


def weekday_schedule(vk_event, weekday, group):
    msg = ""
    if group == "":
        msg += "Сначала введите номер группы"
    else:
        msg += weekday.capitalize() + ", нечетная неделя:\n"
        curr_sch = choose_schedule(group)
        lesson_num = 0
        try:
            if weekday != "воскресенье":
                for i in range(6):  # amount of lessons
                    lesson_num += 1
                    day_info = list(curr_sch[group][weekday][i][0].values())
                    msg += str(lesson_num) + ") " + ', '.join(day_info) + '\n'
            else:
                msg += curr_sch[group][weekday]

            msg += "\n" + weekday.capitalize() + ", четная неделя:\n"
            lesson_num = 0

            if weekday != "воскресенье":
                for i in range(6):  # amount of lessons
                    lesson_num += 1
                    day_info = list(curr_sch[group][weekday][i][1].values())
                    msg += str(lesson_num) + ") " + ', '.join(day_info) + '\n'
            else:
                msg += curr_sch[group][weekday]
        except KeyError:
            msg = "Группы не существует или для нее отсутствует расписание. " \
                  "Пожалуйста, отправьте корректное название группы"

    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message=msg
    )


def change_group(vk_event, group):
    global current_group
    current_group = group.upper()
    vk.messages.send(
        user_id=vk_event.user_id,
        random_id=get_random_id(),
        message="Показать расписание группы " + group.upper() + "...",
        keyboard=keyboard.get_keyboard()
    )


# BOT APPEARANCE AND BEHAVIOUR

# Buttons
keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Ковид', color=VkKeyboardColor.NEGATIVE)
keyboard.add_button('Погоду', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()  # new line of buttons
keyboard.add_button('Расписание на сегодня', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Расписание на завтра', color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_button('Расписание на эту неделю', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('Расписание на следующую неделю', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('Какая неделя?', color=VkKeyboardColor.DEFAULT)
keyboard.add_button('Какая группа?', color=VkKeyboardColor.DEFAULT)

# Mainloop
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg_words = event.text.lower().split()
        if event.text.lower() == "начать":
            greeting(event)
            instructions(event)
        elif event.text.lower() == "привет":
            greeting(event)
        elif event.text.lower() == "инструкция":
            instructions(event)
        elif event.text.lower() == "ковид":
            send_covid_info(event)
        elif event.text.lower() == "расписание на сегодня":
            print_day_schedule(event, current_group)
        elif event.text.lower() == "расписание на эту неделю":
            print_week_schedule(event, current_group)
        elif event.text.lower() == "расписание на следующую неделю":
            print_week_schedule(event, current_group, next_week=True)
        elif event.text.lower() == "расписание на завтра":
            # if Sunday, than next week's Monday
            if todays_date.weekday() != 6:
                print_day_schedule(event, current_group, todays_date + datetime.timedelta(days=1))
            else:
                print_day_schedule(event, current_group, todays_date + datetime.timedelta(days=1), next_week=True)
        elif event.text.lower() == "какая группа?":
            print_current_group(event)
        elif event.text.lower() == "какая неделя?":
            print_current_week(event)
        elif len(msg_words) == 1 and is_group(msg_words[0]):
            set_current_group(event, event.text)
        elif msg_words[0] == "бот":
            if len(msg_words) == 1:
                show_functions(event)
            if len(msg_words) == 2:
                if msg_words[1] in weekdays:
                    weekday_schedule(event, msg_words[1], current_group)
                elif is_group(msg_words[1]):
                    change_group(event, msg_words[1])
            elif len(msg_words) == 3:
                if msg_words[1] in weekdays and is_group(msg_words[2]):
                    weekday_schedule(event, msg_words[1], msg_words[2].upper())
        elif event.text.lower() == "погода" or event.text.lower() == "погоду":
            weather_keyboard(event)
        elif event.text.lower() == "сейчас":
            current_weather(event)
        elif event.text.lower() == "сегодня":
            day_weather(event)
        elif event.text.lower() == "завтра":
            day_weather(event, next_day=True)
        elif event.text.lower() == "на 5 дней":
            week_weather(event)
        elif event.text.lower() == "спасибо" or event.text.lower() == "спс" or event.text.lower() == "молодец":
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                attachment=choose_random_kitty()
            )
        else:
            unknown(event)
