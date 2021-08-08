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
    try:
        email = current_user.email
        user = get_user(session, email=email)
        resp = make_response(render_template("private.html", us = user))
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
        shifts = user.prenotations_shifts
        shifts = filter(lambda sh: sh.h_start <= datetime.datetime.now().time(), user.prenotations_shifts)
        resp = make_response(render_template("prenotations.html", shifts=shifts))
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
        resp = make_response(render_template("courses_sign_up.html", courses=courses))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

# ________________________________________________________PRENOTATION________________________________________________________
@app.route('/shifts/<year>/<month>/<day>/<room>')
#@app.route('/shifts?year=&month=&day=&room=')
def shifts(day, month, year, room):
    try:
        session = Session()
        date = datetime.date(year=int(year), month=int(month), day=int(day))
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
        resp = make_response(render_template("shifts.html", shifts=sorted(shifts, key=lambda x: (x.room_id, x.h_start)), date_string=date_string, rooms=r))
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
    return redirect(url_for('shifts', year = curr.year, month=curr.month, day=curr.day, room='All'))

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
            return redirect(url_for('shifts', year = date.year, month=date.month, day=date.day, room=room))
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
def del_prenotation(shift):
    try:
        session = Session()
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
    try:
        session = Session()
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

@app.route('/courses/delete_course/<course_name>', methods=['POST'])
def del_course(course_name):
    try:
        session = Session()
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
    if current_user.is_authenticated:
        if "Staff" in current_user.roles:
            r = get_room(session, all=True)
            return render_template('add_course.html', rooms=r)
        return redirect(url_for('courses'))

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
    rooms = get_room(session, all=True)
    r = {}
    for room in rooms:
        r[room.id] = room.name
    return render_template('new_program.html', course = get_course(session, name=course_name), room_dict = r)
    

@app.route('/courses/new_course/add_program/<course_name>')
def add_program(course_name):
    session = Session()
    r = get_room(session, all=True)
    return render_template('add_program.html', rooms = r, course = get_course(session, name=course_name), week_setting = get_week_setting(session, all=True))

@app.route('/courses/new_course/add_program_form/<course_name>', methods=['POST', 'GET'])
def add_program_form(course_name):

    def to_second(t):
        return (t.hour * 60 + t.minute) * 60 + t.second

    if request.method == 'POST':
        session = Session()

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

@app.route('/courses/new_course/del_program/<program_id>/<course_name>')
def del_program(program_id, course_name):
    try:
        session = Session()
        print("AAA")
        print(course_name)
        print("AAA")
        print(program_id)
        print("AAA")
        session.query(CourseProgram).where(CourseProgram.id==program_id).delete()
        session.commit()
        return redirect(url_for('new_program', course_name = course_name))
    except:
        raise

@app.route('/courses/new_course/plan_course/<course_name>')
def plan_course_(course_name):
    try:
        session = Session()
        plan_course(session, course_name)
        session.commit()
        return redirect(url_for('course', course_name=course_name))
    except:
        raise
        

@app.route('/sign_up/<course_name>')
def sign_up(course_name):
    session = Session()
    if current_user.is_authenticated:
        us = get_user(session, id = current_user.id)
        c = get_course(session, name= course_name)
        add_course_sign_up(session, user=us, course=c)
        session.commit()
        return redirect(url_for('courses_sign_up'))
    return redirect(url_for('login'))


@app.route('/delete_sign_up/<course_name>')
def delete_sign_up(course_name):
    session = Session()
    us = get_user(session,id = current_user.id)
    c = get_course(session, name = course_name)
    delete_course_sign_up(session,course = c, user = us)
    session.commit()
    return redirect(url_for('courses_sign_up'))


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
            pwd1 = request.form['pwd1']
            pwd2 = request.form['pwd2']
            us = get_user(session, email=email)
            if fullname and email and pwd1 and pwd1 == pwd2 and us is None:
                flash("Signed in successfully.", category='success')
                add_user(session, fullname=fullname, email=email, pwd=pwd1)
                session.commit()
                return redirect(url_for('login'))
            if not fullname:
                flash("Please enter a fullname.", category='error')
            elif not email:
                flash("Please enter an email.", category='error')
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
    user = get_user(session, id = current_user.id)
    return render_template("update_user.html", user = user)

@app.route('/update_user_form', methods=['POST'])
@login_required
def update_user_form():
    session = Session()
    if request.method == 'POST':
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
        resp = make_response(render_template("messages.html"))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/messages/send')
@login_required
def sent():
    session = Session() 
    try:
        users = get_user(session, all=True)
        users.remove(get_user(session, id=current_user.id))
        messages = get_message(session, sender=current_user.id)
        resp = make_response(render_template("send.html", messages=messages, users=users))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/messages/addressed')
@login_required
def addressed():
    session = Session() 
    try:
        messages = get_message(session, addresser=current_user.id)
        resp = make_response(render_template("addressed.html", messages=messages))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/messages/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method == 'POST':
        session = Session()
        try:
            adr_id = request.form['addresser']
            text = request.form['text']
            add_message(session,current_user.id, adr_id, text)
            session.commit()
            return redirect(url_for('sent'))
        except:
            session.rollback()
            raise
        finally:
            session.close()

