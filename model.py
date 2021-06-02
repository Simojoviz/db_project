from sqlalchemy import create_engine

import datetime
from datetime import timedelta
import calendar

from automap import *

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


# ________________________________________ USER ________________________________________ 


# - Given the email,     returns the User who has got that email if exixsts
# - Given the id,        returns the User who has got that id if exists
# - If all flag is true, returns all Users
# Otherwise return None
def get_user(session, id=None, email=None, all=False):
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
def add_user(session, fullname=None, email=None, pwd=None, user=None):
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
        user = get_user(session, email=email)
        if user is not None:
            return get_trainer(session, id=user.id)
        else:
            return None
    elif all is True:
        return session.query(Trainer).all()
    else:
        return None

# - Given a User, if it's neither a User nor a Trainer, adds it to the database both as User and Trainer; returns True
#                 if it's a User yet, but not a Trainer, adds it to the database as a Trainer; return True
#                 if it's both a User and Trainer yet, returns False
# - Given fullname, email and password of a User does the same as above
# Returns True if it was added correctly, False if the element was already contained
def add_trainer(session, fullname=None, email=None, pwd=None, user=None):
    if user is not None:
        if get_user(session, email=user.email) is None:
            # a) Neither a User nor a Trainer
            add_user(session,user=user)
            new = get_user(session, email=user.email)
            session.add(Trainer(id=new.id))
            return True
        elif get_trainer(session, id=user.id) is None:
            # b) User yet, but not a Trainer
            session.add(Trainer(id=user.id))
            return True
        else:  
            # c) Both a User and a Trainer
            return False
    elif fullname is not None and\
         email    is not None and\
         pwd      is not None: 
        return add_trainer(session, user=User(fullname=fullname, email=email, pwd=pwd))
    else:
        return False

    
# Adds all Trainers from the user_list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_trainer_from_list(session, user_list):
    b = True
    for us in user_list:
        b &= add_trainer(session, user=us)
    return b


# ________________________________________ SHIFT ________________________________________ 


# - Given a combination of date, starting hour, course_id and room_id returns the corresponding Shift or Shifts
# - Given a prenotation returns the corresponding Shift
# - If all flag is True, returns all Shifts
# Otherwise return None
def get_shift(session, date=None, start=None, prenotation=None, id=None, course_id=None, room_id=None, all=False):

    # Four parameters
    if date is not None and start is not None and room_id is not None and course_id is not None:
        return session.query(Shift).filter(Shift.date == date, Shift.h_start == start, Shift.room_id == room_id, Shift.course_id == course_id).one_or_none()
    
    # Three parameters
    elif start is not None and date is not None and course_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.date == date, Shift.course_id == Shift.course_id).one_or_none()
    elif start is not None and date is not None and room_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.date == date, Shift.room_id == room_id).one_or_none()
    elif start is not None and room_id is not None and course_id is not None:
        return session.query(Shift).filter(Shift.h_start == start, Shift.room_id == room_id, Shift.course_id == Shift.course_id).all()
    elif room_id is not None and date is not None and course_id is not None:
        return session.query(Shift).filter(Shift.room_id == room_id, Shift.date == date, Shift.course_id == Shift.course_id).all()
    
    # Two parameters
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

    # One parameter
    elif date is not None:
        return session.query(Shift).filter(Shift.date == date).all()
    elif course_id is not None:
        return session.query(Shift).filter(Shift.course_id == course_id).all()
    elif room_id is not None:
        return session.query(Shift).filter(Shift.room_id == room_id).all()
    

    elif id is not None:
        return session.query(Shift).filter(Shift.id == id).one_or_none()

    elif prenotation is not None:
        return prenotation.shift 
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
    course_id = None
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


# - Given a Shift adds it to the database
# - Given a date, starting and ending hour, the room's id and course's id of a Shift adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_shift(session, date=None, start=None, end=None, room_id=None, course_id=None, shift=None):
    if shift is not None:
        exist = get_shift(session, date=shift.date, start=shift.h_start, room_id=shift.room_id)
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
        b &= c
    return b


