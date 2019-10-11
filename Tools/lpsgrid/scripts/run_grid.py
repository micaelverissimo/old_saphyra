

from ringerdb import RingerDB
url = 'postgres://ringer:6sJ09066sV1990;6@postgres-ringer-db.cahhufxxnnnr.us-east-2.rds.amazonaws.com/ringer'



from lpsgrid import *


# Create all services
schedule      = Schedule( "Schedule", LCGRules(), 5*MINUTE )
db            = RingerDB('jodafons', url)
orchestrator  = Orchestrator( "Kubernetes", "../data/lps_cluster.yaml" )



# Create the pilot
#pilot  = Pilot("LPS_Cluster")
#
## Add slots
#pilot.setCPUSlot( Slots( "CPU" , maxlenght=100 ) )
#pilot.setGPUSlot(  Slots( "GPU" , maxlenght=1  , nodes=["node06"]) )
#
## Set services
#pilot.setDatabase( db )
#pilot.setSchedule( schedule )
#pilot.setOrchestrator( orchestrator )
#
#
## Start
#pilot.initialize()
#pilot.execute()
#pilot.finalize()


