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

#__________________________________________HOME________________________________________
@app.route('/')
def home():
    try:
        return render_template("home.html")
    except:
        raise

# ________________________________________________________PRIVATE________________________________________________________

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
        email = current_user.email
        user = get_user(session, email=email)
        resp = make_response(render_template("private.html", us = user, new_mess=new_messages()))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/prenotations')
@login_required
def prenotations():
    session = Session() 
    try:
        email = current_user.email
        user = get_user(session, email=email)
        shifts = filter(lambda sh: sh.date >= datetime.date.today(), user.prenotations_shifts)
        past_shifts = filter(lambda sh: sh.date <= datetime.date.today() and datetime.datetime.now().time() >= sh.h_end, user.prenotations_shifts)
        resp = make_response(render_template("prenotations.html", shifts=shifts, past_shifts=past_shifts))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/courses_sign_up')
@login_required
def courses_sign_up():
    session = Session() 
    try:
        email = current_user.email
        user = get_user(session, email=email)
        courses = user.courses
        resp = make_response(render_template("courses_sign_up.html", courses=courses, today=datetime.date.today()))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/trainer_courses')
@login_required
def trainer_courses():
    session = Session()
    try:
        trainer = get_trainer(session, id = current_user.id)
        if trainer is not None:
            courses = trainer.courses
            session.commit()
            return render_template("trainer_courses.html", courses = courses, trainer = trainer, today= datetime.date.today())
        else:
            session.commit()
            abort(401)
    except:
        session.rollback()
        raise
    finally:
        session.close()


@app.route('/private/trainer_courses/<course_name>')
@login_required
def trainer_course(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, id = current_user.id)
        course = get_course(session, name = course_name)
        if trainer is not None and course.instructor_id == trainer.id:
            course_program = get_course_program(session, course_id = course.id)
            sh = []
            for i in course_program:
                sh.append(get_shift(session, id=i.turn_number))
            session.commit()
            return render_template("trainer_course.html", course = course, course_program = course_program, shifts = sh)
        else:
            session.commit()
            abort(401)
    except:
        session.rollback()
        raise
    finally:
        session.close()


# ________________________________________________________PRENOTATION________________________________________________________

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
            shifts = filter(lambda sh: sh.h_start >= datetime.datetime.now().time(), shifts)
        resp = make_response(render_template("shifts.html", shifts=sorted(shifts, key=lambda x: (x.h_start, x.room_id)), date_string=date_string, rooms=r))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/shifts/first')
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
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/prenotation/<shift>')
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
    except:
        session.rollback()
        raise
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
    except:
        session.rollback()
        raise
    finally:
        session.close()

# ________________________________________________________COURSES________________________________________________________

@app.route('/courses')
def courses():
    session = Session()
    try:
        courses = get_course(session, all=True)
        if current_user.is_authenticated and "Staff" in current_user.roles:
            return render_template("courses.html", courses = courses, isStaff=True)
        return render_template("courses.html", courses = courses, isStaff=False)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/<course_name>')
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
            if "Staff" in current_user.roles:
                return render_template("course.html", course = c, course_program = cp, shift = sh, course_sign_up = cs, isStaff=True)
            return render_template("course.html", course = c, course_program = cp, shift = sh, course_sign_up = cs, isStaff=False)
        return render_template("course.html", course = c, course_program = cp, shift = sh, isStaff=False)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/delete_course/<course_name>', methods=['POST'])
def del_course(course_name):
    session = Session()
    try:
        c = get_course(session, name = course_name)
        if current_user.is_authenticated :
            delete_course(session, course = c)
            session.commit()
            return redirect(url_for('courses'))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/new_course')
def new_course():
    session = Session()
    try:
        if current_user.is_authenticated:
            if "Staff" in current_user.roles:
                r = get_room(session, all=True)
                return render_template('add_course.html', rooms=r)
            return redirect(url_for('courses'))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/new_course_form', methods=['GET', 'POST'])
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
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/courses/new_course/new_program/<course_name>')
def new_program(course_name):
    session = Session()
    try:
        rooms = get_room(session, all=True)
        r = {}
        for room in rooms:
            r[room.id] = room.name
        return render_template('new_program.html', course = get_course(session, name=course_name), room_dict = r)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/undo_course/<course_name>')
def undo_course(course_name):
    session = Session()
    try:
        c = get_course(session, name=course_name)
        starting = c.starting
        ending = c.ending
        max_partecipants = c.max_partecipants
        delete_course(session, course=c)
        session.commit()
        return render_template('add_course.html', rooms=get_room(session, all=True), course_name=course_name, starting=starting, ending=ending, max_partecipants=max_partecipants)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/new_course/add_program/<course_name>')
def add_program(course_name):
    session = Session()
    try:
        r = get_room(session, all=True)
        return render_template('add_program.html', rooms = r, course = get_course(session, name=course_name), week_setting = get_week_setting(session, all=True))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/new_course/add_program_form/<course_name>', methods=['POST', 'GET'])
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
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/courses/new_course/del_program/<program_id>/<course_name>')
def del_program(program_id, course_name):
    session = Session()
    try:
        session.query(CourseProgram).where(CourseProgram.id==program_id).delete()
        session.commit()
        return redirect(url_for('new_program', course_name = course_name))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/new_course/plan_course/<course_name>')
def plan_course_(course_name):
    session = Session()
    try:
        plan_course(session, course_name)
        session.commit()
        return redirect(url_for('course', course_name=course_name))
    except:
        session.rollback()
        raise
    finally:
        session.close()
        

