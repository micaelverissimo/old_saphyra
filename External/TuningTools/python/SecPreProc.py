__all__ = ["ReshapeToConv1D", "ConcentricSquareRings","SpiralRings"]


from Gaugi import ( Logger, LoggerStreamable, checkForUnusedVars, EnumStringification
                       , save, load, LimitedTypeList, LoggingLevel, LoggerRawDictStreamer
                       , LimitedTypeStreamableList, RawDictStreamer, RawDictCnv )
from TuningTools.coreDef import npCurrent
from copy import deepcopy
import numpy as np


class ReshapeToConv1D(object):
  def __init__(self):
    pass
  def __call__(self,data):
    data=  np.array([data])
    data = np.transpose(data, [1,2,0])
    return data
 

class ConcentricSquareRings(Logger):

  def __init__(self):
    Logger.__init__(self)


  # toke from: https://codereview.stackexchange.com/questions/195233/print-concentric-rectangular-patterns
  def _make_concentric_squares(self, num):
  
      m = n = 2*num -1 ##    m x n matrix , length of each row and column
      k = 0 # row start counter
      l = 0 # column start counter
      i = 0 # iterator
  
      matrix = [[0 for _ in range(n)] for _ in range(m)]
      while k < m and l < n :  
          #insert the first row
          for i in range(l, n) :      
              if matrix[k][i] == 0:
                  matrix[k][i] = num   # row index constt, change values in columns
          k += 1   # first row printed, so increment row start index
  
          #insert the last column
          for i in range(k, m) :         
              if matrix[i][n-1]==0:
                  matrix[i][n-1] = num   # column index constt, change values in rows
          n -= 1   # last column printed, so decrement num of columns
  
          #insert the last row
          if (k<m):   #  if row index less than number of rows remaining
              for i in range(n-1, l-1, -1):
                  if matrix[m-1][i] == 0:
                      matrix[m-1][i] = num   # row index constt, insert in columns
          m -= 1   # last row printed, so decrement num of rows
  
          #insert the first column
          if (l<n):    #  if column index less than number of columns remaining
              for i in range(m-1, k-1, -1):
                  if matrix[i][l] == 0:
                      matrix[i][l] = num # column index constt, insert in rows
          l += 1      # first column printed, so increment column start index
  
          num -= 1    # all elements of value A inserted , so decrement
      return matrix
  

  def _scale(self, mask, x, y):
    import numpy as np
    m = np.zeros( (mask.shape[0]*x, mask.shape[1]*y) )
    for i in range(mask.shape[0]):
      for j in range(mask.shape[1]):
        value = mask[i][j]
        for ii in range(x):
          for jj in range(y):
            m[ i*x + ii ][ j*y + jj] = value
    return m
  
  def _make_quarter_rings( self, rings, scale ):
    import numpy as np
    mask =  np.array(self._make_concentric_squares(rings.shape[1]))   
    from pprint import pprint
    
    center = np.where(mask==1)
    cx = center[0][0]; cy=center[1][0]
    mask = np.array([ mask[i][0:cy+1] for i in range(0,cx+1)])
    #pprint(mask)
    mask = self._scale( mask, scale, scale )
    
    #print (mask.shape[0],mask.shape[1],rings.shape[0]) 
    cells = np.zeros( (mask.shape[0],mask.shape[1],rings.shape[0]) )
    for r in range(len(rings)):
      pos = np.where(mask == r+1)
      for c in range(len(pos[0])):
        cells[pos[0][c]][pos[1][c]][:] = rings.T[r][:] / float(len(pos[0])/float(scale*scale))  
    return cells


  def __call__(self,data, layer=None):
    channels = []
    slices  =[(0,7),(8,71),(72,79),(80,87),(88,91),(92,95),(96,99)]
    scale     = [8, 1, 8, 8, 16, 16, 16]
    if type(layer) is int:
      s=slices[layer]
      channels.append( self._make_quarter_rings( data.T[s[0]:s[1]+1].T, scale[layer] ))
    if layer is None:
      for idx, s in enumerate(slices):
        channels.append( self._make_quarter_rings( data.T[s[0]:s[1]+1].T, scale[idx] ))
    channels= np.array(channels)
    channels = np.transpose(channels, [3,1,2,0])
    return channels




class SpiralRings(Logger):
  
  def __init__(self):
    Logger.__init__(self)
    # Do not change this if you dont know what are you doing
    # standard vortex configuration approach
    self._form = [  [72,73,74,75,76,77,78,79,80,81],
                    [71,42,43,44,45,46,47,48,49,82],
                    [70,41,20,21,22,23,24,25,50,83],
                    [69,40,19,6 ,7 ,8 ,9 ,26,51,84],
                    [68,39,18,5 ,0 ,1 ,10,27,52,85],
                    [67,38,17,4 ,3 ,2 ,11,28,53,86],
                    [66,37,16,15,14,13,12,29,54,87],
                    [65,36,35,34,33,32,31,30,55,88],
                    [64,63,62,61,60,59,58,57,56,89],
                    [99,98,97,96,95,94,93,92,91,90],
                  ]
    self._shape = (10,10)


  def _reshape( self, data, form, shape ):
    d = deepcopy(data.reshape( 1,shape[0],shape[1],data.shape[0] ))
    r=data.T
    for i in range(shape[0]):
      for j in range(shape[1]):
        d[0][i][j][::] = r[ form[i][j] ][::]
    d=d.T
    self._logger.info('Secondary Preproc reshape data %s do %s ',
                      str(data.shape),str(d.shape))
    return d


  def __call__(self,data):
    return self._reshape( data, self._form, self._shape)





