import json
import re
import requests
from copy import deepcopy as copy
from bs4 import BeautifulSoup
import xlrd
from pprint import pprint

mirea_schedule_site = " https://www.mirea.ru/schedule/"
weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
group_regex = r"И[АВКНМ]{1}БО-[0-9]{2}-1[7-9]{1}"
schedule_page = requests.get(mirea_schedule_site)
soup2 = BeautifulSoup(schedule_page.text, "html.parser")
results = soup2.find("div", {"class": "rasspisanie"}).find(string="Институт информационных технологий"). \
    find_parent("div").find_parent("div").findAll("a", {"class": "uk-link-toggle"})
# professors = {}
#
#
# def set_professor(name, lesson, week_day, para_num, week_oddity):
#     if name not in professors:
#         day = [[None] * 2, [None] * 2, [None] * 2, [None] * 2, [None] * 2, [None] * 2]
#         week = {'понедельник': copy(day), 'вторник': copy(day), 'среда': copy(day), 'четверг': copy(day),
#                 'пятница': copy(day),
#                 'суббота': copy(day)}
#         professors.update({name: week})
#
#     professors[name][week_day][para_num][week_oddity] = lesson
#
#
# def find_professors_by_last_name(last_name):
#     return [key for key, value in professors.items() if key.startswith(last_name)]


def get_course_schedule(course=1, request_res=results):
    course_s = str(course) + "к"
    filename = "schedule_" + course_s + ".xlsx"
    file_regex = r"ИИТ_" + course_s + r".+\.xlsx"

    # downloading excel file(-s)
    for result in request_res:
        # if "ИИТ" in str(result) and ".xlsx" in str(result) and course_s in str(result):
        if re.search(file_regex, str(result), re.IGNORECASE) is not None:
            f = open(filename, "wb")
            downloaded_file = requests.get(result["href"])
            f.write(downloaded_file.content)
            f.close()

    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0)

    num_cols = sheet.ncols
    num_rows = sheet.nrows

    groups = []
    schedule = {}

    for col_index in range(num_cols):
        group_name = str(sheet.cell(1, col_index).value)
        if re.search(group_regex, group_name, re.IGNORECASE) is not None:
            groups.append(group_name)
            week = {"понедельник": None, "вторник": None, "среда": None, "четверг": None, "пятница": None,
                    "суббота": None, "воскресенье": "Выходной! Пар нет"}
            for day in range(6):
                lessons = [[], [], [], [], [], []]
                for para in range(6):
                    for week_oddity in range(2):
                        row_index = 3 + week_oddity + para * 2 + day * 12
                        subject = sheet.cell(row_index, col_index).value.replace("\n", "; ") if sheet.cell(row_index,
                                                                                                           col_index).value != '' else "--"
                        lesson_type = sheet.cell(row_index, col_index + 1).value.replace("\n", "; ") if sheet.cell(
                            row_index,
                            col_index + 1).value != '' else "--"
                        lecturer = sheet.cell(row_index, col_index + 2).value.replace("\n", "; ") if sheet.cell(
                            row_index,
                            col_index + 2).value != '' else "--"
                        classroom = sheet.cell(row_index, col_index + 3).value.replace("\n", "; ") if sheet.cell(
                            row_index,
                            col_index + 3).value != '' else "--"
                        url = sheet.cell(row_index, col_index + 4).value.replace("\n", "; ") if sheet.cell(row_index,
                                                                                                           col_index + 4).value != '' else "--"
                        lesson = {"Предмет": subject, "Вид занятий": lesson_type, "Преподаватель": lecturer,
                                  "Аудитория": classroom, "Ссылка": url}
                        lessons[para].append(lesson)

                        # professors_list = lecturer.split('; ')
                        # subject_list = subject.split('; ')
                        # pr_lesson = copy(lesson)
                        # pr_lesson.pop('Преподаватель')
                        # pr_lesson['Группа'] = group_name
                        #
                        # for h in range(len(professors_list)):
                        #     if len(subject_list) > h:
                        #         pr_lesson['Предмет'] = subject_list[h]
                        #     set_professor(professors_list[h], pr_lesson, weekdays[day], day, week_oddity)

                week[weekdays[day]] = lessons
            schedule.update({group_name: week})

    return schedule


schedule_first = get_course_schedule()
schedule_second = get_course_schedule(2)
schedule_third = get_course_schedule(3)

# pprint(schedule_first)
# pprint(professors)

with open("course1_sch.json", "w") as write_file:
    json.dump(schedule_first, write_file)
with open("course2_sch.json", "w") as write_file:
    json.dump(schedule_second, write_file)
with open("course3_sch.json", "w") as write_file:
    json.dump(schedule_third, write_file)

# with open("professors.json", 'w') as write_file:
#     write_file.write(json.dumps(professors, ensure_ascii=False, indent=4))
