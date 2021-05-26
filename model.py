from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
import datetime
import time
import calendar
from datetime import timedelta

from sqlalchemy.sql.operators import exists

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

User          = Base.classes.users
Trainer       = Base.classes.trainers
Prenotation   = Base.classes.prenotations
Shift         = Base.classes.shifts
WeekSetting   = Base.classes.week_setting
GlobalSetting = Base.classes.global_setting
Course        = Base.classes.courses
CourseProgram = Base.classes.course_programs
Room          = Base.classes.rooms
CourseSignUp  = Base.classes.course_signs_up


# ________________________________________ UTILITIES ________________________________________ 

# Clamp the value X in the interval [A,B] given
def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    else:
        return x 


# Max function
def max(a, b):
    if a>b:
        return a
    return b


# Min function
def min(a, b):
    if a<b:
        return a
    return b


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
# - If all flag is true, returns all Users
# Otherwise return None
def get_user(session, id=None, email=None, prenotation=None, course_signing_up=None, all=False):
    if id is not None:
        return session.query(User).filter(User.id == id).one_or_none()
    elif email is not None:
        return session.query(User).filter(User.email == email).one_or_none()
    elif all is True:
        return session.query(User).all()
    else:
        return None

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
        add_user(session, user=User(fullname=fullname, email=email, pwd=pwd))
    else:
        return False

    
# Adds all Users from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_user_from_list(session, user_list):
    b = True
    for user in user_list:
        b &= add_user(session, user=user)
    return b


# ________________________________________ TRAINER ________________________________________ 


# - Given the email,     returns the Trainer who has got that email if exixsts
# - Given the id,        returns the Trainer who has got that id if exists
# - If all flag is true, returns all Trainers
# Otherwise return None
def get_trainer(session, id=None, email=None, all=False):
    if id is not None:
        return session.query(Trainer).filter(Trainer.id == id).one_or_none()
    elif email is not None:
        user = session.query(User).filter(User.email == email).one_or_none()
        if user is not None:
            return get_user(session, id=user.id)
        else:
            return None
    elif all is True:
        return session.query(Trainer).all()
    else:
        return None

# - Given User who is not a Trainer adds it to the database as a Trainer
# - Given fullname, email and password of a User who is not in the database adds it to Users and Trainers
# Returns True if it was added correctly, False if the element was already contained
def add_trainer(session, user=None, fullname=None, email=None, pwd=None):
    if user is not None:
        exist = get_trainer(session, id=user.id)
        if exist is None:
            session.add(Trainer(id=user.id))
            return True
        else:
            print("The user is already a Trainer")
            return False
    elif fullname is not None and\
         email    is not None and\
         pwd      is not None:
        exists = get_user(session, email = email)
        if exists is not None:
            # User with this email already exists, add it as a Trainer
            add_trainer(session, user = get_user(session, email=exists.email))
        else:
            # User does not exixsts, it is added as a User and then as a Trainer
            add_user(session, fullname=fullname, email=email, pwd=pwd)
            us = get_user(session, email=email)
            add_trainer(session, user=us)
    else:
        return False

    
# Adds all Trainers from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_trainer_from_list(session, user_list):
    b = True
    for us in user_list:
        b &= add_trainer(session, user=us)
    return b


# ________________________________________ SHIFT ________________________________________ 


