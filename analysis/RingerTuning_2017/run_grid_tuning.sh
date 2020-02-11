


runGRIDtuning.py \
 --do-multi-stop 0 \
 -c user.jodafons.configs.n5to10.jk.inits_20by20 \
 -d user.jodafons.mc15_13TeV.361106.423300.sgn.probes_lhmedium.bkg.vetotruth.patterns.npz \
 -p user.jodafons.ppFile.norm1.v6.pic.gz \
 -x user.jodafons.crossValid.v6.pic.gz \
 -r user.jodafons.mc15_13TeV.361106.423300.sgn.probes.bkg.vetotruth.trig.l2calo.vloose-eff.npz \
 -o user.jodafons.nn.mc15c_13TeV.361106.423300.sgn_Zee.bkg_JF17.Rel21.bestSP.Norm1.r0002 \
 --excludedSite ANALY_DESY-HH_UCORE ANALY_BNL_MCORE ANALY_MWT2_SL6 ANALY_MWT2_HIMEM  ANALY_DESY-HH ANALY_FZK_UCORE ANALY_FZU DESY-HH_UCORE FZK-LCG2_UCORE \
 --et-bins 0 4 \
 --eta-bins 0 3 \
 #--multi-files \
 #--dry-run
 