# ________________________________________ PRENOTATION ________________________________________ 


# - Given a user_id and a shift_id returns the correponding Prenotation if exists
# - Given a user_id                returns all his prenotations
# - Given a shift_id               returns all prenotations for that Shift
# - Given a date                   returns all prenotations for that day
# - If all flag is true,           returns all Prenotations
# Returns None otherwise
def get_prenotation(session, user_id=None, shift_id=None, date=None, all=False):
    if user_id is not None and shift_id is not None:
        return session.query(Prenotation).filter(Prenotation.client_id == user_id, Prenotation.shift_id == shift_id).one_or_none()
    elif user_id is not None:
         return session.query(Prenotation).filter(Prenotation.client_id == user_id).all()
    elif shift_id is not None:
        return session.query(Prenotation.client_id).filter(Prenotation.shift_id == shift_id).all()
    elif date is not None:
        return session.query(Prenotation).join(Shift).filter(Shift.date == date).all()
    elif all is True:
        return session.query(Prenotation).all()
    else:
        return None   

# - Given a User and a Shift adds the corresponding Prenotation to the Database
# - Given a Prenotation adds it to the Database
# Returns True if it was added correctly, False if the element was already contained
# Raise an Exception if
# - shift is occupied by a course
# - maximum capacity has already been reached
# - the user is already in that turn
# - the user has reached week-limit hours
def add_prenotation(session, user=None, shift=None, prenotation=None):

    # Returns the number of own-training-week-prenotations for the  given the user and a date
    def get_count_weekly_prenotations(session, user, date):
        # Move to monday
        day = date
        while(calendar.day_name[day.weekday()] != 'Monday'):
            day = day - timedelta(days = 1)
        count = 0
        for i in range(7):
            shifts = get_shift(session, date = day)
            for sh in shifts:
                users = sh.users_prenotated
                if user in users:
                    count += 1
            day = day + timedelta(days = 1)
        
        return count

    if user is not None and shift is not None:
        exist = get_prenotation(session, user_id=user.id, shift_id=shift.id)
        if exist is not None:
            raise Exception("User already prenoted")
        else:
            if shift.course_id == None:
                nprenoted = len(shift.users_prenotated)
                room_capacity = get_room(session, id=shift.room_id).max_capacity
                if(nprenoted < room_capacity):
                    max_ = get_global_setting(session, name='MaxWeeklyEntry').value
                    count = get_count_weekly_prenotations(session, user, shift.date)
                    if (count < max_):
                        session.add(Prenotation(client_id=user.id, shift_id=shift.id))
                        return True
                    else:
                        raise Exception("Week prenotation peak reached")
                else:
                    raise Exception("Maximum capacity already reached")
            else:
                raise Exception("Shift occupied by a course")
    elif prenotation is not None:
        user_  = get_user(session, id=prenotation.client_id)
        shift_ = get_shift(session, id=prenotation.shift_id)
        add_prenotation(session, user=user_, shift=shift_)
    else:
        return False


# Adds all Prenotation from the list given to the Database
# Returns True if all elements were added, False otherwise
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
def update_weekend_setting(session, day_name, starting=None, ending=None, length=None):
    
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

    session.query(WeekSetting).filter(WeekSetting.day_name == day_name).update({WeekSetting.changed:any_change}, synchronize_session = False)
    
    

# - Given a WeekSetting add it to the Database
# - Given WeekSetting's day_name, starting, ending and length  add it to the Database
# Returns True if it was added correctly, False if the element was already contained
def add_week_setting(session, day_name=None, starting=None, ending=None, length=None, week_setting=None):
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
         length   is not None:
        exist = get_week_setting(session, day_name=day_name)
        add_week_setting(session, WeekSetting(day_name=day_name, starting=starting, ending=ending, length=length, changed=True))
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
def add_global_setting(session,name=None, value=None,  global_setting=None):
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
def add_room(session, name=None, max_capacity=None, room=None):
    if room is not None:
        exist = get_room(session, name=room.name)
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
# It raises an exception if:
# - there's no the turn in that day
# - the course overlaps with any other 
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
    own_training_id = None
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
                raise Exception("There is not that turn in that day")
            if(shift.course_id != own_training_id):
                raise Exception("Course cannot be planned: it overlaps with an other course!")
            else:
                # Delete all Prenotation in that Shift
                session.query(Prenotation).where(Prenotation.shift_id==shift.id).delete()
                update_shift_course(session, shift.id, course.id)
            day = day + timedelta(days=7)
            
        

