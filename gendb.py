from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, Boolean, String, Date, Time
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base, Session

engine = create_engine('sqlite:///database.db', echo=True)
# engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    pwd = Column(String, nullable=False)

    prenotations = relationship("Prenotation", back_populates="users")
    enrollments = relationship("Enrollment", back_populates="users")

    def __repr__(self):
        return "<User(fullname='%s', email='%s')>" % (self.fullname,
                                                         self.email)


class Prenotation(Base):
    __tablename__ = 'prenotations'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=False)

    users = relationship("User", back_populates="prenotations")


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    h_start = Column(Time, nullable=False)
    h_end = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('date', 'h_start'),)

    prenotations = relationship("Prenotation", back_populates="shifts")


class WeekSetting(Base):
    __tablename__ = 'week_setting'

    day_name = Column(String, primary_key=True)
    starting = Column(Time, nullable=False)
    ending = Column(Time, nullable=False)
    lenght = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)
    changed = Column(Boolean, nullable=False)

class Course(Base):
    __tablename__= 'corsues'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    h_start = Column(Time, nullable=False)
    h_end = Column(Time, nullable=False)
    instructor = Column(Integer, ForeignKey('user.id'), nullable=False)

    user = relationship("Enrollment", back_populates="courses")
    #TO-DO: gestione giorni

class Enrollment(Base):
    __tablename__= 'enrollments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    

Prenotation.shifts = relationship("Shift", back_populates="prenotations", order_by=Shift.date)


Base.metadata.create_all(engine)
