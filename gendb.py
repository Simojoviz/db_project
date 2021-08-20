from sqlalchemy import create_engine

from automap import *

# engine = create_engine('sqlite:///database.db', echo=True)
#engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=False)
#engine = create_engine('postgresql://postgres:gemellirosa@localhost:5432/Gym', echo=True)

Base.metadata.create_all(engine)

#_________________________________________________CHECK_________________________________________________
conn = engine.connect()

#___________USER___________
conn.execute(
    "ALTER TABLE public.users\
    DROP CONSTRAINT IF EXISTS email_at;\
    ALTER TABLE public.users\
    ADD CONSTRAINT email_at CHECK (email::text LIKE '%%@%%'::text)\
    NOT VALID;\
    \
    COMMENT ON CONSTRAINT email_at ON public.users\
    IS 'email must contain @';"
)

conn.execute(
    "ALTER TABLE public.users\
    DROP CONSTRAINT IF EXISTS password_length;\
    ALTER TABLE public.users\
    ADD CONSTRAINT password_length CHECK (length(pwd::text) >= 6);\
    \
    COMMENT ON CONSTRAINT password_length ON public.users\
        IS 'password must be longer than 6 characters';"
)

#___________SHIFT___________
conn.execute(
    "ALTER TABLE public.shifts\
    DROP CONSTRAINT IF EXISTS shift_start_end;\
    ALTER TABLE public.shifts\
    ADD CONSTRAINT shift_start_end CHECK (h_start < h_end);\
    \
    COMMENT ON CONSTRAINT shift_start_end ON public.shifts\
        IS 'shift starting hour must be before the ending hour';"
)

#___________WEEK SETTING___________
conn.execute(
    "ALTER TABLE public.week_setting\
    DROP CONSTRAINT IF EXISTS valid_dayname;\
    ALTER TABLE public.week_setting\
    ADD CONSTRAINT valid_dayname CHECK (day_name::text = ANY (ARRAY['Monday'::character varying, 'Tuesday'::character varying, 'Wednesday'::character varying, 'Thursday'::character varying, 'Friday'::character varying, 'Saturday'::character varying, 'Sunday'::character varying]::text[]))\
    NOT VALID;\
    \
    COMMENT ON CONSTRAINT valid_dayname ON public.week_setting\
    IS 'dayname must be valid';"
)

conn.execute(
    "ALTER TABLE public.week_setting\
    DROP CONSTRAINT IF EXISTS week_setting_start_end;\
    ALTER TABLE public.week_setting\
    ADD CONSTRAINT week_setting_start_end CHECK (starting < ending);\
    \
    COMMENT ON CONSTRAINT week_setting_start_end ON public.week_setting\
        IS 'the starting hour must be before the ending hour';"
)


#___________GLOBAL SETTING___________
conn.execute(
    "ALTER TABLE public.global_settings\
    DROP CONSTRAINT IF EXISTS positive_value;\
    ALTER TABLE public.global_settings\
    ADD CONSTRAINT positive_value CHECK (""value"" > 0);\
    COMMENT ON CONSTRAINT positive_value ON public.global_settings\
    IS 'setting value must be positive';"
)

#___________COURSE___________
conn.execute(
    "ALTER TABLE public.courses\
    DROP CONSTRAINT IF EXISTS course_start_end;\
    ALTER TABLE public.courses\
    ADD CONSTRAINT course_start_end CHECK (starting < ending);\
    \
    COMMENT ON CONSTRAINT course_start_end ON public.courses\
        IS 'the starting hour must be before the ending hour';"
)

conn.execute(
    "ALTER TABLE public.courses\
    DROP CONSTRAINT IF EXISTS positive_max_partecipants;\
    ALTER TABLE public.courses\
    ADD CONSTRAINT positive_max_partecipants CHECK (max_partecipants>0);\
    \
    COMMENT ON CONSTRAINT positive_max_partecipants ON public.courses\
        IS 'max_partecipants must be positive';"
)

#___________COURSE_PROGRAM___________
conn.execute(
    "ALTER TABLE public.course_programs\
    DROP CONSTRAINT IF EXISTS valid_weekday;\
    ALTER TABLE public.course_programs\
    ADD CONSTRAINT valid_weekday CHECK (week_day::text = ANY (ARRAY['Monday'::character varying, 'Tuesday'::character varying, 'Wednesday'::character varying, 'Thursday'::character varying, 'Friday'::character varying, 'Saturday'::character varying, 'Sunday'::character varying]::text[]))\
    NOT VALID;\
    \
    COMMENT ON CONSTRAINT valid_weekday ON public.course_programs\
    IS 'weekday must be valid';"
)

conn.execute(
    "ALTER TABLE public.course_programs\
    DROP CONSTRAINT IF EXISTS positive_turn_number;\
    ALTER TABLE public.course_programs\
    ADD CONSTRAINT positive_turn_number CHECK (turn_number>0);\
    \
    COMMENT ON CONSTRAINT positive_turn_number ON public.course_programs\
    IS 'turn number must be positive';"
)

#___________ROOM___________
conn.execute(
    "ALTER TABLE public.rooms\
    DROP CONSTRAINT IF EXISTS positive_max_capacity;\
    ALTER TABLE public.rooms\
    ADD CONSTRAINT positive_max_capacity CHECK (max_capacity > 0);\
    \
    COMMENT ON CONSTRAINT positive_max_capacity ON public.rooms\
        IS 'max_capacity must be positive';"
)

