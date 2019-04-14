
__all__ = [ "CrossValidStatCurator", "PlotCurator" ]

from RingerCore import Logger
from ROOT import TH1D, TH2F,TH1F,TF1,TGraph, TParameter
from ROOT import gROOT, kTRUE


class CrossValidStatCurator(Logger):
  
  def __init__(self, benchmark, summary):
    Logger.__init__(self)
    self._summary = summary
    self._benchmark = benchmark
    self._initBounds=None

  def neuronBounds(self):
    neuronBounds = [int(neuron.replace('config_','')) for neuron in self._summary.keys() if 'config_' in neuron]
    neuronBounds.sort()
    return neuronBounds

  def sortBounds(self, neuron):
    sortBounds = [int(sort.replace('sort_','')) for sort in self._summary['config_'+str(neuron).zfill(3)].keys() \
                  if 'sort_' in sort]
    sortBounds.sort()
    return sortBounds

  def setInitBounds( self, v ):
    self._initBounds=v

  def initBounds(self, neuron, sort):
    if self._initBounds:
      return self._initBounds
    else:
      def GetInits(sDict):
        initBounds = list(set([sDict['infoOpBest']['init'], sDict['infoOpWorst']['init'], \
                       sDict['infoTstBest']['init'], sDict['infoTstWorst']['init']]))
        initBounds.sort()
        return initBounds
      return GetInits(self._summary['config_'+str(neuron).zfill(3)]['sort_'+str(sort).zfill(3)])

  def benchmark(self):
    return self._benchmark

  def reference(self):
    return self._summary['rawBenchmark']['reference']

  def etBinIdx(self):
    return self._summary['etBinIdx']

  def etaBinIdx(self):
    return self._summary['etaBinIdx']

  def etBin(self):
    return self._summary['etBin']

  def etaBin(self):
    return self._summary['etaBin']

  def rawSummary(self):
    return self._summary

  def __getitem__(self, key):
    return self._summary[key]

  def thresholdType(self):
    return self._summary['infoOpBest']['cut']['class']


  