# - Given a combination of date, starting hour, course_id and room id returns the corresponding Shift or Shifts
# - Given a prenotation returns the corresponding Shift
# - If all flag is true, returns all Shifts
# Otherwise return None
def get_shift(session, date=None, start=None, prenotation=None, id=None, course_id=None, room_id=None, all=False):

    # 4
    if date is not None and start is not None and room_id is not None and course_id is not None:
        return session.query(Shift).filter(Shift.date == date, Shift.h_start == start, Shift.room_id == room_id, Shift.course_id == course_id).one_or_none()
    
    # 3
    elif start is not None and date is not None and course_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.date == date, Shift.course_id == Shift.course_id).one_or_none()
    elif start is not None and date is not None and room_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.date == date, Shift.room_id == room_id).one_or_none()
    elif start is not None and room_id is not None and course_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.room_id == room_id, Shift.course_id == Shift.course_id).all()
    elif room_id is not None and date is not None and course_id is not None:
        return session.query(Shift).filter(Shift.room_id == room_id, Shift.date == date, Shift.course_id == Shift.course_id).all()
    
    # 2
    elif start is not None and date is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.date == date).all()
    elif start is not None and course_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.course_id == course_id).all()
    elif start is not None and room_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.room_id == room_id).all()
    elif course_id is not None and date is not None:
        return session.query(Shift).filter(Shift.course_id == course_id, Shift.date == date).all()
    elif room_id is not None and date is not None:
        return session.query(Shift).filter(Shift.room_id == room_id, Shift.date == date).all()
    elif course_id is not None and room_id is not None:
        return session.query(Shift).filter(Shift.course_id == course_id, Shift.room_id == room_id).all()

    # 1
    elif date is not None:
        return session.query(Shift).filter(Shift.date == date).all()
    elif course_id is not None:
        return session.query(Shift).filter(Shift.course_id == course_id).all()
    elif room_id is not None:
        return session.query(Shift).filter(Shift.room_id == room_id).all()
    
    elif id is not None:
        return session.query(Shift).filter(Shift.id == id).one_or_none()
    elif prenotation is not None:
        return session.query(Shift).filter(Shift.id == prenotation.shift_id).one_or_none()
    elif prenotation is not None:
        return session.query(Shift).filter(Shift.id == prenotation.shift_id).one_or_none()
    elif all is True:
        return session.query(Shift).all()
    else:
        return None

