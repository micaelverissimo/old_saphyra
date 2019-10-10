
#from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()
from saphyra.db.models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer')
Session = sessionmaker(bind=engine)
session = Session()
#Base.metadata.clear()
#Base.metadata.drop_all(bind=engine)

user = session.query(Worker).filter(Worker.username=='jodafons').first()
print (user)


task = Task(taskName='user.jodafons.dev_task',etBinIdx=0,etaBinIdx=0,status='registered')
user.addTask(task)
#session.drop_all()  
#user = User( name='jodafons' )
#user2 = Username( username='mverissi' )
#session.add(user)
#session.add(user2)
session.commit()
session.close()







