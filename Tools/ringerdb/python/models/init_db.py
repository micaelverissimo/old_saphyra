
#from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()
from saphyra.db.models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer')
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

users = ["jodafons", "mverissimo", "gabriel.milan","wsfreund","cadu.covas"]


for user in users:
  obj = Worker( username = user )
  session.add(obj)



session.commit()
session.close()







