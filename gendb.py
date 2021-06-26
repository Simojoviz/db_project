from sqlalchemy import create_engine

from automap import *

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
#engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)

Base.metadata.create_all(engine)

#_________________________________________________CHECK_________________________________________________
conn = engine.connect()

#___________USER___________
conn.execute(
    "ALTER TABLE public.users\
    ADD CONSTRAINT email_at CHECK (email::text LIKE '%%@%%'::text)\
    NOT VALID;\
    \
    COMMENT ON CONSTRAINT email_at ON public.users\
    IS 'email must contain @';"
)

conn.execute(
    "ALTER TABLE public.users\
    ADD CONSTRAINT password_length CHECK (length(pwd::text) >= 6);\
    \
    COMMENT ON CONSTRAINT password_length ON public.users\
        IS 'password must be longer than 6 characters';"
)

#___________SHIFT___________
conn.execute(
    "ALTER TABLE public.shifts\
    ADD CONSTRAINT shift_start_end CHECK (h_start < h_end);\
    \
    COMMENT ON CONSTRAINT shift_start_end ON public.shifts\
        IS 'shift starting hour must be before the ending hour';"
)

#___________WEEK SETTING___________
conn.execute(
    "ALTER TABLE public.week_setting\
    ADD CONSTRAINT valid_dayname CHECK (day_name::text = ANY (ARRAY['Monday'::character varying, 'Tuesday'::character varying, 'Wednesday'::character varying, 'Thursday'::character varying, 'Friday'::character varying, 'Saturday'::character varying, 'Sunday'::character varying]::text[]))\
    NOT VALID;\
    \
    COMMENT ON CONSTRAINT valid_dayname ON public.week_setting\
    IS 'dayname must be valid';"
)

conn.execute(
    "ALTER TABLE public.week_setting\
    ADD CONSTRAINT week_setting_start_end CHECK (starting < ending);\
    \
    COMMENT ON CONSTRAINT week_setting_start_end ON public.week_setting\
        IS 'the starting hour must be before the ending hour';"
)

#___________COURSE___________
conn.execute(
    "ALTER TABLE public.courses\
    ADD CONSTRAINT course_start_end CHECK (starting < ending);\
    \
    COMMENT ON CONSTRAINT course_start_end ON public.courses\
        IS 'the starting hour must be before the ending hour';"
)

conn.execute(
    "ALTER TABLE public.courses\
    ADD CONSTRAINT positive_max_partecipants CHECK (max_partecipants>0);\
    \
    COMMENT ON CONSTRAINT positive_max_partecipants ON public.courses\
        IS 'max_partecipants must be positive';"
)

#___________COURSE_PROGRAM___________
conn.execute(
    "ALTER TABLE public.course_programs\
    ADD CONSTRAINT valid_weekday CHECK (week_day::text = ANY (ARRAY['Monday'::character varying, 'Tuesday'::character varying, 'Wednesday'::character varying, 'Thursday'::character varying, 'Friday'::character varying, 'Saturday'::character varying, 'Sunday'::character varying]::text[]))\
    NOT VALID;\
    \
    COMMENT ON CONSTRAINT valid_weekday ON public.course_programs\
    IS 'weekday must be valid';"
)

conn.execute(
    "ALTER TABLE public.course_programs\
    ADD CONSTRAINT positive_turn_number CHECK (turn_number>0);\
    \
    COMMENT ON CONSTRAINT positive_turn_number ON public.course_programs\
    IS 'turn number must be positive';"
)

#___________ROOM___________
conn.execute(
    "ALTER TABLE public.rooms\
    ADD CONSTRAINT positive_max_capacity CHECK (max_capacity > 0);\
    \
    COMMENT ON CONSTRAINT positive_max_capacity ON public.rooms\
        IS 'max_capacity must be positive';"
)

#___________MESSAGE___________
conn.execute(
    "ALTER TABLE public.messages\
    ADD CONSTRAINT sender_addressee CHECK (sender <> addressee);\
    \
    COMMENT ON CONSTRAINT sender_addressee ON public.messages\
        IS 'sender must not be addresser too';"
)

conn.execute(
    "ALTER TABLE public.messages\
    ADD CONSTRAINT not_empty_text CHECK (text <> '');\
    \
    COMMENT ON CONSTRAINT not_empty_text ON public.messages\
        IS 'text cannot be empty';"
)