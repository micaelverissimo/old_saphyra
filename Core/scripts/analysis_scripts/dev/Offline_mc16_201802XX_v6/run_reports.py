


basepath = 'data/crossval'


crossval = [

			'mc16a.zee.20M.jf17.20M.offline.binned.caloAndShowerAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
			'mc16a.zee.20M.jf17.20M.offline.binned.caloAndShowerAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',

			'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Tight_PileupCorrection',
			'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
			'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Loose_PileupCorrection',
			'mc16a.zee.20M.jf17.20M.offline.binned.caloAndTrack.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',

			'mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
			'mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',
			
			'mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
      'mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',
			
			'mc16a.zee.20M.jf17.20M.offline.binned.calo.wdatadrivenlh.v6.crossValStat_Offline_CutBasedMedium_PileupCorrection',
		]


dirnames = [
							'crossval_mc16_caloAndShowerAndTrack_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
							'crossval_mc16_caloAndShowerAndTrack_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',

							'crossval_mc16_caloAndTrack_Offline_LH_DataDriven2016_Rel21_Tight_PileupCorrection',
							'crossval_mc16_caloAndTrack_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
							'crossval_mc16_caloAndTrack_Offline_LH_DataDriven2016_Rel21_Loose_PileupCorrection',
							'crossval_mc16_caloAndTrack_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',

							'crossval_mc16_calo_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
							'crossval_mc16_calo_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',
							
							'crossval_mc16_track_Offline_LH_DataDriven2016_Rel21_Medium_PileupCorrection',
							'crossval_mc16_track_Offline_LH_DataDriven2016_Rel21_VeryLoose_PileupCorrection',
	
							'crossval_mc16_calo_Offline_CutBasedMedium_PileupCorrection',
						]


data  = 'data/files/mc16track_lhgrid_v3/mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.npz'

command = 'crossValStatMonAnalysis.py -f {} -d {} -o {}'


import os
for i in range(len(dirnames)):
	cmd = command.format(basepath+'/'+crossval[i], data, dirnames[i])
	os.system(cmd); break



