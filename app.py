from typing import final
from flask import *
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

from model import *


app = Flask ( __name__ )

#engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
# engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)
#engine = create_engine('postgresql://postgres:gemellirosa@localhost:5432/Gym', echo=True)

app.config ['SECRET_KEY'] = 'ubersecret'

Session = sessionmaker(bind=engine, autoflush=True)

login_manager = LoginManager()
login_manager.init_app(app)

#__________________________________________ SESSION-USER ________________________________________


class SessionUser(UserMixin):
    # costruttore di classe
    def __init__(self, id, email, pwd, roles, active=True):
        self.id = id
        self.email = email
        self.pwd = pwd
        self.roles = roles
        self.active = active

def get_SessionUser_by_email(session, email):
    user = get_user(session, email = email)
    if user is not None:
        roles = [role.name for role in user.roles]
        return SessionUser(id=user.id, email=user.email, pwd=user.pwd, roles=roles)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    try:
        user = get_user(session, id = user_id)
        if user is not None:
            roles = [role.name for role in user.roles]
            session.commit()
            return SessionUser(id=user.id, email=user.email, pwd=user.pwd, roles=roles)
    except:
        session.rollback()
        raise
    finally:
        session.close()

def is_admin(us):
    return us.is_authenticated and "Admin" in us.roles

def is_trainer(us):
    return us.is_authenticated and "Trainer" in us.roles


#__________________________________________ LOGIN ________________________________________


@app.route('/login')
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('private'))
        return render_template("login.html")
    except BaseException as exc:
        flash(str(exc), category='error')
        return redirect(url_for('login'))