# - Given a Course adds it to the database
# - Given name, starting and ending date, max_partecipants and the instructor_id of a Course adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_course(session, name = None, starting=None, ending=None, max_partecipants=None, instructor_id=None, course=None):
    if course is not None:
        exist = get_course(session, name=course.name)
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
def get_course_program(session, id=None, course_id=None, week_day=None, turn_number=None, all=False):
    if id is not None:
        return session.query(CourseProgram).filter(CourseProgram.id == id).one_or_none()
    elif course_id is not None and week_day is not None and turn_number is not None:
        return session.query(CourseProgram).filter(CourseProgram.course_id == course_id, CourseProgram.week_day == week_day, CourseProgram.turn_number == turn_number).one_or_none()
    elif course_id is not None:
        return session.query(CourseProgram).filter(CourseProgram.course_id == course_id).all()
    elif all is True:
        return session.query(CourseProgram).all()
    else:
        return None


# - Given a CourseProgram adds it to the database
# - Given week_day, turn_number, room_id and cours_id of a CourseProgram adds it to the database
# Returns True if it was added correctly, False if the element was already contained
def add_course_program(session, week_day=None, turn_number=None, room_id=None, course_id=None, course_program=None,):
    if course_program is not None:
        exist = get_course_program(session, course_id=course_program.course_id, week_day=course_program.week_day, turn_number=course_program.turn_number)
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


# Adds a CourseSignUp to the Database given the User and the Course or the CourseSignUp
# Returns True if it was added correctly, False otherwise
# Raises an error if
#  - the user has already SignedUp to the course
#  - the capacity peak has already been reached
# TODO the course in in conflict with other courses the user has SignedIn
# 
def add_course_sign_up(session, user=None, course=None, course_sign_up=None):

    if user is not None and course is not None:
        exist = get_course_sign_up(session, user_id=user.id, course_id=course.id)
        if exist is not None:
            raise Exception("The user has already sign-up for the course")
        else:
            n_signed = len(course.users)
            n_max = course.max_partecipants
            if  n_signed>= n_max:
                raise Exception("Course peak has already been reached")
            else:
                course_signs = get_course_sign_up(session, user_id=user.id)
                ids = []
                for sign in course_signs:
                    ids.append(sign.course_id)
                if course.id in ids:
                    raise Exception("User has already signed up for the course")
                else:
                    session.add(CourseSignUp(user_id=user.id, course_id=course.id))
    elif course_sign_up is not None:
        user_  =  get_user(session, id=course_sign_up.user_id)
        course_ = get_shift(session, id=course_sign_up.user_id)
        add_course_sign_up(session, user=user_, course=course_)
    else:
        return False


# Adds all CourseSignUp from the list given to the sDatabase
# Returns True if all elements were added,
# False if at least one was already contained or the maximum capacity has already been reached for that shift
def add_course_sign_up_from_list(session, course_sign_up_list):
    b = True
    for course_sign_up in course_sign_up_list:
        b &= add_course_sign_up(session, course_sign_up=course_sign_up)
    return b

def delete_course_sign_up(session, course=None, user=None):
    if course is not None and user is not None:
        cs = get_course_sign_up(session, user_id = user.id, course_id = course.id)
        session.delete(cs)
        session.commit()
        return True
    elif course is not None:
        cs = get_course_sign_up(session,course_id=course.id)
        session.delete(cs)
        session.commit()
        return True
    elif user is not None:
        cs = get_course_sign_up(session,user_id=user.id)
        session.delete(cs)
        session.commit()
        return True
    return False