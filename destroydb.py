from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import datetime

# engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=True)
# engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.metadata.drop_all(engine)  
