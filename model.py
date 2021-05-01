from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
import datetime
import time
from datetime import timedelta

engine = create_engine('sqlite:///database.db', echo=True)
# engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users
Prenotation = Base.classes.prenotations
Shift = Base.classes.shifts



# ________________________________________ TO STRING ________________________________________ 


# Return the given input as a string
def to_string(user=None, shift=None):
    if user is not None:
        return user.fullname + "(" + user.email + ")\n"
    elif shift is not None:
        return "Day: " + shift.date.strftime("%Y-%m-%d") +\
               " ("    + shift.h_start.strftime("%H:%M") +\
               " --> " + shift.h_end.strftime("%H:%M") + ")\n"


# ________________________________________ USER ________________________________________ 


# - Given the email,     returns the User who has got that email if exixsts
# - Given the id,        returns the User who has got that id if exists
# - Given a prenotation, returns the User who did the prenotation
# Otherwise return None
def get_user(session, id=None, email=None, prenotation=None):
    if id is not None:
        return session.query(User).filter(User.id == id).one_or_none()
    elif email is not None:
        return session.query(User).filter(User.email == email).one_or_none()
    elif prenotation is not None:
        return session.query(User).filter(User.id == prenotation.client_id).one_or_none()
    else:
        return None


# Returns all user emails
def get_all_emails(session):
    return session.query(User.email).all()


# - Given a User adds it to the database
# - Given fullname, email and password of a User adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_user(session, user=None, fullname=None, email=None, pwd=None):
    if user is not None:
        exist = get_user(session, id=user.id)
        if exist is not None:
            return False
        else:
            session.add(user)
            return True
    elif fullname is not None and\
         email    is not None and\
         pwd      is not None:
        exist = get_user(session, id=id)
        if exist is not None:
                return False
        else:
            session.add(User(fullname=fullname, email=email, pwd=pwd))
            return True
    else:
        return False

    
# Adds all Users from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_user_from_list(session, user_list):
    b = True
    for user in user_list:
        b &= add_user(session, user=user)
    return b


# ________________________________________ SHIFT ________________________________________ 


# - Given a date returns all Shifts in that day
# - Given a date and a starting hour return the corresponding Shift if exists
# - Given a prenotation returns the corresponding Shift
# Otherwise return None
def get_shift(session, date=None, start=None, prenotation=None):
    if date is not None:
        if start is None:
            return session.query(Shift).filter(Shift.date == date).all()
        else:
            return session.query(Shift).filter(Shift.date == date, Shift.h_start == start).one_or_none()
    elif prenotation is not None:
        return session.query(Shift).filter(Shift.id == prenotation.shift_id).one_or_none()
    else:
        return None


# Returns the list of all shifts for a date given the date, the starting and ending hour, the shift_lenght ad the capacity
def get_daily_shifts(date, hour_start, hour_end, shift_lenght, capacity):
    l = []
    start =     timedelta(hours=hour_start.hour,   minutes=hour_start.minute)
    lenght =    timedelta(hours=shift_lenght.hour, minutes=shift_lenght.minute)
    hour_end_ = timedelta(hours=hour_end.hour,     minutes=hour_end.minute)
    end = start + lenght
    while(end <= hour_end_):
        l.append(Shift(
            date=date,
            h_start= datetime.time(hour=start.seconds//3600, minute=(start.seconds//60)%60),
            h_end=   datetime.time(hour=end.seconds//3600, minute=(end.seconds//60)%60),
            capacity=capacity
        ))
        start = end
        end = start + lenght
    return l


# Returns all user-id who has prenoted for the shift given
def get_usersId_prenoted(session, Shift):
    return session.query(User.id).join(Prenotation).filter(Prenotation.shift_id == Shift.id)


# Returns the number of prenotations for the given Shift
def get_prenoted_count(session, shift):
    return get_usersId_prenoted(session, Shift).count()


# - Given a Shift adds it to the database
# - Given a date, starting and ending hour and capacity of a Shift adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_shift(session, shift=None, date=None, start=None, end=None, capacity=None):
    if shift is not None:
        exist = get_shift(session, date=shift.date, start=shift.h_start)
        if exist is not None:
            return False
        else:
            session.add(shift)
            return True
    elif date     is not None and\
         start    is not None and\
         end      is not None and\
         capacity is not None:
        exist = get_shift(session, date=date, start=start)
        if exist is not None:
            return False
        else:
            session.add(Shift(date=date, h_start=start, h_end=end, capacity=capacity))
            return True
    else:
        return False


# Adds all Shifts from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_shift_from_list(session, shift_list):
    b = True
    for shift in shift_list:
        b &= add_shift(session, shift=shift)
    return b


# ________________________________________ PRENOTATION ________________________________________ 


# - Given a User and a Shift returns the correponding Prenotation if exists
# - Given a User             returns all his prenotations
# - Given a Shift            returns all prenotations for that Shift
# - Given a date             returns all prenotations for that day
# Returns None otherwise
def get_prenotation(session, user=None, shift=None, date=None):
    if user is not None and shift is not None:
        return session.query(Prenotation).filter(Prenotation.client_id == user.id, Prenotation.shift_id == shift.id).one_or_none()
    elif user is not None:
         return session.query(Prenotation).filter(Prenotation.client_id == user.id).all()
    elif shift is not None:
        return session.query(Prenotation.client_id).filter(Prenotation.shift_id == shift.id).all()
    elif date is not None:
        return session.query(Prenotation).join(Shift).filter(Shift.date == date).all()
    else:
        return None   

# Adds a Prenotation to the Database given the User and the Shift or the Prenotion
# Returns True if it was added correctly,
# False if the element was already contained
# or the maximum capacity has already been reached for that shift
# or the User was already in that turn
def add_prenotation(session, user=None, shift=None, prenotation=None):
    if user is not None and shift is not None:
        exist = get_prenotation(session, user=user, shift=shift)
        if exist is not None:
            return False
        else:
            nprenoted = get_prenoted_count(session, shift=shift)
            if(nprenoted < shift.capacity):
                prenoted = get_usersId_prenoted(session, Shift)
                if user.id not in prenoted:
                    session.add(Prenotation(client_id=user.id, shift_id=shift.id))
                else:
                    return False
            else:
                return False
    elif prenotation is not None:
        user_  = get_user(session, prenotation=prenotation)
        shift_ = get_shift(session, prenotation=prenotation)
        exist = get_prenotation(session, user=user_, shift=shift_)
        if exist is not None:
            return False
        else:
            nprenoted = get_prenoted_count(session, shift=shift_)
            if(nprenoted < shift_.capacity):
                prenoted = get_usersId_prenoted(session, shift_)
                if user.id not in prenoted:
                    session.add(Prenotation(client_id=user_.id, shift_id=shift_.id))
                else:
                    return False
            else:
                return False
    else:
        return False



# Adds all Prenotation from the list given to the Database
# Returns True if all elements were added,
# False if at least one was already contained or the maximum capacity has already been reached for that shift
def add_prenotation_from_list(session, prenotation_list):
    b = True
    for prenotation in prenotation_list:
        b &= add_prenotation(session, prenotation=prenotation)
    return b