@app.route('/login_form', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        session = Session()
        try:
            userReq = request.form['user']
            passReq = request.form['pass']
            userIn = get_user(session, email = userReq)
            if(userIn is not None):
                if (passReq == userIn.pwd):
                    user = get_SessionUser_by_email(session, userReq)
                    login_user(user)
                    session.commit()
                    return redirect(url_for('login'))
                else:
                    flash("Incorrect username or password.", category='error')
                    session.commit()
                    return redirect(url_for('login'))
            else:
                flash("Incorrect username or password.", category='error')
                session.commit()
                return redirect(url_for('login'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('login'))
        finally:
            session.close()


#__________________________________________ SIGIN ________________________________________


@app.route('/signin')
def signin():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('private'))
        return render_template("signin.html")
    except BaseException as exc:
            flash(str(exc), category='error')
            if current_user.is_authenticated:
                return redirect(url_for('private'))
            return redirect(url_for('home'))

@app.route('/signin_form', methods=['GET', 'POST'])
def signin_form():
    if request.method == 'POST':
        session = Session()
        try:
            fullname = request.form['name']
            email = request.form['email']
            address = request.form['address']
            telephone = request.form['telephone']
            pwd1 = request.form['pwd1']
            pwd2 = request.form['pwd2']
            us = get_user(session, email=email)
            if fullname and email and address and telephone and pwd1 and pwd1 == pwd2 and us is None:
                flash("Signed in successfully.", category='success')
                add_user(session, fullname=fullname, email=email, address=address, telephone=telephone, pwd=pwd1)
                session.commit()
                return redirect(url_for('login'))
            if not fullname:
                flash("Please enter a fullname.", category='error')
            elif not email:
                flash("Please enter an email.", category='error')
            elif not telephone:
                flash("Please enter telephone", category='error')
            elif not address:
                flash("Please enter address", category='error')
            elif us is not None:
                flash("User already exist.", category='error')
            elif us is not None:
                flash("User already exist.", category='error')
            elif not pwd1:
                flash("Please enter a password.", category='error')
            else:    
                flash("Passwords do not match.", category='error')
            return redirect(url_for('signin'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('signin'))
        finally:
            session.close()


#__________________________________________ LOGOUT ________________________________________


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


#__________________________________________ HOME ________________________________________


@app.route('/')
def home():
    try:
        return render_template("home.html")
    except BaseException as exc:
            flash(str(exc), category='error')
            return redirect(url_for('home'))


# ________________________________________________________ PRIVATE ________________________________________________________


@app.route('/private')
@login_required
def private():

    session = Session()

    def new_messages():
        messages = get_message(session, addresser=current_user.id)
        new = False
        for message in messages:
            new |= (not message.read)
        return new

    try:
        user = get_user(session, email=current_user.email)
        resp = make_response(render_template("private.html", us = user, new_mess=new_messages()))
        session.commit()
        return resp
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/private/prenotations')
@login_required
def prenotations():
    session = Session() 
    try:
        user = get_user(session, email=current_user.email)
        shifts = filter(lambda sh: sh.date >= datetime.date.today(), user.shifts)
        past_shifts = filter(lambda sh: sh.date <= datetime.date.today() and datetime.datetime.now().time() >= sh.ending, user.shifts)
        return make_response(render_template("prenotations.html", shifts=shifts, past_shifts=past_shifts))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/private/courses_sign_up')
@login_required
def courses_sign_up():
    session = Session() 
    try:
        user = get_user(session, email=current_user.email)
        courses = user.courses
        return make_response(render_template("courses_sign_up.html", courses=courses, today=datetime.date.today()))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('courses_sign_up'))
    finally:
        session.close()


@app.route('/private/covid_report')
@login_required
def covid_report():
    session = Session() 
    try:
        user = get_user(session, id=current_user.id)
        user_covid_report(session, user_id=user.id)
        session.commit()
        return redirect(url_for('private'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/private/messages')
@login_required
def messages():
    session = Session() 
    try:
        messages = get_message(session, addresser=current_user.id)
        resp = make_response(render_template("messages.html", messages=reversed(messages)))
        mark_read(session, messages)
        session.commit()
        return resp
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('messages'))
    finally:
        session.close()


@app.route('/private/messages/del/<mess_id>', methods=['POST'])
@login_required
def delete_message(mess_id):
    if request.method == 'POST':
        session = Session()
        try:
            del_message(session, id=mess_id)
            session.commit()
            return redirect(url_for('messages'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('messages'))
        finally:
            session.close()


# ________________________________________________________ UPDATE USER ________________________________________________________


@app.route('/private/update_user')
@login_required
def upd_user():
    session = Session()
    try:
        user = get_user(session, id = current_user.id)
        return render_template("update_user.html", user = user)
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('upd_user'))
    finally:
        session.close()


@app.route('/private/update_user_form', methods=['POST'])
@login_required
def update_user_form():
    if request.method == 'POST':
        session = Session()
        try:
            user = get_user(session, email= current_user.email)
            fullname = request.form['fullname']
            if fullname == "":
                flash("Empty Field!", category='error')
                return redirect(url_for('upd_user'))
            telephone = request.form['telephone']
            if telephone == "":
                flash("Empty Field!", category='error')
                return redirect(url_for('upd_user'))
            address = request.form['address']
            if address == "":
                flash("Empty Field!", category='error')
                return redirect(url_for('upd_user'))
            pwd1 = request.form['pwd1']
            if pwd1 == "":
                flash("Empty Field!", category='error')
                return redirect(url_for('upd_user'))
            pwd2 = request.form['pwd2']
            if pwd1 == "":
                flash("Empty Field!", category='error')
                return redirect(url_for('upd_user'))

            if pwd1 != pwd2:
                flash("Password Mismatch!", category='error')
                return redirect(url_for('upd_user'))
                
            update_user(session, user_id = user.id, fullname = fullname, telephone = telephone, address = address, pwd = pwd1)
            session.commit()
            return redirect(url_for('upd_user'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('upd_user'))
        finally:
            session.close()


# ________________________________________________________ SHIFT, PRENOTATION ________________________________________________________

#@app.route('/shifts/<year>/<month>/<day>/<room>')
@app.route('/shifts')
def shifts():
    session = Session()
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        day = request.args.get('day')
        room = request.args.get('room')
        date = datetime.date(year=int(year), month=int(month), day=int(day))
        if date < datetime.date.today():
            date = datetime.date.today()
        date_string = date.strftime("%Y-%m-%d")
        r = get_room(session, all=True)
        if room == 'All':
            shifts = get_shift(session, date=date)
        else:
            room_id = get_room(session, name=room).id
            shifts = get_shift(session, date=date, room_id=room_id)
        shifts = filter(lambda sh: sh.course_id is None, shifts) # Remove the shifts occupied from a course
        if date == date.today():
            shifts = filter(lambda sh: sh.ending >= datetime.datetime.now().time(), shifts)
        resp = make_response(render_template("shifts.html", shifts=sorted(shifts, key=lambda x: (x.ending, x.room_id)), date_string=date_string, rooms=r, user=get_user(session, email=current_user.email)))
        session.commit()
        return resp
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('shifts_first'))
    finally:
        session.close()


@app.route('/shifts/shifts_first')
def shifts_first():
    curr = datetime.date.today()
    return redirect('/shifts?year=%s&month=%s&day=%s&room=All' % (curr.year, curr.month, curr.day))


@app.route('/shifts/load_date', methods=['GET', 'POST'])
def shifts_load_state():
    if request.method == 'POST':
        session = Session()
        try:
            date_str = request.form['date']
            room = request.form['room']
            date_str = date_str.replace('-', '/')
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
            session.commit()
            return redirect('/shifts?year=%s&month=%s&day=%s&room=%s' % (date.year, date.month, date.day, room))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('shifts_first'))
        finally:
            session.close()


@app.route('/prenotation/<shift>')
@login_required
def prenotation(shift):
    session = Session()
    try:
        if current_user.is_authenticated:
            us = get_user(session, id = current_user.id)
            s = get_shift(session, id = shift)
            add_prenotation(session, user = us, shift = s)
            session.commit()
            return redirect(url_for('prenotations'))
        return redirect(url_for('login'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        if current_user.is_authenticated:
            return redirect(url_for('shifts_first'))
        return redirect(url_for('login'))
    finally:
        session.close()
    

@app.route('/del_prenotation/<shift>')
@login_required
def del_prenotation(shift):
    session = Session()
    try:
        us = get_user(session,id = current_user.id)
        s = get_shift(session, id = shift)
        delete_prenotation(session, shift=s, user=us)
        session.commit()
        return redirect(url_for('prenotations'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('prenotations'))
    finally:
        session.close()

# ________________________________________________________COURSES________________________________________________________


@app.route('/courses')
def courses():
    session = Session()
    try:
        user = get_user(session, email=current_user.email)
        courses = get_course(session, all=True)
        if is_trainer(current_user):
            courses = filter(lambda course: course not in user.trainer.courses, courses)
        return render_template("courses.html", courses = courses, today= datetime.date.today())
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('courses'))
    finally:
        session.close()


@app.route('/courses/course/<course_name>')
def course(course_name):
    session = Session()
    try:
        c = get_course(session,name = course_name)
        cp = get_course_program(session,course_id = c.id)
        sh = []
        for i in cp:
            sh.append(get_shift(session, id=i.turn_number))
        if current_user.is_authenticated:
            u = get_user(session, id = current_user.id)
            cs = get_course_sign_up(session, user_id=u.id, course_id=c.id)
            return render_template("course.html", course = c, course_program = cp, shift = sh, course_sign_up = cs)
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('course'), course_name=course_name)
    finally:
        session.close()


@app.route('/courses/trainer_courses')
@login_required
def trainer_courses():
    session = Session()
    try:
        user = get_user(session, email=current_user.email)
        if is_trainer(current_user):
            courses = user.trainer.courses
            return render_template("trainer_courses.html", courses = courses, trainer = user.trainer, today= datetime.date.today())
        return redirect(url_for('courses'))
    except BaseException as exc:
        flash(str(exc), category='error')
        if is_trainer(current_user):
            ret = redirect(url_for('trainer_courses'))
        else:
            ret = redirect(url_for('trainer_courses'))
        session.rollback()
        session.close()
        return ret
    finally:
        session.close()


@app.route('/trainer_courses/<course_name>')
@login_required
def trainer_course(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            course_program = get_course_program(session, course_id = course.id)
            sh = []
            for i in course_program:
                sh.append(get_shift(session, id=i.turn_number))
            session.commit()
            return render_template("trainer_course.html", course = course, course_program = course_program, shifts = sh)
        else:
            return redirect(url_for('courses'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('trainer_course'), course_name=course_name)
    finally:
        session.close()


@app.route('/courses/delete_course/<course_name>')
@login_required
def del_course(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            delete_course(session, course_id = course.id)
            session.commit()
            return redirect(url_for('trainer_courses'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('trainer_course'), course_name=course_name)
    finally:
        session.close()

@app.route('/courses/new_course')
@login_required
def new_course():
    session = Session()
    try:
        if is_trainer(current_user):
            r = get_room(session, all=True)
            return render_template('add_course.html', rooms=r)
        return redirect(url_for('courses'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        if is_trainer(current_user):
            return redirect(url_for('new_course'))
        return redirect(url_for('courses'))
    finally:
        session.close()

@app.route('/courses/new_course_form', methods=['GET', 'POST'])
@login_required
def new_course_form():
    if request.method == 'POST':
        session = Session()
        try:
            name = request.form['name']
            starting = request.form['starting']
            ending = request.form['ending']
            max_partecipants = request.form['max_partecipants']
            instructor_id = current_user.id
            add_course(session, name=name, starting=starting, ending=ending, max_partecipants=max_partecipants, instructor_id=instructor_id)
            session.commit()
            return redirect(url_for('new_program', course_name = name))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('new_course'))
        finally:
            session.close()

@app.route('/courses/new_course/new_program/<course_name>')
@login_required
def new_program(course_name):
    session = Session()
    try:
        rooms = get_room(session, all=True)
        r = {}
        for room in rooms:
            r[room.id] = room.name
        return render_template('new_program.html', course = get_course(session, name=course_name), room_dict = r)
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('new_program', course_name=course_name))
    finally:
        session.close()

@app.route('/courses/undo_course/<course_name>')
@login_required
def undo_course(course_name):
    session = Session()
    try:
        c = get_course(session, name=course_name)
        starting = c.starting
        ending = c.ending
        max_partecipants = c.max_partecipants
        delete_course(session, course_id=c.id)
        session.commit()
        return render_template('add_course.html', rooms=get_room(session, all=True), course_name=course_name, starting=starting, ending=ending, max_partecipants=max_partecipants)
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('new_program'))
    finally:
        session.close()

@app.route('/courses/new_course/add_program/<course_name>')
@login_required
def add_program(course_name):
    session = Session()
    try:
        r = get_room(session, all=True)
        return render_template('add_program.html', rooms = r, course = get_course(session, name=course_name), week_setting = get_week_setting(session, all=True))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('new_program'))
    finally:
        session.close()

@app.route('/courses/new_course/add_program_form/<course_name>', methods=['POST', 'GET'])
@login_required
def add_program_form(course_name):

    def to_second(t):
        return (t.hour * 60 + t.minute) * 60 + t.second

    if request.method == 'POST':
        session = Session()
        try:
            room = request.form['room']
            r = get_room(session, name = room)
            day = request.form['day']
            c = get_course(session, name = course_name)
            course_id = c.id
            tn = request.form['turn_number']
            ws = get_week_setting(session, day_name=day)
            tn = clamp(int(tn), 1, (to_second(ws.ending) - to_second(ws.starting) ) / to_second(ws.length))
            add_course_program(session, week_day=day, turn_number=tn, room_id=r.id, course_id=course_id )
            session.commit()
            return redirect(url_for('new_program', course_name = course_name))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('add_program'))
        finally:
            session.close()

@app.route('/courses/new_course/del_program/<program_id>/<course_name>')
@login_required
def del_program(program_id, course_name):
    session = Session()
    try:
        delete_course_program(session, cp_id=int(program_id))
        session.commit()
        return redirect(url_for('new_program', course_name = course_name))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('new_program', course_name = course_name))
    finally:
        session.close()

@app.route('/courses/new_course/plan_course/<course_name>')
@login_required
def plan_course_(course_name):
    session = Session()
    try:
        plan_course(session, course_name)
        session.commit()
        return redirect(url_for('course', course_name=course_name))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('course', course_name = course_name))
    finally:
        session.close()
        

@app.route('/courses/sign_up/<course_name>')
@login_required
def sign_up(course_name):
    session = Session()
    try:
        if current_user.is_authenticated:
            us = get_user(session, id = current_user.id)
            c = get_course(session, name= course_name)
            add_course_sign_up(session, user=us, course=c)
            session.commit()
            return redirect(url_for('courses_sign_up'))
        return redirect(url_for('login'))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('course', course_name = course_name))
    finally:
        session.close()

