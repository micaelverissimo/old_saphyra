



taskName = "user.jodafons.lps_dev"

from ringerdb import RingerDB
aws_url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'
db = RingerDB( "jodafons", aws_url )


task = db.createTask( taskName, "/dummy/config/path", "/dummy/input/path", "/dummy/output/path", "containerImage","LPS",
    templateExecArgs  = "python run_tuning.py -i %IN -c %CONFIG -o %OUT",
    secondaryDataPath  = "{}",
    etBinIdx=0,
    etaBinIdx=0,
    isGPU=False)



for i in range (10):

  job = db.createJob( task, "/dummy/config/path/file.npz", i, priority=-1, execArgs="{}",isGPU=False)




