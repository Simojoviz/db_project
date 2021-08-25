from sqlalchemy import create_engine

import datetime
from datetime import timedelta
import calendar

from sqlalchemy.sql.expression import text
from sqlalchemy.sql.operators import exists

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

def time_to_timedelta(time_obj):
        return timedelta(hours=time_obj.hour, minutes=time_obj.minute)

def timedelta_to_time(time_delta):
    return datetime.time(hour=time_delta.hour, minute=time_delta.minute)

# ________________________________________ USER ________________________________________ 


# - Given the email,         returns the User who has got that email if exixsts
# - Given the id,            returns the User who has got that id if exists
# - If all flag is set True, returns all Users
# Otherwise returns None
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
# - Given fullname, email, address, telephone and password of a User adds it to the database
# Returns True if it was added correctly, False otherwise
def add_user(session, fullname=None, email=None, address=None, telephone=None, pwd=None, user=None):
    if user is not None:
        exist = get_user(session, email=user.email)
        if exist is not None:
            return False
        else:
            session.add(user)
            session.flush()
            add_user_role(session, user=user, role=get_role(session, name='Client'))
            return True
    elif fullname     is not None and\
         email        is not None and\
         address      is not None and\
         telephone    is not None and\
         pwd          is not None:
        return add_user(session, user=User(fullname=fullname, email=email, address=address, telephone=telephone, pwd=pwd, covid_state=0, subscription=datetime.date.today()))
    else:
        return False

    
# Adds all Users from the list given to the Database
# Returns True if all elements were added, False otherwise
def add_user_from_list(session, user_list):
    b = True
    for user in user_list:
        b &= add_user(session, user=user)
    return b


# Given user_id and at least one parameter update the value if has changed
# - If covid_state changes,         notifies with a Message
# - If subscription changes, notifies with a Message
def update_user(session, user_id=None, fullname=None, telephone=None, address=None, pwd=None, covid_state=None, subscription=None ):
    user = get_user(session, id=user_id)
    if user is not None:
        if fullname is not None and fullname != user.fullname:
            user.fullname = fullname
        if telephone is not None and telephone != user.telephone:
            user.telephone = telephone
        if address is not None and address != user.address:
            user.address = address
        if pwd is not None and pwd != user.pwd:
            user.pwd = pwd
        if covid_state is not None and covid_state != user.covid_state:
            user.covid_state = covid_state
            admin_id = get_admin_id(session)
            if covid_state == 0:
                text = "Your covid state is now Free! You can prenote"
            elif covid_state == 1:
                text = "You came into contacts with a person affected form Covid19! You can't prenote. Please contact Gym's Admin"
            else:
                text = "You signaled you're positive for Covid19! You can't prenote. Please contact Gym's Admin"
            add_message(session, sender_id=admin_id, addresser_id=user_id, text=text)
        if subscription is not None and subscription != user.subscription:
            user.subscription = subscription
            admin_id = get_admin_id(session)
            add_message(session, sender_id=admin_id, addresser_id=user_id, text="Your membership-deadline is update to " + subscription.strftime('%d/%m/%Y'))


# ________________________________________ TRAINER ________________________________________ 


# - Given the email,         returns the Trainer who has got that email if exixsts
# - Given the id,            returns the Trainer who has got that id if exists
# - If all flag is set True, returns all Trainers
# Otherwise returns None
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
# Returns True if it was added correctly, False otherwise
# PN! Trainer is added both in Trainer table as in UserRole table
def add_trainer(session, fullname=None, email=None, pwd=None, telephone=None, address=None, user=None):
    if user is not None:
        if get_user(session, email=user.email) is None:
            # a) Neither a User nor a Trainer
            add_user(session,user=user)
            session.flush()
            session.add(Trainer(id=user.id))
            add_user_role(session, user=user, role=get_role(session, name='Trainer'))
            return True
        elif get_trainer(session, email=user.email) is None:
            # b) User yet, but not a Trainer
            session.add(Trainer(id=user.id))
            add_user_role(session, user=user, role=get_role(session, name='Trainer'))
            return True
        else:  
            # c) Both a User and a Trainer
            return False
    elif fullname is not None and\
         email    is not None and\
         pwd      is not None: 
        return add_trainer(session, user=User(fullname=fullname, email=email, pwd=pwd, telephone=telephone, address=address, covid_state=0, subscription=datetime.date.today()+timedelta(days=365)))
    else:
        return False

    