@app.route('/courses/delete_sign_up/<course_name>')
@login_required
def delete_sign_up(course_name):
    session = Session()
    try:
        us = get_user(session,id = current_user.id)
        c = get_course(session, name = course_name)
        delete_course_sign_up(session,course = c, user = us)
        session.commit()
        return redirect(url_for('courses_sign_up'))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('course', course_name=course_name))
    finally:
        session.close()


# ________________________________________________________ADMIN SETTINGS________________________________________________________
@app.route('/admin/settings')
@login_required
def settings():
    try:
        if is_admin(current_user):
            return make_response(render_template("settings.html"))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
        if is_admin(current_user):
            return redirect(url_for("settings"))
        else:
            return redirect(url_for('private'))


@app.route('/admin/settings/global_settings')
@login_required
def global_settings():
    session = Session()
    try:
        if is_admin(current_user):
            global_settings = get_global_setting(session, all=True)
            global_settings = sorted(global_settings, key=lambda x: x.name)
            resp= make_response(render_template("update_global_settings.html", global_settings=global_settings))
            return resp
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        if is_admin(current_user):
            return redirect(url_for("global_settings"))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/admin/settings/global_settings_form', methods=['POST'])
@login_required
def global_settings_form():
    if request.method == 'POST':
        session = Session()
        try:
            global_settings = get_global_setting(session, all=True)
            for global_setting in global_settings:
                val = int(request.form[global_setting.name])
                if val != global_setting.value:
                    update_global_setting(session, name=global_setting.name, value=val)
            session.commit()
            return redirect(url_for('settings'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for("global_settings"))
        finally:
            session.close()


@app.route('/admin/settings/room_settings')
@login_required
def room_settings():
    session = Session()
    try:
        if is_admin(current_user):
            rooms = get_room(session, all=True)
            rooms = sorted(rooms, key=lambda x: x.id)
            resp= make_response(render_template("update_room_settings.html", rooms=rooms))
            return resp
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        if is_admin(current_user):
            return redirect(url_for('room_settings'))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/admin/settings/room_settings_form/<room_id>', methods=['POST'])
@login_required
def room_settings_form(room_id):
    if request.method == 'POST':
        session = Session()
        try:
            room = get_room(session, id=room_id)
            val = int(request.form[str(room_id)])
            if val != room.max_capacity:
                update_room_max_capacity(session, name=room.name, mc=val)
            session.commit()
            return redirect(url_for('room_settings'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for("room_settings"))
        finally:
            session.close()


@app.route('/admin/settings/room_settings/add_room')
@login_required
def add_room_():
    session = Session()
    try:
        if is_admin(current_user):
            return make_response(render_template("add_room.html"))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        if is_admin(current_user):
            return redirect(url_for("add_room_"))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()

@app.route('/admin/settings/room_settings/add_room_form', methods=['POST'])
@login_required
def add_room_form():
    if request.method == 'POST':
        session = Session()
        try:
            name = request.form['name']
            max_capacity = request.form['max_capacity']
            date_str = request.form['date']
            date_str = date_str.replace('-', '/')
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
            date = date.date()
            if date < datetime.date.today():
                raise BaseException("Could not plan shift in the past")
            add_room(session, name=name, max_capacity=max_capacity)
            session.flush()
            room = get_room(session, name=name)
            if room is not None:
                plan_shifts(session, starting=datetime.date.today(), ending=date, room_id=room.id)
            else:
                raise BaseException("non trovo stanza appena aggiunta")
            session.commit()
            return redirect(url_for('room_settings'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for("add_room_"))
        finally:
            session.close()

@app.route('/admin/settings/room_settings/delete_room/<room_id>', methods=['POST'])
@login_required
def del_room(room_id):
    if request.method == 'POST':
        session = Session()
        try:
            delete_room(session, room_id=int(room_id))
            session.commit()
            return redirect(url_for('room_settings'))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('room_settings'))
        finally:
            session.close()


@app.route('/admin/settings/users_settings')
@login_required
def users_settings():
    session = Session()
    try:
        if is_admin(current_user):
            users = get_user(session, all=True)
            users = filter(lambda us: us.email != 'admin@gmail.com', users)
            users = sorted(users, key=lambda us: (us.id))
            return make_response(render_template("users_settings.html", users=users))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('user_settings'))
    finally:
        session.close()


@app.route('/admin/settings/user_settings_form', methods=['GET', 'POST'])
@login_required
def users_settings_form():
    if request.method == 'POST':
        session = Session()
        try:
            user_id = request.form['user']
            return redirect(url_for('user_settings', user_id=user_id))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('user_settings'))
        finally:
            session.close()


