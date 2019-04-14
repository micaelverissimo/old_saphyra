

from TuningTools.monitoring import MonitoringTool

basepath = '.'
dataLocation = 'data_cern/files/data_entries.pic.gz'
cnames = [
            '$CutBased$',
            '$NN_{v8}(rings)$',
            '$CNN_{v10}(vortex)$',
            '$CNN_{v11}(conv1D)$',
          ]


summaryList =  [
            basepath+'/report_tight_v8/summary.pic.gz',
            basepath+'/report_tight_v10/summary.pic.gz',
            basepath+'/report_tight_v11/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v8 Vs v10 Vs v11) Tight', outname='comparison_ref_v8_v10_v11_tight') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v8 Vs v10 Vs v11) Tight', outname='comparison_ref_v8_v10_v11_tight',toPDF=False) 


summaryList =  [
            basepath+'/report_vloose_v8/summary.pic.gz',
            basepath+'/report_vloose_v10/summary.pic.gz',
            basepath+'/report_vloose_v11/summary.pic.gz',
          ]

MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v8 Vs v10 Vs v11) VeryLoose', outname='comparison_ref_v8_v10_v11_vloose') 
MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='Comparison (ref Vs v8 Vs v10 Vs v11) VeryLoose', outname='comparison_ref_v8_v10_v11_vloose',toPDF=False) 