# Adds all Trainers from the user_list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_trainer_from_list(session, user_list):
    b = True
    for us in user_list:
        b &= add_trainer(session, user=us)
    return b


# ________________________________________ ROLE ________________________________________ 


# - Given the name,          returns the Role who has got that name if exixsts
# - Given the id,            returns the Role who has got that id if exists
# - If all flag is set True, returns all Roles
# Otherwise returns None
def get_role(session, id=None, name=None, all=False):
    if id is not None:
        return session.query(Role).filter(Role.id == id).one_or_none()
    elif name is not None:
        return session.query(Role).filter(Role.name == name).one_or_none()
    elif all is True:
        return session.query(Role).all()
    else:
        return None


# - Given a Role adds it to the database
# - Given the name of a a Role adds it to the databases
# Returns True if it was added correctly, False otherwise
def add_role(session, name=None, role=None):
    if role is not None:
        exist = get_role(session, name=role.name)
        if exist is not None:
            return False
        else:
            session.add(role)
            return True
    elif name is not None:
        return add_role(session, role=Role(name=name))
    else:
        return False

    
# Adds all Roles from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_role_from_list(session, role_list):
    b = True
    for role in role_list:
        b &= add_role(session, role=role)
    return b


# ________________________________________ USER-ROLES ________________________________________


# - Given a user_id and a role_id returns the correponding UserRole if exists
# - If all flag is set True, returns all UserRole
# Returns None otherwise
def get_user_role(session, user_id=None, role_id=None):
    if user_id is not None and role_id is not None:
        return session.query(UserRole).filter(UserRole.user_id == user_id, UserRole.role_id == role_id).one_or_none()
    elif user_id is not None:
        return session.query(UserRole).filter(UserRole.user_id == user_id).all()
    else:
        return None   

# - Given a User and a Role adds the corresponding User-Roles to the Database
# - Given a Roles adds it to the Database
# Returns True if it was added correctly
# Raises an Exception if
# - The User already had that Role (BaseException, violated p_key contraint)
def add_user_role(session, user=None, role=None):

    if user is not None and role is not None:
        session.add(UserRole(user_id=user.id, role_id=role.id))
        return True

# Deletes the UserRole form the given User and Role
# Raises an Error if the User doesn't have the Role
def delete_user_role(session, user_id=None, role_id=None):
    role = get_role(session, id=role_id)
    user = get_user(session, id=user_id)
    if role in user.roles:
        user_role = get_user_role(session, user_id=user_id, role_id=role_id)
        session.delete(user_role)
    else:
        raise BaseException("Cannot revoke role: User " + user.fullname + " doesn't have " + role.name + " role")


# Returns Admin's id
def get_admin_id(session):
    return get_user(session, email="admin@gmail.com").id


# Assigns Trainer-Role to the user with the given user_id
# Notifies the user with a Message
def assign_trainer_role(session, user_id=None):
    if user_id is not None:
        user = get_user(session, id=user_id)
        add_trainer(session, user=user)
        admin_id = get_admin_id(session)
        add_message(session, sender_id=admin_id, addresser_id=user_id, text="You're a Trainer now! You can create your own course")


# Revokes Trainer-Role from the user with the given user_id
# Delete all his Courses (and CoursePrograms and CourseSignsUp ON CASCADE)
# PN! The role is revoked both from UserRoles and Trainer table
def revoke_trainer_role(session, user_id=None):
    if user_id is not None:
        trainer_role = get_role(session, name="Trainer")
        trainer = get_trainer(session, id=user_id)
        for course in  trainer.courses: # could be also done from ON DELETE CASCADE, but we need to notify users
            delete_course(session, course_id=course.id)
        session.delete(trainer)
        delete_user_role(session, user_id=user_id, role_id=trainer_role.id)
        admin_id = get_admin_id(session)
        add_message(session, sender_id=admin_id, addresser_id=user_id, text="You're Trainer role has been revoked. All your Courses have been deleted")



# ________________________________________ SHIFT ________________________________________ 


