from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from model import*
import datetime
from datetime import timedelta

x = datetime.datetime(2020, 5, 17)

engine = create_engine('sqlite:///database.db', echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users
Prenotation = Base.classes.prenotations
Shift = Base.classes.shifts

Session = sessionmaker(bind=engine)
session = Session()

users = [
    User(fullname = "Stefano Calzavara",      email='stefano@gmail.com',    pwd='stefano1'),
    User(fullname = "Simone Jovon",           email='simone@gmail.com',     pwd='simone1'),
    User(fullname = "Andrea Rosa",            email='andrea@gmail.com',     pwd='andrea1'),
    User(fullname = "Sebastiano Quintavalle", email='sebastiano@gmail.com', pwd='sebastiano1')
]

shifts_1gen = get_daily_shifts_list(
    date = datetime.datetime(day = 1, month = 1, year = 2020),
    hour_start = timedelta(hours = 8, minutes = 00),
    hour_end = timedelta(hours = 20, minutes = 00),
    shift_lenght = timedelta(hours = 1, minutes = 30),
    capacity = 10
)

shifts_2gen = get_daily_shifts_list(
    date = datetime.datetime(day = 2, month = 1, year = 2020),
    hour_start = timedelta(hours = 14, minutes = 00),
    hour_end = timedelta(hours = 22, minutes = 00),
    shift_lenght = timedelta(hours = 2, minutes = 00),
    capacity = 8
)


add_user_from_list(session, users)
add_shift_from_list(session, shifts_1gen)
add_shift_from_list(session, shifts_2gen)

def add_prenotation_aux(session, email, day, month, year, hours, minutes):
    add_prenotation(
        session,
        get_user(session, email),
        get_shifts(session, datetime.datetime(day = day, month = month, year = year), timedelta(hours = hours, minutes = minutes))
    )

add_prenotation_aux(session, "andrea@gmail.com", 1, 1, 2020, 9, 30)
add_prenotation_aux(session, "sebastiano@gmail.com", 1, 1, 2020, 11, 00)
add_prenotation_aux(session, "simone@gmail.com", 2, 1, 2020, 20, 00)

session.commit()