

import os
import glob
begin = 'mc16a.zee.20M.jf17.20M.offline.binned.track.wdatadrivenlh.v6.crossValStat'

for f in glob.glob("*.gz"):
  partname = f.split('_')
  end = partname[2]+'_'+partname[3]
  newname =  begin+'_'+end
  os.system('mv '+f+' '+newname)

