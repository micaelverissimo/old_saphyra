
from TuningTools.monitoring import TuningMonitoringTool

MoM =  TuningMonitoringTool( 'crossValStat.pic.gz', 'crossValStat_monitoring.root')

MoM( doBeamer=True , overwrite=True, level=0 )


