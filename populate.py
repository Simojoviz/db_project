from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from model import*
import datetime

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

# Import classes
User          = Base.classes.users
Prenotation   = Base.classes.prenotations
Shift         = Base.classes.shifts
WeekSetting   = Base.classes.week_setting
GlobalSetting = Base.classes.global_setting
Course        = Base.classes.courses
CourseProgram = Base.classes.course_programs
Room          = Base.classes.rooms
CourseSignUp  = Base.classes.course_signs_up


Session = sessionmaker(bind=engine)
session = Session()


# Rooms
add_room(session, name='Main Room', max_capacity=10)



# Users
users = [
    User(fullname = "Stefano Calzavara",      email='stefano@gmail.com',    pwd='stefano1'),
    User(fullname = "Simone Jovon",           email='simone@gmail.com',     pwd='simone1'),
    User(fullname = "Andrea Rosa",            email='andrea@gmail.com',     pwd='andrea1'),
    User(fullname = "Sebastiano Quintavalle", email='sebastiano@gmail.com', pwd='sebastiano1')
]

add_user_from_list(session, users)


# Course
add_course(
    session,
    name = 'OwnTraining',
    starting = datetime.datetime(year=2021, month=5, day=1),
    ending =   datetime.datetime(year=2021, month=7, day=31),
    max_partecipants=10,
    instructor_id=get_user(session, email="stefano@gmail.com").id
)

# WeekSetting
week_settings = [
    WeekSetting(day_name='Monday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), capacity = 10, changed = True),
    WeekSetting(day_name='Tuesday',   starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00), capacity = 12, changed = True),
    WeekSetting(day_name='Wednesday', starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), capacity = 10, changed = True),
    WeekSetting(day_name='Thursday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00), capacity = 12, changed = True),
    WeekSetting(day_name='Friday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), capacity = 10, changed = True),
    WeekSetting(day_name='Saturday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=15, minute=00), length=datetime.time(hour=1, minute=30), capacity =  8, changed = True),
    WeekSetting(day_name='Sunday',    starting=datetime.time(hour=0, minute= 1),  ending=datetime.time(hour=00, minute=0),  length=datetime.time(hour=0, minute=0),  capacity =  0, changed = True),
]

for ws in week_settings:
    add_week_setting(session, week_setting=ws)

# GlobalSettings
global_settings = [
    GlobalSetting(name='MaxWeeklyEntry',       value =   3),   # max-week entry
    GlobalSetting(name='MaxCapacity',          value =  15),   # max-capacity of weight-room
    GlobalSetting(name='CovidCapacity',        value =  10),   # max-capacity of weight-room due to covid-rules
    GlobalSetting(name='MinutesShiftLength',   value =  90),   # stanadard shifts' length in minutes
    GlobalSetting(name='MaximumShiftLength',   value = 180),   # maximum shift's length
    GlobalSetting(name='MinimumShiftLength',   value =  30),   # minimum shift's length
    GlobalSetting(name='HourOpening',          value =   8),   # gym opening hour
    GlobalSetting(name='HourClosing',          value =  22),   # gym closing hour
]


for gs in global_settings:
    add_global_setting(session, global_setting=gs)


# Shifts
plan_shifts(session, starting=datetime.date.today(), n=90)
update_weekend_setting(session, 'Monday', length=datetime.time(hour=1, minute=30))
plan_shifts(session, starting=datetime.date.today(), n=90)

# CourseProgram

# Prenotations

def add_prenotation_aux(session, email, day, month, year, hours, minutes):
    add_prenotation(
        session,
        user = get_user(session, email = email),
        shift = get_shift(
            session,
            date = datetime.date(day = day, month = month, year = year),
            start = datetime.time(hour = hours, minute= minutes)
        )
    )

# Prenotatoin for the first Shift for that day
def add_prenotation_aux_nostart(session, email, day, month, year):
    sh = get_shift(session, date = datetime.date(day = day, month = month, year = year))
    if sh is not None:
        add_prenotation(session, user = get_user(session, email = email), shift= sh[0])

add_prenotation_aux_nostart(session, "andrea@gmail.com",     22, 6, 2021)
add_prenotation_aux_nostart(session, "sebastiano@gmail.com", 23, 6, 2021)
add_prenotation_aux_nostart(session, "simone@gmail.com",     24, 6, 2021)


session.commit()
session.close()