# - Given a combination of date, starting hour, course_id and room_id returns the corresponding Shift or Shifts
# - Given a prenotation returns the corresponding Shift
# - If all flag is set True, returns all Shifts
# Otherwise returns None
#TODO eliminare casi inutili e magari suddividere in più funzioni
def get_shift(session, date=None, start=None, prenotation=None, id=None, course_id=None, room_id=None, all=False):

    # Four parameters
    if date is not None and start is not None and room_id is not None and course_id is not None:
        return session.query(Shift).filter(Shift.date == date, Shift.starting == start, Shift.room_id == room_id, Shift.course_id == course_id).one_or_none()
    
    # Three parameters
    elif start is not None and date is not None and course_id is not None:
        return session.query(Shift).filter(Shift.starting == start, Shift.date == date, Shift.course_id == Shift.course_id).one_or_none()
    elif start is not None and date is not None and room_id is not None:
        return session.query(Shift).filter(Shift.starting == start, Shift.date == date, Shift.room_id == room_id).one_or_none()
    elif start is not None and room_id is not None and course_id is not None:
        return session.query(Shift).filter(Shift.starting == start, Shift.room_id == room_id, Shift.course_id == Shift.course_id).all()
    elif room_id is not None and date is not None and course_id is not None:
        return session.query(Shift).filter(Shift.room_id == room_id, Shift.date == date, Shift.course_id == Shift.course_id).all()
    
    # Two parameters
    elif start is not None and date is not None:
        return session.query(Shift).filter(Shift.starting == start, Shift.date == date).all()
    elif start is not None and course_id is not None:
        return session.query(Shift).filter(Shift.starting == start, Shift.course_id == course_id).all()
    elif start is not None and room_id is not None:
        return session.query(Shift).filter(Shift.starting == start, Shift.room_id == room_id).all()
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