class PlotCurator( Logger ):
  
  gROOT.SetBatch(kTRUE)
  ### NOTE: All standard plots from the FastNet core
  _objects_v1  = [ 
                  (TParameter("double"),'mse_stop'            ),
                  (TParameter("double"),'sp_stop'             ),
                  (TParameter("double"),'det_stop'            ),
                  (TParameter("double"),'fa_stop'             ),
                  (TGraph,    'mse_trn'                       ), 
                  (TGraph,    'mse_val'                       ), 
                  (TGraph,    'mse_tst'                       ),
                  (TGraph,    'bestsp_point_sp_val'           ), 
                  (TGraph,    'bestsp_point_det_val'          ), 
                  (TGraph,    'bestsp_point_fa_val'           ),
                  (TGraph,    'bestsp_point_sp_tst'           ), 
                  (TGraph,    'bestsp_point_det_tst'          ), 
                  (TGraph,    'bestsp_point_fa_tst'           ),
                  (TGraph,    'det_point_sp_val'              ), 
                  (TGraph,    'det_point_det_val'             ), 
                  (TGraph,    'det_point_fa_val'              ),
                  (TGraph,    'det_point_sp_tst'              ), 
                  (TGraph,    'det_point_det_tst'             ), 
                  (TGraph,    'det_point_fa_tst'              ), 
                  (TGraph,    'fa_point_sp_val'               ), 
                  (TGraph,    'fa_point_det_val'              ), 
                  (TGraph,    'fa_point_fa_val'               ),
                  (TGraph,    'fa_point_sp_tst'               ), 
                  (TGraph,    'fa_point_det_tst'              ), 
                  (TGraph,    'fa_point_fa_tst'               ),  
                  (TGraph,    'roc_tst'                       ), 
                  (TGraph,    'roc_operation'                 ),
                  ]

  ### The Linear Pileup correction directory from the cross validation code
  _objects_v2 = [
                  (TGraph,  'signalCorr_{}_opData_graph'      ),
                  (TH1D,    'signalCorr_{}_opData_histEff'    ),
                  (TH1F,    'signalUncorr_{}_tstData_eff'     ),
                  (TH1F,    'signalUncorr_{}_opData_eff'      ),
                  (TH1F,    'backgroundUncorr_{}_tstData_eff' ),
                  (TH1F,    'backgroundUncorr_{}_opData_eff'  ),
                  (TH1F,    'signalCorr_{}_tstData_eff'       ),
                  (TH1F,    'backgroundCorr_{}_tstData_eff'   ),
                  (TH1F,    'signalOutputs_{}_tstData'        ),
                  (TH1F,    'backgroundOutputs_{}_tstData'    ),
                  (TH1F,    'signalOutputs_{}_opData'         ),
                  (TH1F,    'backgroundOutputs_{}_opData'     ),
                  (TH2F,    'signal2DCorr_{}_tstData'         ),
                  (TH2F,    'background2DCorr_{}_tstData'     ),
                  (TH2F,    'signal2DCorr_{}_opData'          ),
                  (TH2F,    'background2DCorr_{}_opData'      ),
                  (TF1,     'signalCorr_{}_opData_f1'         ),
                  (TF1,     'backgroundCorr_0_{}_opData_f1'   ),
                  (TF1,     'backgroundCorr_1_{}_opData_f1'   ),
                  (TF1,     'backgroundCorr_2_{}_opData_f1'   ),
                  (TF1,     'backgroundCorr_3_{}_opData_f1'   ),
                  (TF1,     'backgroundCorr_4_{}_opData_f1'   ),
                  (TF1,     'backgroundCorr_5_{}_opData_f1'   ),
                  (TF1,     'backgroundCorr_6_{}_opData_f1'   ),
                ]


  def __init__(self, rawFile, benchmark, neuron, sort, init, etBinIdx, etaBinIdx, **kw ):
    
    Logger.__init__( self, **kw ) 
    self._rawFile = rawFile 
    self._benchmark = benchmark
    self._reference = benchmark.split('_')[-1]
    self._neuron = neuron
    self._sort = sort
    self._init = init
    self._etBinIdx = etBinIdx
    self._etaBinIdx = etaBinIdx
    ### Hold all ROOT objects
    self._obj = {}
    ### Current frame version
    self._version =  2

  @property
  def sort(self):
    return self._sort
  
  @property
  def init(self):
    return self._init
  
  @property
  def neuron(self):
    return self._neuron

  @property   
  def version(self):
    return self._version


  def initialize(self):
    # Release the memory first
    self.finalize()  # Force memory release
    
    basepath = ("%s/config_%s/sort_%s/init_%s")%(self._benchmark, str(self._neuron).zfill(3),\
                                                 str(self._sort).zfill(3), str(self._init))

    for obj_v1 in self._objects_v1:
      self._logger.verbose("Alloc object to %s/%s", basepath, obj_v1[1])
      self.__retrieve_object(self._rawFile, basepath, obj_v1[1], obj_v1[0]() )
   

    try: ### Get all objects from the Linear Pileup correction file
      for obj_v2 in self._objects_v2:
        key = 'ref{}_etBin{}_etaBin{}_neuron{}_sort{}_init{}'.format(self._reference,\
            self._etBinIdx,self._etaBinIdx,self._neuron,self._sort, self._init)
        plotname = obj_v2[1].format(key)
        shortname = (obj_v2[1].format('')).replace('__','_') ### Fix the shortname
        self._logger.verbose("Alloc object to %s/%s", basepath, obj_v2[1])
        self.__retrieve_object(self._rawFile, basepath+'/linearcorr', plotname, obj_v2[0](), shortkey = shortname  )
    except:
      self._logger.warning("There is no Pileup Linear correction analysis in this root file.")
      self._version = 1
 

    # Decorate with multi stops curves
    keys = ['sp_val','det_val','fa_val','sp_tst','det_tst','fa_tst']
    for key in keys:
      if 'Pd' in self._benchmark: ### Get all curves from Detection stop
        self._obj[key] = self._obj['det_point_'+key]
      elif 'Pf' in self._benchmark: ### Get all curves from FA stop
        self._obj[key] = self._obj['fa_point_'+key]
      elif 'SP' in self._benchmark:### Get all curves from SP stop (default)
        self._obj[key] = self._obj['bestsp_point_'+key]
      else: ### No benchmark was fround
        self._logger.warning('Impossible to decorate with multi stops curves from %s',self._benchmark)
    

  def finalize(self):
    import gc
    for key, value in self._obj.iteritems():
      self._logger.verbose("Delete %s", key)
      del value
    self._obj={}
    gc.collect()


  def __retrieve_object(self, rawObj, path, key, obj, shortkey=None):
    rawObj.GetObject( path+'/'+key, obj)
    if shortkey:  self._obj[shortkey] = obj 
    else:  self._obj[key]=obj


  def __getitem__(self, key):
    return self._obj[key]


 