# Generate a list of all shifts for a date given the date
def generate_daily_shifts(session, date):
    day_name = calendar.day_name[date.weekday()]
    weeksetting = get_week_setting(session, day_name)
    hour_start = weeksetting.starting
    hour_end = weeksetting.ending
    shift_length = weeksetting.length
    course_id = get_course(session, name = 'OwnTraining').id
    rooms = get_room(session, all=True)
    
    l = []
    start =     timedelta(hours=hour_start.hour,   minutes=hour_start.minute)
    length =    timedelta(hours=shift_length.hour, minutes=shift_length.minute)
    end_ =      timedelta(hours=hour_end.hour,     minutes=hour_end.minute)
    end = start + length

    while(end <= end_):
        for room in rooms:
            l.append(
                Shift(
                    date=date,
                    h_start = datetime.time(hour=start.seconds//3600, minute=(start.seconds//60)%60),
                    h_end =   datetime.time(hour=end.seconds//3600, minute=(end.seconds//60)%60),
                    room_id = room.id,
                    course_id = course_id
                )
            )
        start = end
        end = start + length

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
        ws = get_week_setting(session, day_name=day_name)
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


# Returns the number of own-training-week-prenotations for the  given the user and a date
def get_count_weekly_prenotations(session, user, date):
    # Move to monday
    day = date
    while(calendar.day_name[day.weekday()] != 'Monday'):
        day = day - timedelta(days = 1)
    count = 0
    for i in range(7):
        shifts = get_shift(session, date = day, course_id = get_course(session, name='OwnTraining').id)
        for sh in shifts:
            ids = get_usersId_prenoted(session, shift = sh)
            if user.id in ids:
                count += 1
        day = day + timedelta(days = 1)
    
    return count


# - Given a Shift adds it to the database
# - Given a date, starting and ending hour, the room's id and course's id of a Shift adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_shift(session, shift=None, date=None, start=None, end=None, room_id=None, course_id=None):
    if shift is not None:
        exist = get_shift(session, date=shift.date, start=shift.h_start, room_id=shift.room_id)
        print(exist!=None)
        if exist is not None:
            return False
        else:
            session.add(shift)
            return True
    elif date      is not None and\
         start     is not None and\
         end       is not None and\
         room_id   is not None and\
         course_id is not None:
        add_shift(session, shift=Shift(date=date, h_start=start, h_end=end, room_id=room_id, course_id=course_id))
    else:
        return False


# Adds all Shifts from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_shift_from_list(session, shift_list):
    b = True
    for shift in shift_list:
        c = add_shift(session, shift=shift)
        print(c)
        b &= c
    return b


# ________________________________________ PRENOTATION ________________________________________ 


# - Given a User and a Shift returns the correponding Prenotation if exists
# - Given a User             returns all his prenotations
# - Given a Shift            returns all prenotations for that Shift
# - Given a date             returns all prenotations for that day
# - If all flag is true,     returns all Prenotations
# Returns None otherwise
def get_prenotation(session, user=None, shift=None, date=None, all=False):
    if user is not None and shift is not None:
        return session.query(Prenotation).filter(Prenotation.client_id == user.id, Prenotation.shift_id == shift.id).one_or_none()
    elif user is not None:
         return session.query(Prenotation).filter(Prenotation.client_id == user.id).all()
    elif shift is not None:
        return session.query(Prenotation.client_id).filter(Prenotation.shift_id == shift.id).all()
    elif date is not None:
        return session.query(Prenotation).join(Shift).filter(Shift.date == date).all()
    elif all is True:
        return session.query(Prenotation).all()
    else:
        return None   

# Adds a Prenotation to the Database given the User and the Shift or the Prenotion
# Returns True if it was added correctly,
# False if the element was already contained
# or the maximum capacity has already been reached for that shift
# or the User was already in that turn
# or the User has reached week-limit hours
def add_prenotation(session, user=None, shift=None, prenotation=None):
    if user is not None and shift is not None:
        exist = get_prenotation(session, user=user, shift=shift)
        if exist is not None:
            return False
        else:
            if shift.course_id == get_course(session, name='OwnTraining'):
                # Prenotation for OwnTraining: need some control
                nprenoted = get_prenoted_count(session, shift=shift)
                room_capacity = get_room(session, id=shift.room_id).max_capacity
                if(nprenoted < room_capacity):
                    prenoted = get_usersId_prenoted(session, Shift)
                    if user.id not in prenoted:
                        max_ = get_global_setting(session, name='MaxWeeklyEntry').value
                        count = get_count_weekly_prenotations(session, user, shift.date)
                        if (count < max_):
                            session.add(Prenotation(client_id=user.id, shift_id=shift.id))
                            return True
                        else:
                            print("Week prenotation peak reached")
                            return False
                    else:
                        print("User already prenoted")
                        return False
                else:
                    print("Maximum capacity already reached")
                    return False
            else:
                # Prenotation for a course: need no control
                session.add(Prenotation(client_id=user.id, shift_id=shift.id))
                return True
    elif prenotation is not None:
        user_  = get_user(session, id=prenotation.client_id)
        shift_ = get_shift(session, id=prenotation.shift_id)
        add_prenotation(session, user=user_, shift=shift_)
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
# If all flag is true, returns all WeekSettings

def get_week_setting(session, day_name=None, all=False):
    if day_name is not None:
        return session.query(WeekSetting).filter(WeekSetting.day_name == day_name).one_or_none()
    elif all is True:
        return session.query(WeekSetting).all()
    else:
        return None

# Update the WeekSetting with the given parameters
def update_weekend_setting(session, day_name, starting=None, ending=None, length=None, capacity=None):
    
    any_change = False

    if starting is not None:
        h_start = session.query(GlobalSetting).filter(GlobalSetting.name == "HourStarting")
        if starting.hour < h_start:
            starting = datetime.time(hour=h_start)
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.starting:starting}, synchronize_session = False)
        any_change = True

    if ending is not None:
        h_end = session.query(GlobalSetting).filter(GlobalSetting.name == "HourEnding")
        if ending.hour > h_end:
            ending = datetime.time(hour=h_end)
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.ending:ending}, synchronize_session = False)
        any_change = True
        
    if length is not None:
        min_len = get_global_setting(session, name='MinimumShiftLength').value
        max_len = get_global_setting(session, name='MaximumShiftLength').value
        length_min = clamp(length.minute + length.hour * 60, min_len, max_len)
        length_hour = int(length_min / 60)
        length_min =  int(length_min % 60)
        length = datetime.time(hour = length_hour, minute=length_min)
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.length:length}, synchronize_session = False)
        any_change = True

    if capacity is not None:
        covid_capacity = get_global_setting(session, name='CovidCapacity').value
        capacity = clamp(capacity, 1, covid_capacity)
        session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.capacity:capacity}, synchronize_session = False)
        any_change = True

    session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.changed:any_change}, synchronize_session = False)
    
    

