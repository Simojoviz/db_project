from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from model import*
import datetime

engine = create_engine('sqlite:///database.db', echo=True)
# engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)

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

shifts_1gen = get_daily_shifts(
    date = datetime.date(day = 1, month = 1, year = 2020),
    hour_start = datetime.time(hour = 8, minute= 00),
    hour_end = datetime.time(hour = 20, minute= 00),
    shift_lenght = datetime.time(hour = 1, minute= 30),
    capacity = 10
)

shifts_2gen = get_daily_shifts(
    date = datetime.date(day = 2, month = 1, year = 2020),
    hour_start = datetime.time(hour = 14, minute= 00),
    hour_end = datetime.time(hour = 22, minute= 00),
    shift_lenght = datetime.time(hour = 2, minute= 00),
    capacity = 8
)


add_user_from_list(session, users)
add_shift_from_list(session, shifts_1gen)
add_shift_from_list(session, shifts_2gen)

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

add_prenotation_aux(session, "andrea@gmail.com", 1, 1, 2020, 9, 30)
add_prenotation_aux(session, "sebastiano@gmail.com", 1, 1, 2020, 11, 00)
add_prenotation_aux(session, "simone@gmail.com", 2, 1, 2020, 20, 00)

session.commit()
session.close()