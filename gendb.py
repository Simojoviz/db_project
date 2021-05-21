from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Boolean, String, Date, Time
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base, Session

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    pwd = Column(String, nullable=False)

    prenotations = relationship("Prenotation", back_populates="users")
    course_signs_up = relationship("CourseSignUp", back_populates="users")
    # VA NELLA SOTTOCLASSE ISTRUTTORE
    # courses = relationship("Course", back_popoulates="users")

    def __repr__(self):
        return "<User(fullname='%s', email='%s')>" % (self.fullname,
                                                         self.email)


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    h_start = Column(Time, nullable=False)
    h_end = Column(Time, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    __table_args__ = (UniqueConstraint('date', 'h_start'),)

    prenotations = relationship("Prenotation", back_populates="shifts")
    courses = relationship("Course", back_populates="shifts")
    rooms = relationship("Room", back_populates="shifts")


class Prenotation(Base):
    __tablename__ = 'prenotations'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=False)

    users = relationship("User", back_populates="prenotations")
    shifts = relationship("Shift", back_populates="prenotations")


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
    capacity = Column(Integer, nullable=False)
    changed = Column(Boolean, nullable=False)


class Course(Base):
    __tablename__= 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    starting = Column(Time, nullable=False)
    ending = Column(Time, nullable=False)
    instructor = Column(Integer, ForeignKey('users.id'), nullable=False)

    # VA NELLA SOTTOCLASSE ISTRUTTORE
    # users = relationship("User", back_populates="courses") 
    course_signing_up = relationship("CourseSignUp", back_populates="courses")
    shifts = relationship("Shift", back_populates="courses")
    course_programs = relationship("CourseProgram", back_populates="courses")
    

class CourseProgram(Base):
    __tablename__= 'course_programs'

    id = Column(Integer, primary_key=True)
    week_day = Column(String, nullable=False)
    turn_number = Column(Time, nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    rooms = relationship("Room", back_populates="course_programs")
    courses = relationship("Course", back_populates="course_programs")

  
class Room(Base):
    __tablename__= 'rooms'

    id = Column(Integer, primary_key=True)
    max_capacity = Column(Integer, nullable=False)

    shifts = relationship("Shift", back_populates="rooms")
    course_programs = relationship("CourseProgram", back_populates="rooms")


class CourseSignUp(Base):
    __tablename__= 'course_signs_up'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    

Base.metadata.create_all(engine)
