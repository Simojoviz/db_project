from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base


engine = create_engine('postgresql://utente:password@localhost:5432/Gym', echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)

Base.metadata.drop_all(engine)  
