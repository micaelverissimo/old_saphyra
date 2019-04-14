
from TuningTools.PreProc import *
ppCol1 = PreProcChain( [Norm1()] ) 
ppCol2 = PreProcChain( [Norm1()] ) 
ppCol3 = PreProcChain( [Norm1()] ) 



from TuningTools.TuningJob import fixPPCol
#ppCol = fixPPCol(ppCol)
#place = PreProcArchieve( 'ppFile', ppCol = ppCol ).save()
import numpy as np
A =  np.random.rand(3,5)
B =  np.random.rand(3,5)

print type(ppCol1)
print type(ppCol1[0])


from RingerCore import *




test = PreProcChain([ PreProcMerge(ppChains=[ppCol1, ppCol1]) ])
test = fixPPCol(test)
place = PreProcArchieve( 'ppFile', ppCol = test ).save()


with PreProcArchieve(place) as ppCol:
  print 'donw'
  print ppCol
  ppCol[0][0][0]([[A,A],[B,B]])



