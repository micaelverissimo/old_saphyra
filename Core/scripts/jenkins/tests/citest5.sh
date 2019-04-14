
runGRIDtuning.py -d user.jodafons.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.medium.npz \
               -pp user.wsfreund.ppFile_et_eta_bins_indep.pic.gz \
               -c user.wsfreund.config.nn5to20_sorts10_JackKnife_1by1_inits100_100by100 \
               -x user.wsfreund.crossValid-JackKnife.pic.gz \
               -xs user.wsfreund.crossValid-JackKnife-subset.pic.gz \
               -r user.wsfreund.reference.pic.gz \
               -o user.jodafons.nn.mc15_13TeV.sgn.361106.probes.newLH.bkg.423300.vetotruth.strig.l2calo.medium.npz \
               --cloud US \
               --long \
               --site ANALY_BNL_LONG\
               --eta-bins 0 3 --et-bin 0 4 \
               --dry-run




