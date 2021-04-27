from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base, Session


engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    pwd = Column(String, nullable=False)

    prenotations = relationship("Prenotation", back_populates="users")

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
    capacity = Column(Time, nullable=False)

    __table_args__ = (UniqueConstraint('date', 'h_start'),)

    prenotations = relationship("Prenotation", back_populates="shifts")


Prenotation.shifts = relationship("Shift", back_populates="prenotations",
                                    order_by=Shift.date)


Base.metadata.create_all(engine)
