
runGRIDtuning.py -d user.jodafons.mc14_13TeV.147406.129160.sgn.offLH.bkg.truth.trig.e24_lhmedium_nod0_l120_l219.20160324.pic.npz \
               -pp user.jodafons.Norm1.20160324 \
               -c user.jodafons:user.jodafons.config.nn5to10_sorts50_1by1_inits100_100by100.20160325 \
               -x user.jodafons.crossVal_50sorts_20160324.pic.gz \
               -o user.jodafons.nn.std.mc14.147406.129160.sgn.offLH.bkg.truth.trig.l2.e24_lhmedium_nod0_nobinned_t0005_nn5to10_cern \
               --cloud "CERN" \
               --long \
               #--site ANALY_BNL_LONG
               #--eta-bins 0 3 --et-bin 0 3 --dry-run --long
