# Progetto DB 2020/2021

# Gruppo Casteo: Andrea Rosa, Simone Jovon, Sebastiano Quintavalle

# Il progetto che abbiamo consegnato è composto dai seguenti file:
1) automap.py: in cui sono definite in ORM tutte le tabelle che compongono il nostro database;
2) gendb.py: in cui viene creata l’istanza del database e vengono aggiunti tutti i trigger di controllo;
3) populate.py: si occupa di popolare tutte le tabelle del nostro database;
4) destroydb.py: si occupa di distruggere la base di dati in caso di evenienza;
5) model.py: contiene tutti i metodi che servono per le funzionalità della nostra applicazione;
6) app.py: racchiude le tutte le rotte della nostra applicazione;
7) template: contiene tutti i template html della nostra applicazione;
8) static: al suo interno ci sono le immagini utilizzate nell’applicazione.

# La sequenza di comandi, per utilizzare in locale la nostra applicazione, è la seguente:
1) python gendb.py
2) python populate.py
3) set FLASK_APP=app.py
4) flask run
5) sul browser aprire l’url: http://localhost:5000

# Il comando per distruggere la base di dati, e tutti i suoi dati, è il seguente:
1) python destroydb.py

# Nei seguenti file dovranno essere inserite le proprie credenziali del proprio database locale nell’url sottostante, per 
# permetterne la connessione:
1) app.py
2) gendb.py
3) destroydb.py
4) populate.py

