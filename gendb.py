from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Boolean, String, Date, Time
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
#engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    pwd = Column(String, nullable=False)

    prenotations = relationship("Prenotation", viewonly=True)
    prenotations_shifts = relationship("Shift", secondary="prenotations", back_populates="users_prenotated")
    courses = relationship("Course", secondary="course_signs_up", back_populates="users")


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

    def _repr_(self):
        return "<Shift(date='%d/%d/%d', start='%d:%d', end='%d:%d', room:'%s', course:'%s')>" % (
            self.date.day, self.date.month, self.date.year,
            self.h_start.hour, self.h_start.minute,
            self.h_end.hour,   self.h_end.minute,
            self.room.name,
            self.course.name
        )


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

    def _repr_(self):
        return "<GlobalSetting(name='%s', value='%d')>" % (
            self.name,
            self.value
        )


class WeekSetting(Base):
    __tablename__ = 'week_setting'

    day_name = Column(String, primary_key=True)
    starting = Column(Time, nullable=False)
    ending = Column(Time, nullable=False)
    length = Column(Time, nullable=False)
    changed = Column(Boolean, nullable=False)

    def _repr_(self):
        return "<WeekSetting(day='%s', starting='%d:%d', ending='%d:%d', length='%d:%d', capacity='%d')>" % (
            self.day_name,
            self.starting.hour, self.starting.minute,
            self.ending.hour,   self.ending.minute,
            self.length.hour,   self.length.minute,
            self.capacity
        )

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

    def _repr_(self):
        return "<Course(name='%s', starting='%d/%d/%d', ending='%d/%d/%d', max_partecipants='%d', trainer='%s')>" % (
            self.name,
            self.starting.day, self.starting.month, self.starting.year,
            self.ending.day, self.ending.month, self.ending.year,
            self.max_partecipants,
            self.trainer.user.fullname
        )


class CourseProgram(Base):
    __tablename__ = 'course_programs'

    id = Column(Integer, primary_key=True)
    week_day = Column(String, nullable=False)
    turn_number = Column(Integer, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    __table_args__ = (UniqueConstraint('course_id', 'week_day', 'turn_number'),)

    room = relationship("Room", back_populates="course_programs")
    course = relationship("Course", back_populates="course_programs")

    def _repr_(self):
        return "<CourseProgram(weekday='%s', turn number='%d', room='%s', course='%s')>" % (
            self.week_day,
            self.turn_number,
            self.room.name,
            self.course.name,
        )

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    max_capacity = Column(Integer, nullable=False)

    shifts = relationship("Shift", back_populates="room")
    course_programs = relationship("CourseProgram", back_populates="room")

    def _repr_(self):
        return "<Room(name='%s', capacity='%d')>" % (
            self.name,
            self.max_capacity,
        )

class CourseSignUp(Base):
    __tablename__ = 'course_signs_up'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)


Base.metadata.create_all(engine)