# Generates a list of all shifts for the fibem date and room_id
def generate_room_daily_shifts(session, date=None, room_id=None):
    if date is not None and room_id is not None:

        day_name = calendar.day_name[date.weekday()]
        weeksetting = get_week_setting(session, day_name)
        hour_start = weeksetting.starting
        hour_end = weeksetting.ending
        shift_length = weeksetting.length
        room = get_room(session, id=room_id)
        
        l = []
        start =     timedelta(hours=hour_start.hour,   minutes=hour_start.minute)
        length =    timedelta(hours=shift_length.hour, minutes=shift_length.minute)
        end_ =      timedelta(hours=hour_end.hour,     minutes=hour_end.minute)
        end = start + length

        while(end <= end_):
            l.append(
                    Shift(
                        date=date,
                        starting = datetime.time(hour=start.seconds//3600, minute=(start.seconds//60)%60),
                        ending =   datetime.time(hour=end.seconds//3600, minute=(end.seconds//60)%60),
                        room_id = room.id,
                        course_id = None
                    )
                )
            start = end
            end = start + length

        return l


# - Given the starting date and the number of days and the room  generate the shifts for all days in time-interval
# - Given the starting date and the ending date and the room     generate the shifts for all days in time-interval
# If there were previous plans which are changed, the previous shifts are removed
# If a Shift is removed, noififies User who made a Prenotations for that shift (removed ON CASCADE) wiht a message
def plan_shifts(session, starting=None, n=1, ending=None, room_id=None, all_room=False):
    if starting is not None and room_id is not None:
        day = starting + timedelta(days=0)
        room = get_room(session, id=room_id)
        if ending is None:
            ending = day + timedelta(days=n)
        while(day <= ending):
            day_name = calendar.day_name[day.weekday()]
            ws = get_week_setting(session, day_name=day_name)
            if ws is not None and (ws.changed or room.new):
                shifts = get_shift(session, date=day, room_id=room_id)
                for shift in shifts:
                    prenotations = shift.prenotations
                    admin_id = get_user(session, email="admin@gmail.com").id
                    for pr in prenotations:
                        add_message(session, sender_id=admin_id, addresser_id=pr.user_id,
                        text = "Your prenotation on " + pr.shift.date.strftime('%d/%m/%Y') +\
                            " in " + pr.shift.room.name +  " from " + pr.shift.starting.strftime('%H:%M') +\
                            " to " + pr.shift.ending.strftime('%H:%M') + " has been deleted due to the replan of week setting")
                    session.delete(shift)
                l = generate_room_daily_shifts(session, datetime.date(year=day.year, month=day.month, day=day.day), room_id=room_id)
                add_shift_from_list(session, l)
            day = day + timedelta(days=1)

        wss = get_week_setting(session, all=True)
        for ws in wss:
            ws.changed = False
        room.new = False
    elif starting is not None and all_room is True:
        for room in get_room(session, all=True):
            plan_shifts(session, starting=starting, n=n, ending=ending, room_id=room.id)


# - Given a Shift adds it to the database
# - Given a date, starting and ending hour, the room's id and course's id of a Shift adds it to the database
# Returns True if it was added correctly, False otherwise
def add_shift(session, date=None, start=None, end=None, room_id=None, course_id=None, shift=None):
    if shift is not None:
        exist = get_shift(session, date=shift.date, start=shift.starting, room_id=shift.room_id)
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
        return add_shift(session, shift=Shift(date=date, starting=start, ending=end, room_id=room_id, course_id=course_id))
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


# - Given a user_id and a shift_id returns the correponding Prenotation if exists
# - Given a user_id                returns all his prenotations
# - Given a shift_id               returns all prenotations for that Shift
# - Given a date                   returns all prenotations for that day
# - If all flag is set True,       returns all Prenotations
# Returns None otherwise
def get_prenotation(session, user_id=None, shift_id=None, date=None, all=False):
    if user_id is not None and shift_id is not None:
        return session.query(Prenotation).filter(Prenotation.user_id == user_id, Prenotation.shift_id == shift_id).one_or_none()
    elif user_id is not None:
         return session.query(Prenotation).filter(Prenotation.user_id == user_id).all()
    elif shift_id is not None:
        return session.query(Prenotation.user_id).filter(Prenotation.shift_id == shift_id).all()
    elif date is not None:
        return session.query(Prenotation).join(Shift).filter(Shift.date == date).all()
    elif all is True:
        return session.query(Prenotation).all()
    else:
        return None   

# - Given a User and a Shift adds the corresponding Prenotation to the Database
# - Given a Prenotation adds it to the Database
# Returns True if it was added correctly, False otherwise
# Raises an Exception if
# - shift is occupied by a course (trigger)
# - maximum capacity has already been reached (trigger)
# - prenotation overlaps with an other one (trigger)
# - User is already in that turn (BaseException, violated p_key contraint)
# - User has reached week-limit hours (app)
# - User has an unsafe covid-state (trigger)
# - User subscription has expired (trigger)
def add_prenotation(session, user=None, shift=None, prenotation=None):

    # Returns the number of own-training-week-prenotations for the  given the user and a date
    def get_count_weekly_prenotations(session, user, date):
        # Move to monday
        day = date + timedelta(days=0)
        while(calendar.day_name[day.weekday()] != 'Monday'):
            day = day - timedelta(days=1)
        count = 0
        for i in range(7):
            shifts = get_shift(session, date=day)
            for sh in shifts:
                users = sh.users_prenoted
                if user in users:
                    count += 1
            day = day + timedelta(days=1)
        
        return count

    if user is not None and shift is not None:
        max_ = get_global_setting(session, name='MaxWeeklyEntry').value
        count = get_count_weekly_prenotations(session, user, shift.date)
        if (count < max_):
            if "Admin" not in user.roles:
                session.add(Prenotation(user_id=user.id, shift_id=shift.id))
                return True
            else:
                raise BaseException("Admin can't book")
        else:
            raise BaseException("Week prenotation peak reached")
    elif prenotation is not None:
        user_  = get_user(session, id=prenotation.user_id)
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

# Deletes the prenotation given the Shift, the User or both
def delete_prenotation(session, shift=None, user=None):
    if shift is not None and user is not None:
        p = get_prenotation(session, user_id = user.id, shift_id = shift.id)
        session.delete(p)
        return True
    elif shift is not None:
        p = get_prenotation(session, shift_id=shift.id)
        session.delete(p)
        return True
    elif user is not None:
        p = get_prenotation(session, user_id = user.id)
        session.delete(p)
        return True
    else:
        return False


# ________________________________________ ROOM ________________________________________


# - Given the id,            returns the Room who has got that id if exixsts
# - Given the name,          returns the Room who has got that name if exists
# - If all flag is set True, returns all Rooms
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
# Returns True if it was added correctly, False otherwise
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
        return add_room(session, room=Room(name=name, max_capacity=max_capacity, new=True))
    else:
        return False
    

# Adds all Rooms from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_room_from_list(session, rooms_list):
    b = True
    for room in rooms_list:
        b &= add_room(session, room=room)
    return b


# Updates Room Max Capacity with the given parameters
# Return True if the changes are done, False otherwise
# Raises an Exception if the name is not valid
# PN! If capacity decreases, it's possible to delete prenotations in excess. If so, Users are notified with a Message
def update_room_max_capacity(session, name=None, mc=None):
    if name is not None and mc is not None:
        exixst = get_room(session, name=name)
        if exixst is not None:
            first = exixst.max_capacity
            session.query(Room).filter(Room.name == name).update({Room.max_capacity:mc}, synchronize_session = False)
            # It is possible to remove some prenotation because the capacity has decreased
            if first > mc:
                room = exixst
                shifts = get_shift(session, room_id=room.id)
                for shift in shifts:
                    prenotations = shift.prenotations
                    num = len(prenotations)
                    if num > mc:
                        to_remove = num-mc
                        admin_id = get_admin_id(session)
                        for i in range(to_remove):
                            pr = prenotations[num-1-i]
                            add_message(session, sender_id=admin_id, addresser_id=pr.user_id,
                                text= "Your prenotation on " + shift.date.strftime('%d/%m/%Y') + " in " + shift.room.name +\
                                      " from " + shift.starting.strftime('%H:%M') + " to " + shift.ending.strftime('%H:%M') +\
                                      " has been deleted due to the decrease of room capacity from " + str(first) + " to " + str(mc))
                            session.delete(pr)
            return True
        else:
            raise BaseException("Room " + name + " doesn't exists")
    else:
        return False


# Deletes the Room with the given room_id
# PN! Delete also all Shifts and Prenotations and CoursePrograms for that Room (ON CASCADE)
# Notifies all Users that had a Course or a Prenotation in that Room with a Message
def delete_room(session, room_id=None):
    if room_id is not None:
        room = get_room(session, id=room_id)
        # Notifies for courses
        courses = get_course(session, all=True)
        to_notify = []
        for course in courses:
            course_programs = course.course_programs
            for course_program in course_programs:
                if room_id == course_program.room_id:
                    to_notify.append(course.id)
        admin_id = get_admin_id(session)
        for course_id in to_notify:
            course = get_course(session, id=course_id)
            for user in course.users:
                add_message(session, sender_id=admin_id, addresser_id=user.id,
                            text=room.name + " has been deleted: your " + course.name + " program could have changed, please check on course's page")
            add_message(session, sender_id=admin_id, addresser_id=course.instructor_id,
                        text=room.name + " has been deleted: please redefine " + course.name + " program")
        # Notifies for prenotations
        shifts = get_shift(session, room_id=room_id)
        for shift in shifts:
            prenotations = shift.prenotations
            for pr in prenotations:
                add_message(session, sender_id=admin_id, addresser_id=pr.user_id,
                            text="Your prenotation on " + shift.date.strftime('%d/%m/%Y') + " in " + shift.room.name +\
                                 " from " + shift.starting.strftime('%H:%M') + " to " + shift.ending.strftime('%H:%M') +\
                                 " has been deleted due to the deletion of " + room.name)
        session.delete(room) # deletes on cascade shifts, prenotations and course_programs


# ________________________________________ GLOBAL SETTING ________________________________________


# Returns the GlobalSetting with the corresponding name
# If all flag is set True, returns all GlobalSettings
def get_global_setting(session, name=None, all=False):
    if name is not None:
        ret = session.query(GlobalSetting).filter(GlobalSetting.name == name).one_or_none()
        return ret
    elif all is True:
        return session.query(GlobalSetting).all()
    else:
        return None


# - Given a GlobalSetting add it to the Database
# - Given GlobalSetting's name and value add it to the Database
# Returns True if it was added correctly, False otherwise
def add_global_setting(session, name=None, value=None, global_setting=None):
    if global_setting is not None:
        exists = get_global_setting(session, name=global_setting.name)
        if exists is not None:
            return False
        else:
            session.add(global_setting)
            return True
    elif name  is not None and\
         value is not None:
        add_global_setting(session, global_setting=GlobalSetting(name=name, value=value))
    else:
        return False


# Adds all GlobalSetting from the list given to the Database
# Returns True if all elements were added, False otherwise
def add_global_setting_from_list(session, global_setting_list):
    b = True
    for global_setting in global_setting_list:
        b &= add_global_setting(session, global_setting=global_setting)
    return b


# Updates the GlobalSetting name with the given parameters
# Raises an exception if the name is not valid
def update_global_setting(session, name=None, value=None):
    if name is not None and value is not None:
        gs = get_global_setting(session, name=name) # raise an exeption if doesn't exixsts
        gs.value = value


# ________________________________________ WEEK SETTING ________________________________________


# Returns the WeekSetting with the corresponding day_name
# Returns None if the day_name is not valid
# If all flag is set True, returns all WeekSettings
def get_week_setting(session, day_name=None, all=False):
    if day_name is not None:
        return session.query(WeekSetting).filter(WeekSetting.day_name == day_name).one_or_none()
    elif all is True:
        return session.query(WeekSetting).all()
    else:
        return None

# - Given a WeekSetting add it to the Database
# - Given WeekSetting's day_name, starting, ending and length  add it to the Database
# Returns True if it was added correctly, False otherwise
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


# Adds all WeekSetting from the list given to the Database
# Returns True if all elements were added, False otherwise
def add_week_setting_from_list(session, week_setting_list):
    b = True
    for week_setting in week_setting_list:
        b &= add_week_setting(session, week_setting=week_setting)
    return b


# Updates the WeekSetting with the given parameters
# If at least one parameter is updated, changed flag is set True 
# PN! Values are clamped between GlobalSetting's values
def update_weekend_setting(session, day_name=None, starting=None, ending=None, length=None):

    if day_name is not None:
        any_change = False
        ws = get_week_setting(session, day_name=day_name)

        if starting is not None:
            h_start = get_global_setting(session, name="HourOpening").value
            if starting.hour < h_start:
                starting = datetime.time(hour=h_start)
            ws.starting = starting
            any_change = True

        if ending is not None:
            h_end = get_global_setting(session, name="HourClosing").value
            if ending.hour > h_end:
                ending = datetime.time(hour=h_end)
            ws.ending = ending
            any_change = True
            
        if length is not None:
            min_len = get_global_setting(session, name='MinimumShiftLength').value
            max_len = get_global_setting(session, name='MaximumShiftLength').value
            length_minutes = clamp(length.minute + length.hour * 60, min_len, max_len)
            length_hour = int(length_minutes / 60)
            length_minutes =  int(length_minutes % 60)
            length = datetime.time(hour = length_hour, minute=length_minutes)
            ws.length = length
            any_change = True

        if any_change is True:
            ws.changed=True


# ________________________________________ COURSE ________________________________________

# - Given the id,            returns the Course who has got that id if exixsts
# - Given the name,          returns the Course who has got that name if exists
# - If all flag is set True, returns all Courses
# Otherwise returns None
def get_course(session, id=None, name=None, all=False):
    if id is not None:
        return session.query(Course).filter(Course.id == id).one_or_none()
    elif name is not None:
        return session.query(Course).filter(Course.name == name).one_or_none()
    elif all is True:
        return session.query(Course).all()
    else:
        return None    
        

# - Given a Course adds it to the database
# - Given name, starting and ending date, max_partecipants and the instructor_id of a Course adds it to the database
# Returns True if it was added correctly, False otherwise
def add_course(session, name=None, starting=None, ending=None, max_partecipants=None, instructor_id=None, course=None):
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
        return add_course(session, course=Course(name=name, starting=starting, ending=ending, max_partecipants=max_partecipants, instructor_id=instructor_id))
    else:
        return False
    

# Adds all Courses from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_course_from_list(session, courses_list):
    b = True
    for course in courses_list:
        b &= add_course(session, course=course)
    return b


# Given the name of the Course plan his Shifts
# It raises an exception if:
# - there's no course with that name
# - the course has no course program
# - there's no turn in that day
# - the course overlaps with any other 
# PN! When a course is set for a Shift, all Prenotation for that Shift are removed and User is notified with a Message
def plan_course(session, name):
 
    
    course = get_course(session, name=name)
    if course is None:
        raise BaseException("Course " + name + " does not exixsts")
    course_programs = get_course_program(session, course_id=course.id)
    if course_programs is None:
        raise BaseException("Course " + name + " is planned with no course program")
    end = course.ending + timedelta(days=0)
    for prog in course_programs:
        dayname = prog.week_day
        turn = prog.turn_number
        room_id = prog.room_id
        day = course.starting + timedelta(days=0)
        while(calendar.day_name[day.weekday()] != dayname): # Move to the correct week day
            day = day + timedelta(days = 1)
        while(day < end):
            ws = get_week_setting(session, day_name=calendar.day_name[day.weekday()])
            starting = time_to_timedelta(ws.starting) + time_to_timedelta(ws.length) * (turn-1)
            shift = get_shift(session, date=day, start=starting, room_id=room_id)
            if shift is None:
                add_shift(
                    session,
                    date=day,
                    start=starting,
                    end=starting+time_to_timedelta(ws.length),
                    room_id=room_id,
                    course_id=course.id
                )
            elif (shift.course_id is not None):
                raise BaseException("Course cannot be planned: it overlaps with an other course!")
            else:
                # Deletes all Prenotation in that Shift
                prenotations = session.query(Prenotation).where(Prenotation.shift_id==shift.id)
                admin_id = get_admin_id(session)
                for prenotation in prenotations:
                    add_message(session, sender_id=admin_id, addresser_id=prenotation.user_id,
                    text='Your prenotation on ' + prenotation.shift.date.strftime('%d/%m/%Y') + " from " + shift.starting.strftime('%H:%M') + " to " + shift.ending.strftime('%H:%M') + " in " + prenotation.shift.room.name + " has been deleted due to the planning of " + course.name + " by the trainer " + course.trainer.user.fullname
                    )
                    session.delete(prenotation)
                shift.course_id = course.id
            day = day + timedelta(days=7)


# Deletes the course with the given course_id
# Notifies Users who signed-up with a Message
# PN! Deletes also CoursePrograms and CourseSignsUp (ON CASCADE)
def delete_course(session, course_id=None):
    if course_id is not None:
        c = get_course(session, id=course_id)
        users = c.users
        admin_id = get_admin_id(session)
        for user in users:
            add_message(session, sender_id=admin_id, addresser_id=user.id,
                        text= "The course " + c.name + " you signed-up has been deleted")
        session.delete(c)
 

# Update name and max_partecipants Course
def update_course(session, course_id=None, name=None, max_partecipants=None):
    if course_id is not None:
        course = get_course(session, id=course_id)
        if name != course.name:
            course.name = name
        if max_partecipants != course.max_partecipants:
            course.max_partecipants = max_partecipants


# ________________________________________ COURSE PROGRAM ________________________________________


# - Given the id,              returns the CourseProgram who has got that id if exixsts
# - Given the course_id,       returns all his CoursePrograms
# - If all flag is set True,   returns all CoursePrograms
# Otherwise returns None
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
# Returns True if it was added correctly, False otherwise
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
        add_course_program(session, course_program=CourseProgram(week_day=week_day, turn_number=turn_number, room_id=room_id, course_id=course_id))
    else:
        return False
    

# Adds all CoursePrograms from the list given to the Database
# Returns True if all elements were added, False if at least one was already contained
def add_course_program_from_list(session, course_programs_list):
    b = True
    for course_program in course_programs_list:
        b &= add_course_program(session, course_program=course_program)
    return b

# Deletes the CourseProgram with the given course_program_id
def delete_course_program(session, cp_id=None):
    cp = get_course_program(session, id=cp_id)
    session.delete(cp)


# ________________________________________ COURSE SIGN UP ________________________________________


# - Given a UserID           returns all his course signs up
# - Given a CourseId         returns all his course signs up
# - If all flag is set True, returns all CourseSignsUp
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
#  - the trainer sign-up for his own course (trigger)
#  - the user has already SignedUp for the course (BaseException, violated p_key contraint)
#  - the capacity peak has already been reached (trigger)
# Notifies both User and Trainer with a Message
def add_course_sign_up(session, user=None, course=None, course_sign_up=None):
    if user is not None and course is not None:
        if "Admin" not in user.roles:
            session.add(CourseSignUp(user_id=user.id, course_id=course.id))
            add_message(session, sender_id=user.id, addresser_id=course.trainer.user.id, text="Hello! I've just Signed-Up for your " + course.name + "course ! ")
            add_message(session, addresser_id=user.id, sender_id=course.trainer.user.id, text="Hello! Welcome to my " + course.name + " course! ")
        else:
            raise BaseException("Admin can't signup for a course")
    elif course_sign_up is not None:
        user_  =  get_user(session, id=course_sign_up.user_id)
        course_ = get_shift(session, id=course_sign_up.user_id)
        return add_course_sign_up(session, user=user_, course=course_)
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


# Deletes course sign up of the given user or course
def delete_course_sign_up(session, course=None, user=None):
    if course is not None and user is not None:
        cs = get_course_sign_up(session, user_id = user.id, course_id = course.id)
        session.delete(cs)
    elif course is not None:
        css = get_course_sign_up(session, course_id=course.id)
        for cs in css:
            session.delete(cs)
    elif user is not None:
        css = get_course_sign_up(session, user_id=user.id)
        for cs in css:
            session.delete(cs)


# ________________________________________ MESSAGES ________________________________________


# - Given a UserID both of the sender and the addresser returns all his Messages if the user is the same
# - Given a UserID of the sender returns all his Messages
# - Given a UserID of the addresser returns all his Messages
# - If all flag is set True, returns all Messages
# Returns None otherwise
def get_message(session, id=None, sender=None, addresser=None, all=False):
    if id is not None:
        return session.query(Message).filter(Message.id == id).one_or_none()
    if sender is not None and addresser is not None:
        if sender == addresser:
            return session.query(Message).filter(Message.sender == sender).union.\
                    session.query(Message).filter(Message.addressee == addresser).all()
        else:
            return None
    elif sender is not None:
        return session.query(Message).filter(Message.sender == sender).all()
    elif addresser is not None:
        return session.query(Message).filter(Message.addressee == addresser).all()
    elif all is True:
        return session.query(Message).all()
    else:
        return None


# - Given a Message adds it to the database
# - Given the sender_id, the addresser_id and the text of a Message adds it to the database
# Returns True if it was added correctly, False otherwise
# Raises an error if
#  - the sender and the addresser are the same User (check)
def add_message(session, sender_id=None, addresser_id=None, text=None, message=None):

    if message is not None:
        session.add(message)
        return True
    if sender_id    is not None and\
       addresser_id is not None and\
       text         is not None:
        mess = Message(sender=sender_id, addressee=addresser_id, text=text, date=datetime.datetime.now(), read=False)
        add_message(session, message=mess)
    else:
        return False


# Adds all Messages from the list given to the Database
# Returns True if all elements were added,
# False if at least one was already contained
def add_messagge_from_list(session, message_list):
    b = True
    for message in message_list:
        b &= add_message(session, message=message)
    return b


# - Given the message_id deletes the corresponding message
def del_message(session, id=None):
    if id is not None:
        mess = get_message(session, id=id)
        session.delete(mess)


# - Given a list of messages update read field as True where is False
def mark_read(session, messages=None):
    if messages is not None:
        for message in messages:
            if message.read is False:
                message.read = True


# Given the user_id who did the report
# - mark is covid_state as positive
# - mark covid_state of users he had contacts
# Sends a message to:
# - all users who had a shift in common in the two previous week
# - all users who have a course in common (and also to the trainer)
def user_covid_report(session, user_id):

    user = get_user(session, id=user_id)
    admin_id = get_admin_id(session)
    update_user(session, user_id=user_id, covid_state=2)
    add_message(session, sender_id=admin_id, addresser_id=user_id,
                    text= "You signaled you're positive to Covid19. For any problem please contact Gym's admin. Get well soon! "
                )

    today = datetime.date.today()

    # Shift
    prev = today - timedelta(days=14)
    shifts = user.shifts
    shifts = filter(lambda sh: prev <= sh.date <= today, shifts) # Remove the shifts that are not in the previous two weeks
    for shift in shifts:
        users = shift.users_prenoted
        for us in users:
            if us.id != user.id:
                update_user(session, user_id=us.id, covid_state=1)
                add_message(
                    session,
                    sender_id=admin_id,
                    addresser_id=us.id,
                    text= "On " + shift.date.strftime('%d/%m/%Y') +
                           " from " + shift.starting.strftime('%H:%M') + " to " + shift.ending.strftime('%H:%M') +\
                           " in " + shift.room.name + " you came into contacts with a person affected from COVID19"
                )
    # Course
    courses = user.courses
    for course in courses:
        course_signs_up = get_course_sign_up(session, course_id=course.id)
        for csu in course_signs_up:
            if csu.user_id != user.id:
                update_user(session, user_id=csu.user_id, covid_state=1)
                add_message(
                    session,
                    sender_id=admin_id,
                    addresser_id=csu.user_id,
                    text= "One person in course " + course.name + " you signed-up for is affected from COVID19"
                )
        update_user(session, user_id=course.instructor_id, covid_state=1)
        add_message(
                    session,
                    sender_id=admin_id,
                    addresser_id= course.instructor_id,
                    text= "One person in your course " + course.name + " is affected from COVID19"
        )
    # Trainer
    if(get_role(session, name="Trainer")) in user.roles:
        trainer = get_trainer(session, email=user.email)
        for course in trainer.courses:
            course_signs_up = get_course_sign_up(session, course_id=course.id)
            for csu in course_signs_up:
                update_user(session, user_id=csu.user_id, covid_state=1)
                add_message(
                    session,
                    sender_id=admin_id,
                    addresser_id=csu.user_id,
                    text= "One person in course " + course.name + " you signed-up for is affected from COVID19"
                )