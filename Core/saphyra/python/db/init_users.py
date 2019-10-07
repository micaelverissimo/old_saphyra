
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer')
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(engine)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()
session.commit()
#session.drop_all()  

user = User( username='jodafons' )
session.add(user)

task = Task( taskName = 'user.jodafons.test' )

for i in range(10):
  job  = Job(status=Status.RUNNING) 
  for i in range(10):
    model = Model()
    job.addModel(model)
  task.addJob(job)

user.addTask(task)

session.commit()



users = session.query(User).all()
for s in users:
  s.addTask( task )
  print(s)

session.close()