# - Given a WeekSetting add it to the Database
# - Given WeekSetting's day_name, starting, ending, length and capacity add it to the Database
# Returns True if it was added correctly, False if the element was already contained
def add_week_setting(session, week_setting=None, day_name=None, starting=None, ending=None, length=None, capacity=None, changed=True):
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
         length   is not None and\
         capacity is not None:
        exist = get_week_setting(session, day_name=day_name)
        if exist is not None:
                return False
        else:
            session.add(WeekSetting(day_name=day_name, starting=starting, ending=ending, length=length, capacity=capacity, changed=changed))
            return True
    else:
        return False



# ________________________________________ GLOBAL SETTING ________________________________________

# Returns the GlobalSetting with the corresponding name
# If all flag is true, returns all GlobalSettings
# Returns None if the name is not valid

def get_global_setting(session, name=None, all=False):
    if name is not None:
        return session.query(GlobalSetting).filter(GlobalSetting.name == name).one_or_none()
    elif all is True:
        return session.query(GlobalSetting).all()
    else:
        return None

# - Given a GlobalSetting add it to the Database
# - Given GlobalSetting's name and value add it to the Database
# Returns True if it was added correctly, False if the element was already contained
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
            session.add(GlobalSetting(name=name, value=value))
            return True
    else:
        return False


# Update the GlobalSetting with the given parameters
def update_global_setting(session, CovidCapacity=None, MinutesShiftLength=None, MaxWeeklyEntry=None):

    def update(name, val):
        session.query(GlobalSetting).filter(GlobalSetting.name == name).update({GlobalSetting.value:val}, synchronize_session = False)
    
 
    if CovidCapacity is not None:
        CovidCapacity = clamp(
            CovidCapacity,
            1,
            get_global_setting(session, name='MaxCapacity').value
        )
        update('CovidCapacity', CovidCapacity)

    if MinutesShiftLength is not None:

        MinutesShiftLength = clamp(
            MinutesShiftLength,
            get_global_setting(session, name='MinimumShiftLength').value,
            get_global_setting(session, name='MaximumShiftLength').value
        )
        update('MinutesShiftLength', MinutesShiftLength)

    if MaxWeeklyEntry is not None:

        MaxWeeklyEntry = clamp(
            MaxWeeklyEntry,
            1,
            100
        )
        update('MaxWeeklyEntry', MaxWeeklyEntry)


# ________________________________________ ROOM ________________________________________

# - Given the id,        returns the Room who has got that id if exixsts
# - Given the name,      returns the Room who has got that name if exists
# - If all flag is true, returns all Rooms
# Otherwise returns None
def get_room(session, id=None, name=None, all=False):
    if id is not None:
        return session.query(Room).filter(Room.id == id).one_or_none()
    elif name is not None:
        return session.query(Room).filter(Room.name == name).one_or_none()
    elif all is True:
        return session.query(Room).all()
    else:
        None


