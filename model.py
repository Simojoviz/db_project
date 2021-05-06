from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
import datetime
import time
import calendar
from datetime import timedelta

engine = create_engine('sqlite:///database.db', echo=True)
# engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users
Prenotation = Base.classes.prenotations
Shift = Base.classes.shifts
WeekSetting = Base.classes.week_setting
GlobalSetting = Base.classes.global_setting



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
        exist = get_user(session, email=user.email)
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


# Generate a list of all shifts for a date given the date
def generate_daily_shifts(session, date):
    day_name = calendar.day_name[date.weekday()]
    weeksetting = session.query(WeekSetting).filter(WeekSetting.day_name == day_name).one_or_none()
    hour_start = weeksetting.starting
    hour_end = weeksetting.ending
    shift_lenght = weeksetting.lenght
    capacity = weeksetting.capacity
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

# - Given the starting date and the number of days generate the shifts for all days in time-interval
# - Given the starting date and the ending date    generate the shifts for all days in time-interval
# If there were previous plans which are changed, the previous is removed
def plan_shifts(session, starting, n=1, ending=None):
    day = starting + timedelta(days=1)
    if ending is None:
        ending = day + timedelta(days=n)
    while(day < ending):
        day_name = calendar.day_name[day.weekday()]
        ws = session.query(WeekSetting).filter(WeekSetting.day_name == day_name).one_or_none()
        if ws.changed is True:
            session.query(Shift).where(Shift.date==day).delete()
            l = generate_daily_shifts(session, datetime.date(year=day.year, month=day.month, day=day.day))
            add_shift_from_list(session, l)
        day = day + timedelta(days=1)

    session.query(WeekSetting).update({WeekSetting.changed:False}, synchronize_session = False)


# Returns all user-id who has prenoted for the shift given
def get_usersId_prenoted(session, shift):
    return session.query(User.id).join(Prenotation).filter(Prenotation.shift_id == shift.id)


# Returns the number of prenotations for the given Shift
def get_prenoted_count(session, shift):
    return get_usersId_prenoted(session, Shift).count()


# Returns the number of week-prenotations given the user and a date
def count_weekly_prenotations(session, user, date):
    # Move to monday
    day = date
    while(calendar.day_name[day.weekday()] != 'Monday')
        day = day - timedelta(days = 1)

    count = 0
    for i in range(7):
        shifts = get_shift(session, date = day):
            for sh in shifts:
               ids = get_usersId_prenoted(session, shift = sh)
               if user.id in ids:
                   count += 1
        day = day + timedelta(days = 1)
    
    return count


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


# ________________________________________ WEEK SETTING ________________________________________


# Returns the WeekSetting with the corresponding day_name
# Returns None if the day_name is not valid
def get_week_setting(session, day_name):
    return session.query(WeekSetting).filter(WeekSetting.day_name == day_name).one_or_none()

# Update the WeekSetting with the given parameters
def update_weekend_setting(session, day_name, starting=None, ending=None, lenght=None, capacity=None):
    session.query(WeekSetting).update({WeekSetting.changed:False}, synchronize_session = False)
    any_change = False

    # TODO FARE CONTROLLI SUI DATI IN INPUT

    if starting is not None:

        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.starting:starting}, synchronize_session = False)
        any_change = True
    if ending is not None:
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.ending:ending}, synchronize_session = False)
        any_change = True
    if lenght is not None:
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.lenght:lenght}, synchronize_session = False)
        any_change = True
    if capacity is not None:
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.capacity:capacity}, synchronize_session = False)
        any_change = True
    session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.changed:any_change}, synchronize_session = False)
    
    

# - Given a WeekSetting add it to the Database
# - Given WeekSetting's day_name, starting, ending, lenght and capacity add it to the Database
# Returns True if it was added correctly, False if the element was already contained
def add_week_setting(session, week_setting=None, day_name=None, starting=None, ending=None, lenght=None, capacity=None, changed=True):
    if week_setting is not None:
        exist = get_week_setting(session, day_name=week_setting.day_name)
        if exist is not None:
            return False
        else:
            session.add(week_setting)
            return True
    elif day_name is not None and\
         starting is not None and\
         ending   is not None and\
         lenght   is not None and\
         capacity is not None:
        exist = get_user(session, day_name=day_name)
        if exist is not None:
                return False
        else:
            session.add(WeekSetting(day_name=day_name, starting=starting, ending=ending, lenght=lenght, capacity=capacity, changed=changed))
            return True
    else:
        return False



# ________________________________________ GLOBAL SETTING ________________________________________

# Returns the GlobalSetting with the corresponding name
# Returns None if the name is not valid
def get_global_setting(session, name):
    return session.query(GlobalSetting).filter(GlobalSetting.name == name).one_or_none()

def add_global_setting(session, global_setting=None, name=None, value=None):
    if global_setting is not None:
        exist = get_global_setting(session, name=global_setting.name)
        if exist is not None:
            return False
        else:
            session.add(global_setting)
            return True
    elif name is not None and\
         value is not None :
        exist = get_user(session, name=name)
        if exist is not None:
                return False
        else:
            session.add(GlobalSetting(name=name, value=value)
            return True
    else:
        return False
    