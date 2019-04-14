
from TuningTools.monitoring import TuningMonitoringTool

MoM =  TuningMonitoringTool( 'crossValStat_13311301_et3_eta8.pic.gz', 'crossValStat_monitoring_et3_eta8.root')

MoM( doBeamer=True , overwrite=True, level=0 )


