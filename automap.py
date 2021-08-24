from flask.app import Flask
from sqlalchemy import Column, Integer, Boolean, String, Date, Time, DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.expression import false, null


Base = declarative_base()


# ______________________________________ USER, TRAINER ______________________________________


class User(Base):

    __tablename__ = 'users'

    id           = Column(Integer, primary_key=True)
    email        = Column(String,  nullable=False, unique=True)
    telephone    = Column(String,  nullable=False, unique=True)
    fullname     = Column(String,  nullable=False)
    pwd          = Column(String,  nullable=False)
    address      = Column(String,  nullable=False)
    subscription = Column(Date,    nullable=False)
    covid_state  = Column(Integer, nullable=False)

    shifts          = relationship("Shift",  secondary="prenotations",    back_populates="users_prenoted")
    courses         = relationship("Course", secondary="course_signs_up", back_populates="users")
    roles           = relationship("Role",   secondary="user_roles",      back_populates="users")
    trainer         = relationship("Trainer", back_populates="user", uselist=False, cascade="all,delete")
    prenotations    = relationship("Prenotation",  viewonly=True)
    course_signs_up = relationship("CourseSignUp", viewonly=True)

    def __repr__(self):
        return "<User(fullname='%s', email='%s')>" % (self.fullname, self.email)


class Trainer(Base):
    
    __tablename__ = 'trainers'

    id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

    user = relationship("User", back_populates="trainer")
    courses = relationship("Course", back_populates="trainer", cascade="all,delete")

    def __repr__(self):
        return "<Trainer(fullname='%s', email='%s')>" % (self.user.fullname,
                                                         self.user.email)


# ______________________________________ ROLE, USER-ROLES ______________________________________        


class Role(Base):

    __tablename__ = 'roles'

    id   = Column(Integer, primary_key=True)
    name = Column(String,  unique=True)
    
    users = relationship("User", secondary="user_roles", back_populates="roles")


class UserRole(Base):

    __tablename__ = 'user_roles'

    user_id = Column(Integer(), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(Integer(), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)


# ______________________________________ SHIFT, PRENOTATION ______________________________________


class Shift(Base):

    __tablename__ = 'shifts'

    id        = Column(Integer, primary_key=True)
    date      = Column(Date, nullable=False)
    starting  = Column(Time, nullable=False)
    ending    = Column(Time, nullable=False)
    room_id   = Column(Integer, ForeignKey('rooms.id',   ondelete='CASCADE'))
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='SET NULL'))

    __table_args__ = (UniqueConstraint('date', 'starting', 'room_id'),)

    users_prenoted = relationship("User",   back_populates="shifts", secondary="prenotations",)
    course         = relationship("Course", back_populates="shifts")
    room           = relationship("Room",   back_populates="shifts")
    prenotations   = relationship("Prenotation", viewonly=True)

    def __repr__(self):
        if self.course is not None:
            return "<Shift(date='%d/%d/%d', start='%d:%d', end='%d:%d', room:'%s', course:'%s')>" % (
                self.date.day, self.date.month, self.date.year,
                self.starting.hour, self.starting.minute,
                self.ending.hour,   self.ending.minute,
                self.room.name,
                self.course.name
            )
        else:
            return "<Shift(date='%d/%d/%d', start='%d:%d', end='%d:%d', room:'%s', course:'OwnTraining')>" % (
                self.date.day, self.date.month, self.date.year,
                self.starting.hour, self.starting.minute,
                self.ending.hour,   self.ending.minute,
                self.room.name
            )
        

class Prenotation(Base):

    __tablename__ = 'prenotations'

    user_id  = Column(Integer, ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True)
    shift_id = Column(Integer, ForeignKey('shifts.id', ondelete='CASCADE'), primary_key=True)

    user  = relationship("User", viewonly=True)
    shift = relationship("Shift", viewonly=True)


# ______________________________________ ROOM ______________________________________


