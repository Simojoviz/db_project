from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime

from sqlalchemy.sql.expression import update

from model import*
from automap import*

engine = create_engine('postgresql://utente:password@localhost:5432/Gym', echo=False)

Session = sessionmaker(bind=engine, autoflush=True)
session = Session()

# Rooms
rooms = [
    Room(name = "Main Room",     max_capacity =  5),
    Room(name = "Weight Room",   max_capacity = 30),
    Room(name = "Fitness Room",  max_capacity = 25),
    Room(name = "Swimming Pool", max_capacity = 40),
    Room(name = "Boxing Room",   max_capacity = 25)
]
add_room_from_list(session, rooms)

# Roles
roles = [
    Role(name = 'Client'),
    Role(name = 'Trainer'),
    Role(name = 'Admin')
]
add_role_from_list(session, roles)

# Users
users = [
    User(fullname = "Admin",                  email='admin@gmail.com',        pwd='admin1',        telephone='1234567890', address='Via Ciao 2',      covid_state=0, subscription=datetime.date.today() + timedelta(days=3000)),
    User(fullname = "Stefano Calzavara",      email='stefano@gmail.com',      pwd='stefano1',      telephone='0123456789', address='Via Falsa 23',    covid_state=0, subscription=datetime.date.today() + timedelta(days=365)),
    User(fullname = "Alessandra Raffaetà",    email='alessandra@gmail.com',   pwd='alessandra1',   telephone='2873018453', address='Via Vai 7',       covid_state=0, subscription=datetime.date.today() + timedelta(days=365)),
    User(fullname = "Simone Jovon",           email='simone@gmail.com',       pwd='simone1',       telephone='3019837283', address='Via Cesare 12',   covid_state=0, subscription=datetime.date.today() + timedelta(days=90)),
    User(fullname = "Andrea Rosa",            email='andrea@gmail.com',       pwd='andrea1',       telephone='3254173433', address='Castello 2534/A', covid_state=0, subscription=datetime.date.today() + timedelta(days=90)),
    User(fullname = "Sebastiano Quintavalle", email='sebastiano@gmail.com',   pwd='sebastiano1',   telephone='5272735383', address='Castello 13',     covid_state=0, subscription=datetime.date.today() + timedelta(days=90)),
    User(fullname = "Mario Rossi",            email='mario@gmail.com',        pwd='mario1',        telephone='5674567438', address='Via Falsa 13',    covid_state=2, subscription=datetime.date.today() + timedelta(days=90)),
]
add_user_from_list(session, users)

# User-Roles
add_user_role(
    session,
    user = get_user(session, email='admin@gmail.com'),
    role = get_role(session, name="Admin")
)

# Trainers
trainers = [
    get_user(session, email='stefano@gmail.com'),
    get_user(session, email='alessandra@gmail.com')
]
add_trainer_from_list(session, trainers)

# GlobalSettings
global_settings = [
    GlobalSetting(name='MaxWeeklyEntry',       value =   3),   # max-week entry
    GlobalSetting(name='MaximumShiftLength',   value = 180),   # maximum shift's length
    GlobalSetting(name='MinimumShiftLength',   value =  30),   # minimum shift's length
    GlobalSetting(name='HourOpening',          value =   8),   # gym opening hour
    GlobalSetting(name='HourClosing',          value =  22)    # gym closing hour
]

add_global_setting_from_list(session, global_setting_list=global_settings)

