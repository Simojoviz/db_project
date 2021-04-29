from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base


engine = create_engine('sqlite:///database.db', echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

User = Base.classes.users
Prenotation = Base.classes.prenotations
Shift = Base.classes.shifts

# Returns the user who has the email given, None if doesn't exists
def get_user(session, email):
    return session.query(User).filter(User.email == email).one_or_none()

# Adds a User to the Database given his fullname, email and password
# Returns True if it was added correctly, False if the element was already contained
def add_user(session, fullname, email, pwd):
    exist = get_user(session, email)
    if exist is not None:
        return False
    else:
        session.add(User(fullname=fullname, email=email, pwd=pwd))
        return True

# Adds the given User to the database
# Returns True if it was added correctly, False if the element was already contained
def add_user(session, user):
    exist = get_user(session, user.email)
    if exist is not None:
        return False
    else:
        session.add(user)
        return True

# Adds all Users from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_user_from_list(session, user_list):
    b = True
    for user in user_list:
        b &= add_user(session, user)
    return b

# Given date and starting hour returns the corresponding Shift if exists,
# Returns all Shifs of that date if the starting hour is not given
def get_shifts(session, date, start=None):
    if start is None:
        return session.query(Shift).filter(Shift.date == date).all()
    else:
        return session.query(Shift).\
            filter(Shift.date == date, Shift.h_start == start).one_or_none()

# Returns the list of all shifts for a date given the date, the starting and ending hour, the shift_lenght ad the capacity
def get_daily_shifts_list(date, hour_start, hour_end, shift_lenght, capacity):
    l = []
    start = hour_start
    end = start + shift_lenght
    while(end <= hour_end):
        l.append(Shift(date=date, h_start=start, h_end=end, capacity=capacity))
        start = end
        end = start + shift_lenght
    return l

# Adds a Shift to the Database given his date, starting and ending hour and capacity
# Returns True if it was added correctly, False if the element was already contained
def add_shift(session, date, start, end, capacity):
    exist = get_shifts(session, date, start)
    if exist is not None:
        return False
    else:
        session.add(Shift(date=date, h_start=start, h_end=end, capacity=capacity))
        return True

# Adds the given Shift to the Database
# Returns True if the element is added, False if the Database already contains the element """
def add_shift(session, shift):
    exist = get_shifts(session, shift.date, shift.h_start)
    if exist is not None:
        return False
    else:
        session.add(shift)
        return True

# Adds all Shifts from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_shift_from_list(session, shift_list):
    b = True
    for shift in shift_list:
        b &= add_shift(session, shift)
    return b

# Returns all Prenotations of the User given
def get_user_prenotations(session, user):
    return session.query(Prenotation).filter(Prenotation.client_id == user.id).all()

# Returns the Prenotation of the User for the Shift given
def get_prenotation(session, user, shift):
    return session.query(Prenotation).filter(Prenotation.client_id == user.id,
                                             Prenotation.shift_id == shift.id).one_or_none()
# Returns all users-id prenoted for the given shift
def get_usersId_prenoted(session, shift):
    return session.query(Prenotation.client_id).filter(Prenotation.shift_id == shift.id).all()

# Returns the number of prenotation for the given shift
def get_prenoted_count(session, shift):
    return session.query(Prenotation).filter(Prenotation.shift_id == shift.id).count()

# Returns all Prenotations in the Date given
def get_prenotations_by_date(session, date):
    return session.query(Prenotation).join(Shift).filter(Shift.date == date).all()

# Adds a Prenotation to the Database given the User and the Shift
# Returns True if it was added correctly,
# False if the element was already contained
# or the maximum capacity has already been reached for that shift
# or the User was already in that turn
def add_prenotation(session, user, shift):
    exist = get_prenotation(session, user, shift)
    if exist is not None:
        print(exist)
        return False
    else:
        nprenoted = get_prenoted_count(session, shift)
        if(nprenoted < shift.capacity):
            prenoted = get_usersId_prenoted(session, Shift)
            if user.id not in prenoted:
                session.add(Prenotation(client_id=user.id, shift_id=shift.id))
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
        b &= add_prenotation(session, prenotation)
    return b
