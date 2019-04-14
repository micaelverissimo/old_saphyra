

from TuningTools.monitoring import MonitoringTool

basepaths = 'data/monitoring'

summaryList =  [
            basepaths+'/crossval_mc16_calo_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/summary.pic.gz',
            basepaths+'/crossval_mc16_track_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/summary.pic.gz',
            basepaths+'/crossval_mc16_caloAndTrack_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/summary.pic.gz',
            basepaths+'/crossval_mc16_caloAndShowerAndTrack_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection/summary.pic.gz',
          ]

cnames = [
            '$LH(shower+track)$',
            '$NN(rings)$',
            '$NN(track)$',
            '$ExNN(rings+track)$',
            '$ExNN(rings+shower+track)$',
          ]


dataLocation = 'data/files/mc16track_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.npz'


MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='MediumID Comparison', outname='medium_comparison') 
#MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='MediumID Comparison', outname='medium_comparison',toPDF=False) 


summaryList =  [
            basepaths+'/crossval_mc16_calo_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/summary.pic.gz',
            basepaths+'/crossval_mc16_track_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/summary.pic.gz',
            basepaths+'/crossval_mc16_caloAndTrack_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/summary.pic.gz',
            basepaths+'/crossval_mc16_caloAndShowerAndTrack_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection/summary.pic.gz',
          ]

#MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='VeryLooseID Comparison', outname='veryLoose_comparison') 
#MonitoringTool.compareTTsReport(cnames,summaryList,dataLocation,title='VeryLooseID Comparison', outname='veryLoose_comparison',toPDF=False) 