class Room(Base):
    
    __tablename__ = 'rooms'

    id           = Column(Integer, primary_key=True)
    name         = Column(String,  nullable=False, unique=True)
    max_capacity = Column(Integer, nullable=False)
    new          = Column(Boolean, nullable=False)

    shifts          = relationship("Shift",         back_populates="room", cascade="all,delete")
    course_programs = relationship("CourseProgram", back_populates="room", cascade="all,delete")

    def __repr__(self):
        return "<Room(name='%s', capacity='%d')>" % (
            self.name,
            self.max_capacity,
        )


# ______________________________________ GLOBAL-SETTING, WEEK-SETTING ______________________________________


class GlobalSetting(Base):

    __tablename__ = 'global_settings'

    name  = Column(String, primary_key=True)
    value = Column(Integer, nullable=False)

    def __repr__(self):
        return "<GlobalSetting(name='%s', value='%d')>" % (
            self.name,
            self.value
        )


class WeekSetting(Base):

    __tablename__ = 'week_settings'

    day_name = Column(String, primary_key=True)
    starting = Column(Time, nullable=False)
    ending   = Column(Time, nullable=False)
    length   = Column(Time, nullable=False)
    changed  = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<WeekSetting(day='%s', starting='%d:%d', ending='%d:%d', length='%d:%d', capacity='%d')>" % (
            self.day_name,
            self.starting.hour, self.starting.minute,
            self.ending.hour,   self.ending.minute,
            self.length.hour,   self.length.minute,
            self.capacity
        )


# ______________________________________ COURSE, COURSE-PROGRAM, COURSE-SIGN-UP ______________________________________


class Course(Base):

    __tablename__ = 'courses'

    id               = Column(Integer, primary_key=True)
    name             = Column(String,  nullable=False, unique=True)
    starting         = Column(Date,    nullable=False)
    ending           = Column(Date,    nullable=False)
    max_partecipants = Column(Integer, nullable=False)
    instructor_id    = Column(Integer, ForeignKey('trainers.id', ondelete='CASCADE'))

    trainer         = relationship("Trainer",       back_populates="courses")
    shifts          = relationship("Shift",         back_populates="course")
    users           = relationship("User",          back_populates="courses", secondary="course_signs_up", cascade="all,delete")
    course_programs = relationship("CourseProgram", back_populates="course")
    course_signs_up = relationship("CourseSignUp", viewonly=True)

    def __repr__(self):
        return "<Course(name='%s', starting='%d/%d/%d', ending='%d/%d/%d', max_partecipants='%d', trainer='%s')>" % (
            self.name,
            self.starting.day, self.starting.month, self.starting.year,
            self.ending.day, self.ending.month, self.ending.year,
            self.max_partecipants,
            self.trainer.user.fullname
        )


class CourseProgram(Base):

    __tablename__ = 'course_programs'

    id          = Column(Integer, primary_key=True)
    week_day    = Column(String,  nullable=False)
    turn_number = Column(Integer, nullable=False)
    room_id     = Column(Integer, ForeignKey('rooms.id',   ondelete='CASCADE'))
    course_id   = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'))

    __table_args__ = (UniqueConstraint('course_id', 'week_day', 'turn_number', ),)
    
    room   = relationship("Room", back_populates="course_programs") #cascade="all,delete"
    course = relationship("Course", back_populates="course_programs")

    def __repr__(self):
        return "<CourseProgram(weekday='%s', turn number='%d', room='%s', course='%s')>" % (
            self.week_day,
            self.turn_number,
            self.room.name,
            self.course.name,
        )


class CourseSignUp(Base):
    
    __tablename__ = 'course_signs_up'

    user_id   = Column(Integer, ForeignKey('users.id',   ondelete='CASCADE'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True)

    course = relationship("Course", viewonly=True)
    user   = relationship("User", viewonly=True)


# ______________________________________ MESSAGE ______________________________________


class Message(Base):

    __tablename__ = 'messages'

    id        = Column(Integer, primary_key=True)
    date      = Column(DateTime, nullable=False)
    text      = Column(String,   nullable=False)
    read      = Column(Boolean,  nullable=False)
    sender    = Column(Integer, ForeignKey('users.id'), nullable=False)
    addressee = Column(Integer, ForeignKey('users.id'), nullable=False)

    addresser = relationship("User", foreign_keys=[addressee])
    sender_   = relationship("User", foreign_keys=[sender])