# - Given a Room adds it to the database
# - Given name and max_capacity of a Room adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_room(session, room=None, name=None, max_capacity=None):
    if room is not None:
        exist = get_room(session, id=room.id)
        if exist is not None:
            return False
        else:
            session.add(room)
            return True
    elif name         is not None and\
         max_capacity is not None:
        add_room(session, room=Room(name=name, max_capacity=max_capacity))
    else:
        return False
    
# Adds all Rooms from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_room_from_list(session, rooms_list):
    b = True
    for room in rooms_list:
        b &= add_room(session, room=room)
    return b


# ________________________________________ COURSE ________________________________________

# - Given the id,        returns the Course who has got that id if exixsts
# - Given the name,      returns the Course who has got that name if exists
# - If all flag is true, returns all Courses
# Otherwise return None
def get_course(session, id=None, name=None, all=False):
    if id is not None:
        return session.query(Course).filter(Course.id == id).one_or_none()
    elif name is not None:
        return session.query(Course).filter(Course.name == name).one_or_none()
    elif all is True:
        return session.query(Course).all()
    else:
        return None

# Given the name of the Course plan his Shifts
# If the course overlap with any other the plan fails
def plan_course(session, name):

    def get_shift_turn(session, date, room_id, turn):
        shifts = get_shift(session, date=date, room_id=room_id)
        if len(shifts) >= turn:
            return shifts[turn]
        else:
            return None

    def update_shift_course(session, shift_id, new_course_id):
        session.query(Shift).filter(Shift.id == shift_id).update({Shift.course_id:new_course_id}, synchronize_session = False)
        

    course = get_course(session, name=name)
    courses_program = get_course_program(session, course_id=course.id)
    own_training_id = get_course(session, name='OwnTraining').id
    print("OWN")
    print(own_training_id)
    end = course.ending + timedelta(days=0)
    for prog in courses_program:
        dayname = prog.week_day
        turn = prog.turn_number
        room_id = prog.room_id
        day = course.starting + timedelta(days=0)
        while(calendar.day_name[day.weekday()] != dayname): # Move to the correct week day
            day = day + timedelta(days = 1)
        while(day < end):
            shift = get_shift_turn(session, date=datetime.date(year=day.year, month=day.month, day=day.day), room_id=room_id, turn=turn)
            if shift is None:
                print("There is not that turn in that day")
                return False
            if(shift.course_id != own_training_id):
                print("Course cannot be planned: it overlaps with an other course!")
                # TODO capire come fare la rollback degli shift che sono stati cambiati
                # Session interna e non quella ricevuta come argomento?
                return False
            else:
                # Delete all Prenotation in that Shift
                session.query(Prenotation).where(Prenotation.shift_id==shift.id).delete()
                update_shift_course(session, shift.id, course.id)
            day = day + timedelta(days=7)
            
        

# - Given a Course adds it to the database
# - Given name, starting and ending date, max_partecipants and the instructor_id of a Course adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_course(session, course=None, name = None, starting=None, ending=None, max_partecipants=None, instructor_id=None):
    if course is not None:
        exist = get_course(session, id=course.id)
        if exist is not None:
            return False
        else:
            session.add(course)
            return True
    elif name             is not None and\
         starting         is not None and\
         ending           is not None and\
         max_partecipants is not None and\
         instructor_id    is not None:
        add_course(session, course=Course(name=name, starting=starting, ending=ending, max_partecipants=max_partecipants, instructor_id=instructor_id))
    else:
        return False
    
# Adds all Courses from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_course_from_list(session, courses_list):
    b = True
    for course in courses_list:
        b &= add_course(session, course=course)
    return b


# ________________________________________ COURSE PROGRAM ________________________________________

