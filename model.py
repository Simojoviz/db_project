from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base


engine = create_engine('sqlite:///database.db', echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users
Prenotation = Base.classes.prenotations
Shift = Base.classes.shifts


def get_user(session, email):
    return session.query(User).filter(User.email == email).one_or_none()


def add_user(session, fullname, email, pwd):
    exist = get_user(session, email)
    if exist is not None:
        return False
    else:
        session.add(User(fullname=fullname, email=email, pwd=pwd))
        return True


def get_shifts(session, date, start=None):
    if start is None:
        return session.query(Shift).filter(Shift.date == date).all()
    else:
        return session.query(Shift).\
            filter(Shift.date == date, Shift.h_start == start).one_or_none()


def add_shift(session, date, start, end, capacity):
    exist = get_shifts(session, date, start)
    if exist is not None:
        return False
    else:
        session.add(Shift(date=date, h_start=start, h_end=end, capacity=capacity))
        return True


def get_user_prenotations(session, user):
    return session.query(Prenotation).filter(Prenotation.client_id == user.id).all()


def get_prenotations_by_date(session, date):
    return session.query(Prenotation).join(Shift).filter(Shift.date == date).all()


def get_prenotation(session, user, shift):
    return session.query(Prenotation).filter(Prenotation.client_id == user.id,
                                             Prenotation.shift_id == shift.id)


def add_prenotation(session, user, shift):
    exist = get_prenotation(session, user, shift)
    if exist is not None:
        return False
    else:
        session.add(Prenotation(client_id=user.id, shift_id=shift.id))