#___________MESSAGE___________
conn.execute(
    "ALTER TABLE public.messages\
    DROP CONSTRAINT IF EXISTS sender_addressee;\
    ALTER TABLE public.messages\
    ADD CONSTRAINT sender_addressee CHECK (sender <> addressee);\
    \
    COMMENT ON CONSTRAINT sender_addressee ON public.messages\
        IS 'sender must not be addresser too';"
)

conn.execute(
    "ALTER TABLE public.messages\
    DROP CONSTRAINT IF EXISTS not_empty_text;\
    ALTER TABLE public.messages\
    ADD CONSTRAINT not_empty_text CHECK (text <> '');\
    \
    COMMENT ON CONSTRAINT not_empty_text ON public.messages\
        IS 'text cannot be empty';"
)



#_________________________________________________TRIGGER_________________________________________________

#___________PRENOTATION___________

conn.execute(
    "DROP FUNCTION IF EXISTS public.no_invalid_prenotation() CASCADE;\
    CREATE FUNCTION public.no_invalid_prenotation()\
    RETURNS trigger\
    LANGUAGE 'plpgsql'\
    COST 100\
    VOLATILE NOT LEAKPROOF\
    AS $BODY$\
    BEGIN\
        IF NEW.client_id IN (\
            SELECT client_id\
            FROM prenotations\
            WHERE shift_id = NEW.shift_id\
        ) THEN\
            RAISE EXCEPTION 'Cannot prenote: User cannot prenote twice for the same Shift';\
            RETURN NULL;\
        ELSIF (\
            SELECT count(*)\
            FROM prenotations\
            WHERE shift_id = NEW.shift_id\
        ) = (\
            SELECT r.max_capacity\
            FROM rooms r JOIN shifts s ON r.id = s.room_id\
            WHERE s.id = NEW.shift_id\
        ) THEN\
            RAISE EXCEPTION 'Cannot prenote: The shift is full';\
            RETURN NULL;\
        ELSIF (\
            SELECT course_id\
            FROM shifts\
            WHERE id = NEW.shift_id\
        ) IS NOT NULL THEN\
            RAISE EXCEPTION 'Cannot prenote: Shift occupied by a course';\
            RETURN NULL;\
        END IF;\
        RETURN NEW;\
    END\
    $BODY$;\
    \
    ALTER FUNCTION public.no_invalid_prenotation()\
        OWNER TO postgres;\
    \
    COMMENT ON FUNCTION public.no_invalid_prenotation()\
        IS 'Raise an exception if - User cannot prenote twice for the same Shift, The shift is full, The shift is occupied by a course ';\
        \
    CREATE TRIGGER NoInvalidPrenotation\
    BEFORE INSERT OR UPDATE\
    ON public.prenotations\
    FOR EACH ROW\
    EXECUTE PROCEDURE public.no_invalid_prenotation();\
    \
    COMMENT ON TRIGGER NoInvalidPrenotation ON public.prenotations\
        IS 'Raise an exception if - User cannot prenote twice for the same Shift, The shift is full, The shift is occupied by a course ';"
)

#___________COURSE SIGN UP___________

conn.execute(
    "DROP FUNCTION IF EXISTS public.no_invalid_sign_up() CASCADE;\
    CREATE FUNCTION public.no_invalid_sign_up()\
    RETURNS trigger\
    LANGUAGE 'plpgsql'\
    COST 100\
    VOLATILE NOT LEAKPROOF\
    AS $BODY$\
    BEGIN\
        IF NEW.user_id = (\
            SELECT instructor_id\
            FROM courses\
            WHERE id=NEW.course_id\
        ) THEN\
            RAISE EXCEPTION 'Cannot Sign-Up: Trainer cannot sign-up for his course';\
            RETURN NULL;\
        ELSIF NEW.user_id IN (\
            SELECT user_id\
            FROM course_signs_up\
            WHERE course_id=NEW.course_id\
        ) THEN\
            RAISE EXCEPTION 'Cannot Sign-Up: User cannot sign-up twice for the same course';\
            RETURN NULL;\
        ELSIF (\
            ( SELECT max_partecipants FROM courses WHERE id = NEW.course_id ) = \
            ( SELECT COUNT(*) FROM course_signs_up WHERE course_id = NEW.course_id) \
        ) THEN\
            RAISE EXCEPTION 'Cannot Sign-Up: Course is full';\
            RETURN NULL;\
        END IF;\
        RETURN NEW;\
    END\
    $BODY$;\
    \
    ALTER FUNCTION public.no_invalid_sign_up()\
        OWNER TO postgres;\
    \
    COMMENT ON FUNCTION public.no_invalid_sign_up()\
        IS 'Raise an exception if - Trainer sign-up for his own course, User  sign-up twice for the same course, The course is full ';\
    \
    CREATE TRIGGER NoInvalidSignUp\
    BEFORE INSERT OR UPDATE\
    ON public.course_signs_up\
    FOR EACH ROW\
    EXECUTE PROCEDURE public.no_invalid_sign_up();\
    \
    COMMENT ON TRIGGER NoInvalidSignUp ON public.course_signs_up\
    IS 'Raise an exception if - Trainer sign-up for his own course, User  sign-up twice for the same course, The course is full ';"
)