# - Given the id,          returns the CourseProgram who has got that id if exixsts
# - Given the course_id,   returns all his CoursePrograms
# - If all flag is true,   returns all CoursePrograms
# Otherwise return None
def get_course_program(session, id=None, course_id=None, all=False):
    if id is not None:
        return session.query(CourseProgram).filter(CourseProgram.id == id).one_or_none()
    elif course_id is not None:
        return session.query(CourseProgram).filter(CourseProgram.course_id == course_id).all()
    elif all is True:
        return session.query(CourseProgram).all()
    else:
        return None


# - Given a CourseProgram adds it to the database
# - Given week_day, turn_number, room_id and cours_id of a CourseProgram adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_course_program(session, course_program=None, week_day=None, turn_number=None, room_id=None, course_id=None):
    if course_program is not None:
        exist = get_course_program(session, id=course_program.id)
        if exist is not None:
            return False
        else:
            session.add(course_program)
            return True
    elif week_day    is not None and\
         turn_number is not None and\
         room_id     is not None and\
         course_id   is not None:
        add_course_program(session, course=CourseProgram(week_day=week_day, turn_number=turn_number, room_id=room_id, course_id=course_id))
    else:
        return False
    
# Adds all CoursePrograms from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_course_program_from_list(session, course_programs_list):
    b = True
    for course_program in course_programs_list:
        b &= add_course_program(session, course_program=course_program)
    return b


# ________________________________________ COURSE SIGN UP ________________________________________


# - Given a UserID       returns all his course signs up
# - Given a CourseId     returns all his course signs up
# - If all flag is true, returns all CourseSignsUp
# Returns None otherwise
def get_course_sign_up(session, user_id=None, course_id=None, all=False):
    if user_id is not None and course_id is not None:
        return session.query(CourseSignUp).filter(CourseSignUp.user_id == user_id, CourseSignUp.course_id == course_id).one_or_none()
    elif user_id is not None:
        return session.query(CourseSignUp).filter(CourseSignUp.user_id == user_id).all()
    elif course_id is not None:
        return session.query(CourseSignUp).filter(CourseSignUp.course_id == course_id).all()
    elif all is True:
        return session.query(CourseSignUp).all()
    else:
        return None

def count_course_sign_up(session, name):
    course = get_course(session, name=name)
    courses_signs_up = get_course_sign_up(session, course_id=course.id)
    return len(courses_signs_up)


# Adds a CourseSignUp to the Database given the User and the Course or the CourseSignUp
# Returns True if it was added correctly,
# False if
#   the user has already SignedUp to the course
#   the capacity peak has already been reached
# TODO the course in in conflict with other courses the user has SignedIn
# 
def add_course_sign_up(session, user=None, course=None, course_sign_up=None):

    if user is not None and course is not None:
        exist = get_course_sign_up(session, user_id=user.id, course_id=course.id)
        if exist is not None:
            return False
        else:
            n_signed = count_course_sign_up(session, course.name)
            n_max = course.max_partecipants
            if  n_signed>= n_max:
                print("Course peak has already been reached")
                return False
            else:
                course_signs = get_course_sign_up(session, user_id=user.id)
                ids = []
                for sign in course_signs:
                    ids.append(sign.course_id)
                if course.id in ids:
                    print("User has already signed up for the course")
                    return False
                else:
                    session.add(CourseSignUp(user_id=user.id, course_id=course.id))
                    shifts = get_shift(session, course_id=course.id)
                    prenotations = []
                    for sh in shifts:
                        add_prenotation(session, user=user, shift=sh)
                    return True
    elif course_sign_up is not None:
        user_  =  get_user(session, id=course_sign_up.user_id)
        course_ = get_shift(session, id=course_sign_up.user_id)
        add_course_sign_up(session, user=user_, course=course_)
    else:
        return False


# Adds all CourseSignUp from the list given to the Database
# Returns True if all elements were added,
# False if at least one was already contained or the maximum capacity has already been reached for that shift
def add_course_sign_up_from_list(session, course_sign_up_list):
    b = True
    for course_sign_up in course_sign_up_list:
        b &= add_course_sign_up(session, course_sign_up=course_sign_up)
    return b
