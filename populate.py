from typing import Tuple
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

from model import*
import datetime

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
#engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)

Base = declarative_base()

#_________________________________________________TABLES_________________________________________________

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    pwd = Column(String, nullable=False)

    prenotations = relationship("Prenotation", viewonly=True)
    prenotations_shifts = relationship("Shift", secondary="prenotations", back_populates="users_prenotated")
    courses = relationship("Course", secondary="course_signs_up", back_populates="users")

    def __repr__(self):
        return "<User(fullname='%s', email='%s')>" % (self.fullname,
                                                         self.email)


class Trainer(Base):
    __tablename__ = 'trainers'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)

    courses = relationship("Course", back_populates="trainer")


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    h_start = Column(Time, nullable=False)
    h_end = Column(Time, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'))

    __table_args__ = (UniqueConstraint('date', 'h_start', 'room_id'),)

    prenotations = relationship("Prenotation", viewonly=True)
    users_prenotated = relationship("User", secondary="prenotations", back_populates="prenotations_shifts")
    course = relationship("Course", back_populates="shifts")
    room = relationship("Room", back_populates="shifts")


class Prenotation(Base):
    __tablename__ = 'prenotations'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=False)

    user = relationship("User", viewonly=True)
    shift = relationship("Shift", viewonly=True)


class GlobalSetting(Base):
    __tablename__ = 'global_setting'

    name = Column(String, primary_key=True)
    value = Column(Integer, nullable=False)


class WeekSetting(Base):
    __tablename__ = 'week_setting'

    day_name = Column(String, primary_key=True)
    starting = Column(Time, nullable=False)
    ending = Column(Time, nullable=False)
    length = Column(Time, nullable=False)
    changed = Column(Boolean, nullable=False)


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    starting = Column(Date, nullable=False)
    ending = Column(Date, nullable=False)
    max_partecipants = Column(Integer, nullable=False)
    instructor_id = Column(Integer, ForeignKey('trainers.id'), nullable=False)

    trainer = relationship("Trainer", back_populates="courses")
    shifts = relationship("Shift", back_populates="course")
    users = relationship("User", secondary="course_signs_up", back_populates="courses")
    course_programs = relationship("CourseProgram", back_populates="course")


class CourseProgram(Base):
    __tablename__ = 'course_programs'

    id = Column(Integer, primary_key=True)
    week_day = Column(String, nullable=False)
    turn_number = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    room = relationship("Room", back_populates="course_programs")
    course = relationship("Course", back_populates="course_programs")


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    max_capacity = Column(Integer, nullable=False)

    shifts = relationship("Shift", back_populates="room")
    course_programs = relationship("CourseProgram", back_populates="room")


class CourseSignUp(Base):
    __tablename__ = 'course_signs_up'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

#________________________________________________________________________________________________________

Session = sessionmaker(bind=engine)
session = Session()


# Rooms
rooms = [
    Room(name = "Main Room", max_capacity = 25),
    Room(name = "Weight Room", max_capacity = 30),
    Room(name = "Fitness Room", max_capacity = 25),
    Room(name = "Swimming Pool", max_capacity = 40),
    Room(name = "Boxing Room", max_capacity = 25)
]

add_room_from_list(session, rooms)


# Users
users = [
    User(fullname = "Stefano Calzavara",      email='stefano@gmail.com',    pwd='stefano1'),
    User(fullname = "Alessandra Raffaetà",    email='alessandra@gmail.com', pwd='alessandra1'),
    User(fullname = "Simone Jovon",           email='simone@gmail.com',     pwd='simone1'),
    User(fullname = "Andrea Rosa",            email='andrea@gmail.com',     pwd='andrea1'),
    User(fullname = "Sebastiano Quintavalle", email='sebastiano@gmail.com', pwd='sebastiano1')
]

add_user_from_list(session, users)

trainers = [
    get_user(session, email='stefano@gmail.com'),
    get_user(session, email='alessandra@gmail.com')
]

add_trainer_from_list(session, trainers)
add_trainer(session, fullname='Riccardo Focardi', email='riccardo@gmail.com', pwd='riccardo1')



courses = [
    Course(name = 'Boxe',
        starting=datetime.datetime(year=2021, month=6, day=1), ending = datetime.datetime(year=2021, month=6, day=30), max_partecipants = 7, 
        instructor_id = get_trainer(session, email='stefano@gmail.com').id
    ),
    Course(name = 'Zumba',
        starting=datetime.datetime(year=2021, month=7, day=1), ending = datetime.datetime(year=2021, month=7, day=30), max_partecipants = 12, 
        instructor_id = get_trainer(session, email='alessandra@gmail.com').id
    )
]

add_course_from_list(session, courses)


# WeekSetting
week_settings = [
    WeekSetting(day_name='Monday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), changed = True),
    WeekSetting(day_name='Tuesday',   starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00), changed = True),
    WeekSetting(day_name='Wednesday', starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), changed = True),
    WeekSetting(day_name='Thursday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=21, minute=00), length=datetime.time(hour=2, minute=00), changed = True),
    WeekSetting(day_name='Friday',    starting=datetime.time(hour=8, minute=00), ending=datetime.time(hour=21, minute=30), length=datetime.time(hour=1, minute=30), changed = True),
    WeekSetting(day_name='Saturday',  starting=datetime.time(hour=9, minute=00), ending=datetime.time(hour=15, minute=00), length=datetime.time(hour=1, minute=30), changed = True),
    WeekSetting(day_name='Sunday',    starting=datetime.time(hour=0, minute= 1),  ending=datetime.time(hour=00, minute=0), length=datetime.time(hour=0, minute=0), changed = True),
]

for ws in week_settings:
    add_week_setting(session, week_setting=ws)

# GlobalSettings
global_settings = [
    GlobalSetting(name='MaxWeeklyEntry',       value =   3),   # max-week entry
    GlobalSetting(name='MaxCapacity',          value =  15),   # max-capacity of room
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


# CourseProgram
courses_program = [
    CourseProgram(
        week_day = 'Monday', turn_number = 3,
        room_id = get_room(session, name='Boxing Room').id,
        course_id =get_course(session, name='Boxe').id
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
    )
]

add_course_program_from_list(session, courses_program)

plan_course(session, "Boxe")
plan_course(session, "Zumba")



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
def add_prenotation_aux_nostart(session, email, day, month, year, room):
    sh = get_shift(session, date = datetime.date(day = day, month = month, year = year), room_id=get_room(session, name=room).id)
    if sh is not None:
        add_prenotation(session, user = get_user(session, email = email), shift= sh[0])

add_prenotation_aux_nostart(session, "andrea@gmail.com",     22, 6, 2021, 'Main Room')
add_prenotation_aux_nostart(session, "sebastiano@gmail.com", 23, 6, 2021, 'Weight Room')
add_prenotation_aux_nostart(session, "simone@gmail.com",     24, 6, 2021, 'Fitness Room')


add_course_sign_up(
    session,
    user=get_user(session, email='sebastiano@gmail.com'),
    course=get_course(session, name='Boxe'),
)

add_course_sign_up(
    session,
    user=get_user(session, email='andrea@gmail.com'),
    course=get_course(session, name='Zumba'),
)

add_course_sign_up(
    session,
    user=get_user(session, email='simone@gmail.com'),
    course=get_course(session, name='Zumba'),
)

session.commit()
session.close()