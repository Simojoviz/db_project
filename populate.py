from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime

from sqlalchemy.sql.expression import update

from model import*
from automap import*

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
#engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)
#engine = create_engine('postgresql://postgres:gemellirosa@localhost:5432/Gym', echo=True)

Session = sessionmaker(bind=engine, autoflush=True)
session = Session()

# Rooms
rooms = [
    Room(name = "Main Room",     max_capacity =  5, new=True),
    Room(name = "Weight Room",   max_capacity = 30, new=True),
    Room(name = "Fitness Room",  max_capacity = 25, new=True),
    Room(name = "Swimming Pool", max_capacity = 40, new=True),
    Room(name = "Boxing Room",   max_capacity = 25, new=True)
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
    User(fullname = "Massimiliano Fardo",     email='massimiliano@gmail.com', pwd='massimiliano1', telephone='5272735382', address='A Zattere',       covid_state=2, subscription=datetime.date.today())
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
add_trainer(session, fullname='Riccardo Focardi', email='riccardo@gmail.com', pwd='riccardo1',  telephone='8302837481', address='Via Ciao 2')

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
    WeekSetting(day_name='Monday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), changed = True), # 9
    WeekSetting(day_name='Tuesday',   starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00), changed = True), # 6
    WeekSetting(day_name='Wednesday', starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), changed = True), # 9
    WeekSetting(day_name='Thursday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00), changed = True), # 6
    WeekSetting(day_name='Friday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), changed = True), # 9
    WeekSetting(day_name='Saturday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=15, minute=00), length=datetime.time(hour=1, minute=30), changed = True) # 4
]
add_week_setting_from_list(session, week_setting_list=week_settings)

# Shifts
plan_shifts(session, starting=datetime.date(day=1, month=8, year=2021), n=90, all_room=True)
""" Da correggere
update_weekend_setting(
    session, day_name='Saturday',
    starting = datetime.time(hour=10, minute=00),
    ending   = datetime.time(hour=15, minute=00),
    length   = datetime.time(hour=1,  minute=00)
)
plan_shifts(session, starting=datetime.date(day=1, month=8, year=2021), n=365, all_room=True)
"""


# Courses
courses = [
    Course(name = 'Boxe',
        starting=datetime.datetime(year=2021, month=8, day=1), ending = datetime.datetime(year=2021, month=8, day=30), max_partecipants = 7, 
        instructor_id = get_trainer(session, email='stefano@gmail.com').id
    ),
    Course(name = 'Zumba',
        starting=datetime.datetime(year=2021, month=8, day=1), ending = datetime.datetime(year=2021, month=8, day=30), max_partecipants = 12, 
        instructor_id = get_trainer(session, email='alessandra@gmail.com').id
    ),
    Course(name = 'Judo',
        starting=datetime.datetime(year=2021, month=9, day=1), ending = datetime.datetime(year=2021, month=9, day=30), max_partecipants = 20, 
        instructor_id = get_trainer(session, email='riccardo@gmail.com').id
    ),
    Course(name = 'Test',
        starting=datetime.datetime(year=2021, month=8, day=1), ending = datetime.datetime(year=2021, month=8, day=15), max_partecipants = 20, 
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
def add_prenotation_aux_nostart(session, email, day, month, year, room):
    sh = get_shift(session, date = datetime.date(day = day, month = month, year = year), room_id=get_room(session, name=room).id)
    if sh is not None:
        add_prenotation(session, user = get_user(session, email = email), shift= sh[0])

add_prenotation_aux_nostart(session, "andrea@gmail.com",     20,  8, 2021, 'Main Room')
add_prenotation_aux_nostart(session, "andrea@gmail.com",     21,  8, 2021, 'Swimming Pool')
add_prenotation_aux_nostart(session, "andrea@gmail.com",     2,   9, 2021, 'Main Room')
add_prenotation_aux_nostart(session, "andrea@gmail.com",     13,  9, 2021, 'Fitness Room')
add_prenotation_aux_nostart(session, "sebastiano@gmail.com", 20,  8, 2021, 'Main Room')
add_prenotation_aux_nostart(session, "sebastiano@gmail.com", 23,  9, 2021, 'Weight Room')
add_prenotation_aux_nostart(session, "sebastiano@gmail.com",  2,  9, 2021, 'Main Room')
add_prenotation_aux_nostart(session, "sebastiano@gmail.com", 12, 10, 2021, 'Swimming Pool')
add_prenotation_aux_nostart(session, "simone@gmail.com",      3,  9, 2021, 'Fitness Room')
add_prenotation_aux_nostart(session, "simone@gmail.com",      4,  9, 2021, 'Fitness Room')
add_prenotation_aux_nostart(session, "simone@gmail.com",      6,  9, 2021, 'Fitness Room')

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

add_course_sign_up(
    session,
    user=get_user(session, email='andrea@gmail.com'),
    course=get_course(session, name='Test'),
)

#covid_report_messages(session, get_user(session, email='andrea@gmail.com').id)

session.commit()