# WeekSetting
week_settings = [
    WeekSetting(day_name='Monday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30)), # 9
    WeekSetting(day_name='Tuesday',   starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00)), # 6
    WeekSetting(day_name='Wednesday', starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30)), # 9
    WeekSetting(day_name='Thursday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00)), # 6
    WeekSetting(day_name='Friday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30)), # 9
    WeekSetting(day_name='Saturday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=15, minute=00), length=datetime.time(hour=1, minute=30)) # 4
]
add_week_setting_from_list(session, week_setting_list=week_settings)

# Courses
courses = [
    Course(name = 'Boxe',
        starting=datetime.datetime(year=2021, month=8, day=30), ending = datetime.datetime(year=2021, month=9, day=30), max_partecipants = 7, 
        instructor_id = get_trainer(session, email='stefano@gmail.com').id
    ),
    Course(name = 'Zumba',
        starting=datetime.datetime(year=2021, month=9, day=21), ending = datetime.datetime(year=2021, month=10, day=21), max_partecipants = 12, 
        instructor_id = get_trainer(session, email='alessandra@gmail.com').id
    ),
    Course(name = 'Judo',
        starting=datetime.datetime(year=2021, month=10, day=1), ending = datetime.datetime(year=2021, month=10, day=30), max_partecipants = 20, 
        instructor_id = get_trainer(session, email='stefano@gmail.com').id
    )
]
add_course_from_list(session, courses)

# CourseProgram
courses_program = [
    CourseProgram(
        week_day = 'Monday', turn_number = 3,
        room_id = get_room(session, name='Boxing Room').id,
        course_id = get_course(session, name='Boxe').id
    ),
    CourseProgram(
        week_day = 'Tuesday', turn_number = 4,
        room_id = get_room(session, name='Fitness Room').id,
        course_id = get_course(session, name='Zumba').id
    ),
    CourseProgram(
        week_day = 'Friday', turn_number = 5,
        room_id = get_room(session, name='Fitness Room').id,
        course_id = get_course(session, name='Zumba').id
    ),
    CourseProgram(
        week_day = 'Tuesday', turn_number = 5,
        room_id = get_room(session, name='Main Room').id,
        course_id = get_course(session, name='Judo').id
    ),
    CourseProgram(
        week_day = 'Thursday', turn_number = 5,
        room_id = get_room(session, name='Fitness Room').id,
        course_id = get_course(session, name='Judo').id
    )
]

add_course_program_from_list(session, courses_program)

plan_course(session, "Boxe")
plan_course(session, "Zumba")
plan_course(session, "Judo")


# Prenotations

# Prenotatoin for the first Shift on that day

def add_populate_prenotation(session, email, day, month, year, room_name, turn_number):
    user = get_user(session, email = email)
    date = datetime.date(day = day, month = month, year = year)
    room = get_room(session, name=room_name)
    ws = get_week_setting(session, day_name=calendar.day_name[date.weekday()])
    starting = time_to_timedelta(ws.starting) + time_to_timedelta(ws.length) * (turn_number-1)
    ending = starting + time_to_timedelta(ws.length)
    add_shift(session, date=date, start=starting, end=ending, room_id=room.id)
    sh = get_shift(session, date=date, start=starting, room_id=room.id)
    add_prenotation(session, user = user, shift= sh)


add_populate_prenotation(session, "andrea@gmail.com",     13,  9, 2021, 'Fitness Room',  2)
add_populate_prenotation(session, "sebastiano@gmail.com", 20,  8, 2021, 'Main Room',     5)
add_populate_prenotation(session, "sebastiano@gmail.com", 23,  9, 2021, 'Weight Room',   5)
add_populate_prenotation(session, "sebastiano@gmail.com", 12, 10, 2021, 'Swimming Pool', 2)
add_populate_prenotation(session, "simone@gmail.com",      8,  9, 2021, 'Fitness Room',  3)
add_populate_prenotation(session, "simone@gmail.com",      9,  9, 2021, 'Fitness Room',  3)
add_populate_prenotation(session, "simone@gmail.com",      10,  9, 2021, 'Fitness Room',  3)


add_course_sign_up(
    session,
    user=get_user(session, email='sebastiano@gmail.com'),
    course=get_course(session, name='Boxe')
)

add_course_sign_up(
    session,
    user=get_user(session, email='andrea@gmail.com'),
    course=get_course(session, name='Zumba')
)

add_course_sign_up(
    session,
    user=get_user(session, email='simone@gmail.com'),
    course=get_course(session, name='Zumba')
)

add_course_sign_up(
    session,
    user=get_user(session, email='simone@gmail.com'),
    course=get_course(session, name='Judo')
)


session.commit()