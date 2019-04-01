

from TuningTools.monitoring import MonitoringTool

basepath = 'data_cern/reports'
dataLocation = 'data_cern/files/new_mc/data_entries.pic.gz'
cnames = [
            '$CutBased$',
            '$NN_{v6}(rings)$',
          ]


summaryList =  [
            basepath+'/report_tight_v6/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) Tight', outname='comparison_ref_v6_tight') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) Tight', outname='comparison_ref_v6_tight',toPDF=False) 

summaryList =  [
            basepath+'/report_medium_v6/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) Medium', outname='comparison_ref_v6_medium') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) Medium', outname='comparison_ref_v6_medium',toPDF=False) 

summaryList =  [
            basepath+'/report_loose_v6/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) Loose', outname='comparison_ref_v6_loose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) Loose', outname='comparison_ref_v6_loose',toPDF=False) 


summaryList =  [
            basepath+'/report_vloose_v6/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) VeryLoose', outname='comparison_ref_v6_vloose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v6) VeryLoose', outname='comparison_ref_v6_vloose',toPDF=False) 