@app.route('/admin/settings/user_settings/user/<user_id>')
@login_required
def user_settings(user_id):
    session = Session()
    try:
        if is_admin(current_user):
            user = get_user(session, id=user_id)
            for role in user.roles:
                print(role.name)
            return make_response(render_template("user_settings.html", user=user, isStaff=(get_role(session,name="Trainer") in user.roles)))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        if is_admin(current_user):
            return redirect(url_for('user_settings', user_id=user_id))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()

@app.route('/admin/settings/user_settings/user/reset_covid_state/<user_id>')
@login_required
def reset_covid_state(user_id):
    session = Session()
    try:
        update_user(session=session, user_id=user_id, covid_state=0)
        session.commit()
        return redirect(url_for('user_settings', user_id=user_id))         
    except BaseException as exc:
        flash(str(exc), category='error')
        session.rollback()
        session.close()
        return redirect(url_for('user_settings'), user_id=user_id)
    finally:
        session.close()

@app.route('/admin/settings/new_deadline/<user_id>', methods=["POST"])
def new_deadline(user_id):
    if request.method == 'POST':
        session = Session()
        try:
            date_str = request.form["date"]
            date_str = date_str.replace('-', '/')
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
            update_user(session, user_id=user_id, subscription=date)
            session.commit()
            return redirect(url_for('user_settings', user_id=user_id))
        except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('user_setting'), user_id=user_id)
        finally:
            session.close()

