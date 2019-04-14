

from TuningTools.monitoring import MonitoringTool

basepath = 'data/reports/zee'
dataLocation = 'data/crossval/zee/data_entries.pic.gz'
cnames = [
            '$CutBased$',
            '$NN_{v8}(data17)$',
            '$NN_{v9}(data17+18)$',
          ]


summaryList =  [
            basepath+'/report_tight_v8/summary.pic.gz',
            basepath+'/report_tight_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Tight', outname='comparison_ref_v9_tight') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Tight', outname='comparison_ref_v9_tight',toPDF=False) 

summaryList =  [
            basepath+'/report_medium_v8/summary.pic.gz',
            basepath+'/report_medium_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Medium', outname='comparison_ref_v9_medium') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Medium', outname='comparison_ref_v9_medium',toPDF=False) 

summaryList =  [
            basepath+'/report_loose_v8/summary.pic.gz',
            basepath+'/report_loose_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Loose', outname='comparison_ref_v9_loose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Loose', outname='comparison_ref_v9_loose',toPDF=False) 


summaryList =  [
            basepath+'/report_vloose_v8/summary.pic.gz',
            basepath+'/report_vloose_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) VeryLoose', outname='comparison_ref_v9_vloose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) VeryLoose', outname='comparison_ref_v9_vloose',toPDF=False) 








basepath = 'data/reports/jpsi'
dataLocation = 'data/crossval/jpsi/data_entries.pic.gz'
cnames = [
            '$CutBased$',
            '$NN_{v9}(data17+18)$',
          ]


summaryList =  [
            basepath+'/report_tight_v9/summary.pic.gz',
          ]


MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Tight', outname='comparison_ref_v9_tight') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Tight', outname='comparison_ref_v9_tight',toPDF=False) 

summaryList =  [
            basepath+'/report_medium_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Medium', outname='comparison_ref_v9_medium') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Medium', outname='comparison_ref_v9_medium',toPDF=False) 

summaryList =  [
            basepath+'/report_loose_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Loose', outname='comparison_ref_v9_loose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) Loose', outname='comparison_ref_v9_loose',toPDF=False) 


summaryList =  [
            basepath+'/report_vloose_v9/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) VeryLoose', outname='comparison_ref_v9_vloose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v9) VeryLoose', outname='comparison_ref_v9_vloose',toPDF=False) 