@app.route('/sign_up/<course_name>')
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
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/delete_sign_up/<course_name>')
def delete_sign_up(course_name):
    session = Session()
    try:
        us = get_user(session,id = current_user.id)
        c = get_course(session, name = course_name)
        delete_course_sign_up(session,course = c, user = us)
        session.commit()
        return redirect(url_for('courses_sign_up'))
    except:
        session.rollback()
        raise
    finally:
        session.close()


# ________________________________________________________LOGIN - SIGNIN________________________________________________________
@app.route('/signin')
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('private'))
    return render_template("signin.html")

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
        except:
            session.rollback()
            raise
        finally:
            session.close()
                
@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('private'))
    return render_template("login.html")

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
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/private/update_user')
@login_required
def upd_user():
    session = Session()
    try:
        user = get_user(session, id = current_user.id)
        return render_template("update_user.html", user = user)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/update_user_form', methods=['POST'])
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
                
            if update_user(session, user = user, fullname = fullname, telephone = telephone, address = address, pwd1 = pwd1, pwd2 = pwd2):
                session.commit()
                return redirect(url_for('private')) 
            else:
                return redirect(url_for('upd_user'))
        except:
            session.rollback()
            raise
        finally:
            session.close()
    

# ________________________________________________________MESSAGES________________________________________________________
@app.route('/private/covid_report')
@login_required
def covid_report():
    session = Session() 
    try:
        covid_report_messages(session, current_user.id)
        session.commit()
        return redirect(url_for('private'))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/messages')
@login_required
def messages():
    session = Session() 
    try:
        messages = get_message(session, addresser=current_user.id)
        for message in messages:
            print(message.text)
        resp = make_response(render_template("messages.html", messages=reversed(messages)))
        mark_read(session, messages)
        session.commit()
        return resp
    except:
        session.rollback()
        raise
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
        except:
            session.rollback()
            raise
        finally:
            session.close()

# ________________________________________________________ADMIN SETTINGS________________________________________________________
def is_admin(us):
    return us.is_authenticated and "Admin" in us.roles

@app.route('/admin/settings')
@login_required
def settings():
    try:
        if is_admin(current_user):
            return make_response(render_template("settings.html"))
        else:
            return redirect(url_for('private'))
    except:
        raise

@app.route('/admin/settings/global_settings')
@login_required
def global_settings():
    session = Session()
    try:
        if is_admin(current_user):
            global_settings = get_global_setting(session, all=True)
            resp= make_response(render_template("update_global_settings.html", global_settings=global_settings))
            return resp
        else:
            return redirect(url_for('private'))
    except:
        session.rollback()
        raise
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
    except:
        session.rollback()
        raise
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
        except:
            session.rollback()
            raise
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
        except:
            session.rollback()
            raise
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
    except:
        session.rollback()
        raise
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
                raise Exception("Could not plan shift in the past")
            add_room(session, name=name, max_capacity=max_capacity)
            session.flush()
            room = get_room(session, name=name)
            if room is not None:
                print(room.name + " " + str(room.id))
                plan_shifts(session, starting=datetime.date.today(), ending=date, room_id=room.id)
            else:
                raise Exception("non trovo stanza appena aggiunta")
            session.commit()
            return redirect(url_for('room_settings'))
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/admin/settings/room_settings/delete_room/<room_id>', methods=['POST'])
@login_required
def del_room(room_id):
    if request.method == 'POST':
        session = Session()
        try:
            delete_room(session, room_id=room_id)
            session.commit()
            return redirect(url_for('room_settings'))
        except:
            session.rollback()
            raise
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
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/admin/settings/user_settings_form', methods=['GET', 'POST'])
def users_settings_form():
    if request.method == 'POST':
        session = Session()
        try:
            if is_admin(current_user):
                user_id = request.form['user']
                return redirect(url_for('user_settings', user_id=user_id))
            else:
                return redirect(url_for('private'))
            
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/admin/settings/user_settings/<user_id>')
def user_settings(user_id):
    session = Session()
    try:
        if is_admin(current_user):
            user = get_user(session, id=user_id)
            return make_response(render_template("user_settings.html", user=user, isStaff=(get_role(session,name="Staff") in user.roles)))
        else:
            return redirect(url_for('private'))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/admin/settings/reset_covid_state/<user_id>')
def reset_covid_state(user_id):
    session = Session()
    try:
        update_user_covid_state(session=session, user_id=user_id, value=0)
        session.commit()
        return redirect(url_for('user_settings', user_id=user_id))         
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/admin/settings/new_deadline/<user_id>', methods=["POST"])
def new_deadline(user_id):
    if request.method == 'POST':
        session = Session()
        try:
            for pr in request.form:
                print("AAA")
                print(pr)
            date_str = request.form["date"]
            date_str = date_str.replace('-', '/')
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
            update_user_deadline(session, user_id=user_id, date=date)
            session.commit()
            return redirect(url_for('user_settings', user_id=user_id))
        except:
            session.rollback()
            raise
        finally:
            session.close()

@app.route('/admin/settings/user_settings/assign_trainer_role/<user_id>')
def assign_trainer_role_(user_id):
    session = Session()
    try:
        assign_trainer_role(session, user_id=user_id)
        session.commit()
        return redirect(url_for('user_settings', user_id=user_id))
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/admin/settings/user_settings/revoke_trainer_role/<user_id>')
def revoke_trainer_role_(user_id):
    session = Session()
    try:
        revoke_trainer_role(session, user_id=user_id)
        session.commit()
        return redirect(url_for('user_settings', user_id=user_id))
    except:
        session.rollback()
        raise
    finally:
        session.close()