@app.route('/admin/settings/user_settings/assign_trainer_role/<user_id>')
def assign_trainer_role_(user_id):
    session = Session()
    try:
        assign_trainer_role(session, user_id=user_id)
        session.commit()
        return redirect(url_for('user_settings', user_id=user_id))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('user_setting'), user_id=user_id)
    finally:
        session.close()

@app.route('/admin/settings/user_settings/revoke_trainer_role/<user_id>')
def revoke_trainer_role_(user_id):
    session = Session()
    try:
        revoke_trainer_role(session, user_id=user_id)
        session.commit()
        return redirect(url_for('user_settings', user_id=user_id))
    except BaseException as exc:
            raise
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('user_settings', user_id=user_id))
    finally:
        session.close()

@app.route('/admin/users_info')
@login_required
def users_info():
    session = Session()
    try:
        if is_admin(current_user):
            users = get_user(session, all=True)
            users = filter(lambda us: us.email != 'admin@gmail.com', users)
            return make_response(render_template("users_info.html", users=users))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('private'))
    finally:
        session.close()

@app.route('/admin/deadlines')
@login_required
def deadlines():
    session = Session()
    try:
        if is_admin(current_user):
            valid =     filter(lambda us: us.subscription >= datetime.date.today(), filter(lambda us: us.email != 'admin@gmail.com', get_user(session, all=True)))
            not_valid = filter(lambda us: us.subscription <  datetime.date.today(), filter(lambda us: us.email != 'admin@gmail.com', get_user(session, all=True)))
            valid =     sorted(valid,     key=lambda us: us.subscription)
            not_valid = sorted(not_valid, key=lambda us: us.subscription)
            return make_response(render_template("deadlines.html", valid=valid, not_valid=not_valid))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('private'))
    finally:
        session.close()

@app.route('/admin/covid_states')
@login_required
def covid_states():
    session = Session()
    try:
        if is_admin(current_user):
            cs0 = filter(lambda us: us.covid_state == 0, filter(lambda us: us.email != 'admin@gmail.com',  get_user(session, all=True)))
            cs1 = filter(lambda us: us.covid_state == 1, filter(lambda us: us.email != 'admin@gmail.com',  get_user(session, all=True)))
            cs2 = filter(lambda us: us.covid_state == 2, filter(lambda us: us.email != 'admin@gmail.com',  get_user(session, all=True)))
            return make_response(render_template("covid_states.html", cs0=cs0, cs1=cs1, cs2=cs2))
        else:
            return redirect(url_for('private'))
    except BaseException as exc:
            flash(str(exc), category='error')
            session.rollback()
            session.close()
            return redirect(url_for('private'))
    finally:
        session.close()