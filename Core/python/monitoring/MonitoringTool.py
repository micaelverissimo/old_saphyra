
__all__ = ['MonitoringTool']

from RingerCore               import calcSP, save, load, Logger, mkdir_p, progressbar
from RingerCore               import retrieve_kw,checkForUnusedVars, NotSet
from RingerCore               import calcSP,LoggingLevel
from RingerCore.tex.TexAPI    import *
from RingerCore.tex.BeamerAPI import *
from pprint                   import pprint
import os
import numpy as np



class MonitoringTool( Logger ):
  
  #Init class
  def __init__(self, cvfile, rootfile, **kw):
    
    from ROOT import TFile, gROOT
    gROOT.ProcessLine("gErrorIgnoreLevel = kFatal;");
    #Set all global setting from ROOT style plot!
    Logger.__init__(self, **kw)
    #Hold all information abount the monitoring root file
    self._summaryObjs = list()
    try:#Protection
      self._logger.info('Reading root file (%s)...',rootfile)
      self._rootObj = TFile(rootfile, 'read')
    except RuntimeError:
      self._logger.fatal('Could not open root monitoring file.')
    from RingerCore import load
    try:#Protection
      self._logger.info('Reading summary file (%s)...', cvfile)
      cvObj = load(cvfile)
    except RuntimeError:
      self._logger.fatal('Could not open pickle summary file.')
    #Loop over benchmarks

    from TuningTools.monitoring.CrossValidStatDataCurator import CrossValidStatCurator
    for benchmark in cvObj.keys():
      #Must skip if ppchain collector
      if 'infoPPChain' in benchmark:  continue
      #Add summary information into MonTuningInfo helper class
      csummary = CrossValidStatCurator( benchmark, cvObj[benchmark] )
      self._summaryObjs.append( csummary ) 
      self._logger.info('Creating Summary for %s in [et=%d, eta=%d]', benchmark,csummary.etBinIdx(), csummary.etaBinIdx())
    #Loop over all benchmarks

    # Eta bin
    self._etaBinIdx = self._summaryObjs[0].etaBinIdx()
    # Et bin
    self._etBinIdx = self._summaryObjs[0].etBinIdx()
    # Eta bin
    self._etaBin = self._summaryObjs[0].etaBin()
    # Et bin
    self._etBin = self._summaryObjs[0].etBin()


  def etBinIdx(self):
    return self._etBinIdx

  def etaBinIdx(self):
    return self._etaBinIdx


  ### Use this method to decorate the cross validation summary
  def decorate( self, benchmark, csummary ):
    
    self._logger.info('Decorate %s summary...',benchmark)
    from TuningTools.monitoring.CrossValidStatDataCurator import PlotCurator
    wantedKeys = ['infoOpBest', 'infoOpWorst', 'infoTstBest','infoTstWorst']

    for neuron in csummary.neuronBounds():
      neuronStr = 'config_'+str(neuron).zfill(3)
      # decorate each neuron with the plot object frame
      for key in wantedKeys:
        info = csummary[neuronStr][key]
        #self._logger.verbose('Decorate %s in neuron %d',key,neuron)
        csummary[neuronStr][key]['plots'] = PlotCurator( self._rootObj, benchmark, info['neuron'], info['sort'],
                                                         info['init'], csummary.etBinIdx(), csummary.etaBinIdx(),
                                                         level = self._level)
  

      for sort in csummary.sortBounds(neuron):
        sortStr = 'sort_'+str(sort).zfill(3)
        # decorate each sort with the plot object frame
        for key in wantedKeys:
          #self._logger.verbose('Decorate %s in neuron %d and sort %d',key,neuron,sort)
          info = csummary[neuronStr][sortStr][key]
          csummary[neuronStr][sortStr][key]['plots'] = PlotCurator( self._rootObj, benchmark, info['neuron'], info['sort'],
                                                                    info['init'], csummary.etBinIdx(), csummary.etaBinIdx(),
                                                                    level = self._level)
        
    self._logger.debug('Decoration is completed!')



  #Main method to execute the monitoring 
  def __call__(self, **kw):
    
    from TuningTools.monitoring.CrossValidStatDrawer import *

    doOnlyTables = retrieve_kw( kw, 'doOnlyTables'  , False                       )
    doBeamer     = retrieve_kw( kw, 'doBeamer'      , True                        )
    toPDF        = retrieve_kw( kw, 'toPDF'         , True                        )
    dirname      = retrieve_kw( kw, 'dirname'       , 'report'                    )
    title        = retrieve_kw( kw, 'cvreport'      , 'Cross Validation Report'   )
    outname      = retrieve_kw( kw, 'outname'       , 'report'                    )
    checkForUnusedVars(kw)

    doBeamer=False

    ### Append binned information
    outname+=('_et%d_eta%d')%(self._etBinIdx,self._etaBinIdx) 
    basepath = os.getcwd()+'/'+dirname
    ret = {}

    #Loop over benchmarks
    for csummary in self._summaryObjs:
      # Retrieve benchmark name
      benchmarkName = csummary.benchmark()
      # Retrieve reference name
      reference = csummary.reference()
      # benchmark object
      cbenchmark = csummary['rawBenchmark']
      
      if csummary.etaBinIdx() != self._etaBinIdx or csummary.etBinIdx() != self._etBinIdx:
        self._logger.fatal("Benchmark dictionary is not compatible with the et/eta Indexs")
 
      self.decorate(benchmarkName, csummary) 
      from copy import copy
      # get the best config
      configOpBest  = 'config_'+str(csummary['infoOpBest']['neuron']).zfill(3)
      configTstBest = 'config_'+str(csummary['infoTstBest']['neuron']).zfill(3)
      # decorate the ret object
      ret[benchmarkName] = {}
      ret[benchmarkName]['infoOpBest']     = copy(csummary[configOpBest]['infoOpBest'])
      ret[benchmarkName]['infoTstBest']    = copy(csummary[configTstBest]['infoTstBest'])
      ret[benchmarkName]['summaryInfoOp']  = copy(csummary[configOpBest]['summaryInfoOp'])
      ret[benchmarkName]['summaryInfoTst'] = copy(csummary[configTstBest]['summaryInfoTst'])
      ret['etBin'] = self._etBin
      ret['etaBin'] = self._etaBin
      ret['etBinIdx'] = self._etBinIdx
      ret['etaBinIdx'] = self._etaBinIdx
      ret['rawBenchmark'] = copy(cbenchmark)

      ### Get sorts 
      oDict =  {  
                'allBestTstNeurons' : [],
                'allBestOpNeurons'  : [], 
               } 
      
      for neuron in csummary.neuronBounds():
        neuronStr = 'config_'+str(neuron).zfill(3)
        oDict['allBestTstNeurons'].append( csummary[neuronStr]['infoTstBest']['plots'] )
        oDict['allBestOpNeurons'].append( csummary[neuronStr]['infoOpBest']['plots'] )
        oDict['allBestTstSorts' ] = list()
        oDict['allBestOpSorts'  ] = list()
        oDict['allWorstTstSorts'] = list() 
        oDict['allWorstOpSorts' ] = list()
 
        for sort in csummary.sortBounds(neuron):
          sortStr = 'sort_'+str(sort).zfill(3)
          oDict['allBestTstSorts'].append( csummary[neuronStr][sortStr]['infoTstBest']['plots'] )
          oDict['allWorstTstSorts'].append( csummary[neuronStr][sortStr]['infoTstWorst']['plots'] )
          oDict['allBestOpSorts'].append( csummary[neuronStr][sortStr]['infoOpBest']['plots'] )
          oDict['allWorstOpSorts'].append( csummary[neuronStr][sortStr]['infoOpWorst']['plots'] )
          
        
        if doBeamer:
          self._logger.debug( "The plot frames were extracted.")
          ### Make all tuning curves
          path = basepath+ ('/figures_et{}_eta{}/{}/{}').format(self._etBinIdx,self._etaBinIdx,benchmarkName,neuronStr) 
          mkdir_p(path)
          TuningDrawer( path, neuron, oDict, csummary, logger=self._logger )
          
          ### make pileup correction plots
          if csummary.thresholdType() == "PileupLinearCorrectionThreshold":
            path = basepath+ ('/figures_et{}_eta{}/{}/{}/linearcorr').format(self._etBinIdx,self._etaBinIdx,benchmarkName,neuronStr) 
            mkdir_p(path)
            LinearPileupCorrectionDrawer( path, neuron, oDict, csummary, logger=self._logger )        

    # Start beamer presentation
    if doBeamer:  
      self.cvReport( basepath, csummary, title, outname, toPDF=toPDF, doOnlyTables=doOnlyTables )
    self._logger.info('Done! ')

    return ret
  #End of loop()



  ### Use this method to create the beamer binned report
  def cvReport( self, basepath, csummary, title, outname, toPDF=True, doOnlyTables=False):
    
    from copy import copy    
    # apply beamer
    with BeamerTexReportTemplate2( theme = 'Berlin'
                           , _toPDF = toPDF
                           , title = title
                           , outputFile = basepath+'/'+outname
                           , font = 'structurebold' ):

      for neuron in self._summaryObjs[0].neuronBounds():

        if not doOnlyTables:
          with BeamerSection( name = 'Config {}'.format(neuron) ):

            neuronstr = 'config_'+str(neuron).zfill(3)

            for csummary in self._summaryObjs:

              with BeamerSubSection (name= csummary.benchmark().replace('OperationPoint_','').replace('_','\_')):
                
                currentPath =  '{}/figures_et%d_eta%d/{}/{}/'.format(basepath,self._etBinIdx,self._etaBinIdx,csummary.benchmark(),neuronstr)
                
                with BeamerSubSubSection (name='Training Curves'):

                  paths = [ ('{}/roc_tst.pdf').format(currentPath),
                            ('{}/roc_operation.pdf').format(currentPath)]
                  BeamerMultiFigureSlide( title = 'ROC Curve'
                      , paths = paths 
                      , nDivWidth = 2  # x
                      , nDivHeight = 1 # y
                      , texts=None
                      , fortran = False
                      , usedHeight = 0.6  # altura
                      , usedWidth = 1.1 # lasgura
                      )

                ### Check if there is linear correction in this summary
                if csummary.thresholdType() == "PileupLinearCorrectionThreshold":
                  
                  with BeamerSubSubSection (name='Linear Pileup Correction'):
                    paths = [
                              '{}/linearcorr/signalCorr_tstData_eff.pdf'.format(currentPath),
                              '{}/linearcorr/backgroundCorr_tstData_eff.pdf'.format(currentPath),
                              '{}/linearcorr/signalComparison_opData_eff.pdf'.format(currentPath)
                            ]
                    BeamerMultiFigureSlide( title = 'Efficiency corrected for all tst sorts'
                        , paths = paths
                        , nDivWidth = 3 # x
                        , nDivHeight = 1 # y
                        , texts=None
                        , fortran = False
                        , usedHeight = 0.4  # altura
                        , usedWidth = .9 # lasgura
                        )


                    paths = [
                              '{}/linearcorr/signalCorr2D_opData.pdf'.format(currentPath),
                              '{}/linearcorr/backgroundCorr2D_opData.pdf'.format(currentPath),
                            ]
                    BeamerMultiFigureSlide( title = 'Pileup Correction for the best sort'
                        , paths = paths
                        , nDivWidth = 2 # x
                        , nDivHeight = 1 # y
                        , texts=None
                        , fortran = False
                        , usedHeight = 0.6  # altura
                        , usedWidth = 1.1 # lasgura
                        )


          with BeamerSubSection (name='Summary'):
            lines1 = []
            lines1 += [ HLine(_contextManaged = False) ]
            lines1 += [ HLine(_contextManaged = False) ]
            lines1 += [ TableLine(    columns = ['Criteria', 'Pd []','SP []', 'Fa []'], _contextManaged = False ) ]
            lines1 += [ HLine(_contextManaged = False) ]
            lines2 = copy(lines1)

            benchmarkValues = {}
            for csummary in self._summaryObjs:
              
              benchmarkValues[csummary['rawBenchmark']['reference']] = csummary['rawBenchmark']['refVal']*100
              info = csummary[neuronstr]['summaryInfoTst']

              # Crossvalidation values with error bar in tst
              c1 = '\\cellcolor[HTML]{9AFF99}' if 'Pd' in csummary.benchmark() else ''
              c2 = '\\cellcolor[HTML]{BBDAFF}' if 'Pf' in csummary.benchmark() else ''
              lines1 += [ TableLine(    columns = [csummary.benchmark().replace('OperationPoint_','').replace('_','\_'), 
                                                   (c1+'%1.2f $\\pm$%1.2f')% (info['detMean']*100,info['detStd']*100),
                                                   ('%1.2f $\\pm$%1.2f')   % (info['spMean' ]*100,info['spStd' ]*100),
                                                   (c2+'%1.2f $\\pm$%1.2f')% (info['faMean' ]*100,info['faStd' ]*100),
                                                   ],
                                    _contextManaged = False ) ]
              lines1 += [ HLine(_contextManaged = False) ]

              # Operation values
              info = csummary[neuronstr]['infoOpBest']
              lines2 += [ TableLine(    columns = [csummary.benchmark().replace('OperationPoint_','').replace('_','\_'), 
                                                   ('%1.2f')% (info['det']*100),
                                                   ('%1.2f')% (info['sp' ]*100),
                                                   ('%1.2f')% (info['fa' ]*100),
                                                   ],
                                    _contextManaged = False ) ]
              lines2 += [ HLine(_contextManaged = False) ]

            


            lines1 += [ TableLine(    columns = ['References', 
                                                 ('\\cellcolor[HTML]{9AFF99}%1.2f')% (benchmarkValues['Pd']),
                                                 ('%1.2f')% (benchmarkValues['SP']),
                                                 ('\\cellcolor[HTML]{BBDAFF}%1.2f')% (benchmarkValues['Pf']),
                                                 ],
                                  _contextManaged = False ) ]
            lines1 += [ HLine(_contextManaged = False) ]

            with BeamerSlide( title = "Crossvalidation table ("+str(neuron)+")"  ):
              
              with Table( caption = 'Cross validation efficiencies for validation set.') as table:
                with ResizeBox( size =  1.) as rb:
                  with Tabular( columns = 'l' + 'c' * 4) as tabular:
                    tabular = tabular
                    for line in lines1:
                      if isinstance(line, TableLine):
                        tabular += line
                      else:
                        TableLine(line, rounding = None)
 
              with Table( caption = 'Operation efficiencies for the best model.') as table:
                with ResizeBox( size =  0.7) as rb:
                  with Tabular( columns = 'l' + 'c' * 4) as tabular:
                    tabular = tabular
                    for line in lines2:
                      if isinstance(line, TableLine):
                        tabular += line
                      else:
                        TableLine(line, rounding = None)
 



  @classmethod
  def ttReport( cls, inputfile,  dataLocation, title=None, outname=None, toPDF=True, ):

    outname = outname if outname else 'tuning_report'
    title = title if title else 'Tuning Report'

    ### retrieve all summary files
    from copy import copy
    from RingerCore import load,save
    csummary = load(inputfile)

    if dataLocation:
      rawDataArchieve = load(dataLocation)
      if type(rawDataArchieve) is list:  
        dataEntries=rawDataArchieve
      else: 
        from TuningTools.CreateData import TuningDataArchieve
        isEtDependent, isEtaDependent, nEtBins, nEtaBins, tdVersion = \
            TuningDataArchieve.load(dataLocation, retrieveBinsInfo=True, retrieveVersion=True)
        dataEntries = [[None for _ in range(nEtaBins) ] for __ in range(nEtBins)]

        for etBinIdx in range(nEtBins):
          for etaBinIdx in range(nEtaBins):
            tdArchieve = TuningDataArchieve.load(dataLocation, etBinIdx = etBinIdx if isEtDependent else None,
                                     etaBinIdx = etaBinIdx if isEtaDependent else None,
                                     loadEfficiencies = False,
                                     loadCrossEfficiencies = False
                                     )
            dataEntries[etBinIdx][etaBinIdx] = (tdArchieve.signalPatterns.shape[0], tdArchieve.backgroundPatterns.shape[0] )

    #save( dataEntries, 'data_entries')
    
    ### retrieve et/eta bins from the summary
    etbins = []; etabins = []
    for idx, c in enumerate(csummary[0]):  
      if idx > 0:  etabins.append( round(c['etaBin'][1],2) )
      else:
        etabins.extend( [round(c['etaBin'][0],2), round(c['etaBin'][1],2)] )
    
    for idx, c in enumerate(csummary):
      if idx > 0:  etbins.append( round(c[0]['etBin'][1],2) )
      else:
        etbins.extend( [round(c[0]['etBin'][0],2), round(c[0]['etBin'][1],2)] )
 
    ### Make Latex str et/eta labels
    etbins_str = []; etabins_str=[]
    for etBinIdx in range( len(etbins)-1 ):
      etbin = (etbins[etBinIdx], etbins[etBinIdx+1])
      if etbin[1] > 100 :
        etbins_str.append( r'$E_{T}\text{[GeV]} > %d$' % etbin[0])
      else:
        etbins_str.append(  r'$%d < E_{T} \text{[Gev]}<%d$'%etbin )
 
    for etaBinIdx in range( len(etabins)-1 ):
      etabin = (etabins[etaBinIdx], etabins[etaBinIdx+1])
      etabins_str.append( r'$%.2f<\eta<%.2f$'%etabin )

    ### Get the benchmark names
    from pprint import pprint
    benchmarks=[]
    for key in csummary[0][0].keys():
      if 'OperationPoint' in key:  benchmarks.append(key)

    # apply beamer
    with BeamerTexReportTemplate1( theme = 'Berlin'
                           , _toPDF = toPDF
                           , title = title
                           , outputFile = outname
                           , font = 'structurebold' ):

      gCounts = {}

      for benchmark in benchmarks:
        
        colorPD = '\\cellcolor[HTML]{9AFF99}' if 'Pd' in benchmark else ''
        colorPF = '\\cellcolor[HTML]{9AFF99}' if 'Pf' in benchmark else ''
        colorSP = '\\cellcolor[HTML]{9AFF99}' if 'SP' in benchmark else ''
 
        ### Prepare tables
        lines1 = []
        lines1 += [ HLine(_contextManaged = False) ]
        lines1 += [ HLine(_contextManaged = False) ]
        lines1 += [ TableLine( columns = ['','kinematic region'] + reduce(lambda x,y: x+y,[['',s,''] for s in etbins_str]), _contextManaged = False ) ]
        lines1 += [ HLine(_contextManaged = False) ]
        lines1 += [ TableLine( columns = ['Det. Region','Type'] + reduce(lambda x,y: x+y,[[colorPD+r'$P_{D}[\%]$',colorSP+r'$SP[\%]$',colorPF+r'$P_{F}[\%]$'] \
                                                                         for _ in etbins_str]), _contextManaged = False ) ]
        lines1 += [ HLine(_contextManaged = False) ]


        lines2 = []
        lines2 += [ HLine(_contextManaged = False) ]
        lines2 += [ HLine(_contextManaged = False) ]
        lines2 += [ TableLine( columns = [''] + [s for s in etabins_str], _contextManaged = False ) ]
        lines2 += [ HLine(_contextManaged = False) ]

        s=len(csummary[0][0][benchmark]['summaryInfoOp']['det'])
        ### Use this to compute the final efficiency
        gCounts[benchmark]=  {

                                    'sgnRef':{'total':0,'passed':0,'eff':0}, 
                                    'bkgRef':{'total':0,'passed':0,'eff':0},
                                    'sgn':{'total':[0 for _ in range(s)],'passed':[0 for _ in range(s)]}, 
                                    'bkg':{'total':[0 for _ in range(s)],'passed':[0 for _ in range(s)]}, 
                                    'sgnOp':{'total':0,'passed':0,'eff':0}, 
                                    'bkgOp':{'total':0,'passed':0,'eff':0},
                                    }

        for etaBinIdx in range( len(etabins)-1 ):

          valuesCV = []; valuesREF = []; valuesBest = []
          
          for etBinIdx in range( len(etbins)-1 ):
            
            ### Get all values needed
            det    = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['detMean']*100
            fa     = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['faMean']*100
            sp     = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['spMean']*100
            opdet  = csummary[etBinIdx][etaBinIdx][benchmark]['infoOpBest']['det']*100
            opfa   = csummary[etBinIdx][etaBinIdx][benchmark]['infoOpBest']['fa']*100
            opsp   = csummary[etBinIdx][etaBinIdx][benchmark]['infoOpBest']['sp']*100
            detstd = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['detStd']*100
            fastd  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['faStd']*100
            spstd  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['spStd']*100
            refdet = csummary[etBinIdx][etaBinIdx]['rawBenchmark']['signalEfficiency']['efficiency']
            reffa  = csummary[etBinIdx][etaBinIdx]['rawBenchmark']['backgroundEfficiency']['efficiency']
            refsp  = calcSP( csummary[etBinIdx][etaBinIdx]['rawBenchmark']['signalEfficiency']['efficiency'],
                             100-csummary[etBinIdx][etaBinIdx]['rawBenchmark']['backgroundEfficiency']['efficiency']) 
            
            
            ### Make general efficiencies
            sgnTotal = dataEntries[etBinIdx][etaBinIdx][0]
            bkgTotal = dataEntries[etBinIdx][etaBinIdx][1]
            detList  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['det']
            faList   = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['fa']
            
            ### Update all counts for each sort
            for idx in range(len(detList)):
              gCounts[benchmark]['sgn']['total'][idx] += sgnTotal
              gCounts[benchmark]['sgn']['passed'][idx]+= int(sgnTotal*(detList[idx]))
              gCounts[benchmark]['bkg']['total'][idx] += bkgTotal
              gCounts[benchmark]['bkg']['passed'][idx]+= int(bkgTotal*(faList[idx]))
 
            ### Update all counts for the operation network
            gCounts[benchmark]['sgnOp']['total'] += sgnTotal
            gCounts[benchmark]['sgnOp']['passed']+= int(sgnTotal*(opdet/100.))
            gCounts[benchmark]['bkgOp']['total'] += bkgTotal
            gCounts[benchmark]['bkgOp']['passed']+= int(bkgTotal*(opfa/100.))
            
            ### Update all counts for the reference
            gCounts[benchmark]['sgnRef']['total'] += sgnTotal
            gCounts[benchmark]['sgnRef']['passed']+= int(sgnTotal*(refdet/100.))
            gCounts[benchmark]['bkgRef']['total'] += bkgTotal
            gCounts[benchmark]['bkgRef']['passed']+= int(bkgTotal*(reffa/100.))

            ### Append values to the table
            valuesCV   += [ colorPD+('%1.2f$\pm$%1.2f')%(det,detstd),colorSP+('%1.2f$\pm$%1.2f')%(sp,spstd),colorPF+('%1.2f$\pm$%1.2f')%(fa,fastd),    ]
            valuesREF  += [ colorPD+('%1.2f')%(refdet), colorSP+('%1.2f')%(refsp), colorPF+('%1.2f')%(reffa)]
            valuesBest += [ colorPD+('%1.2f')%(opdet), colorSP+('%1.2f')%(opsp), colorPF+('%1.2f')%(opfa)]
            
         
          ### Make summary table
          lines1 += [ TableLine( columns = ['\multirow{3}{*}{'+etabins_str[etaBinIdx]+'}', 'CrossValidation'] + valuesCV   , _contextManaged = False ) ]
          lines1 += [ TableLine( columns = ['','Reference']                          + valuesREF  , _contextManaged = False ) ]
          lines1 += [ TableLine( columns = ['','Operation']                          + valuesBest , _contextManaged = False ) ]
          lines1 += [ HLine(_contextManaged = False) ]
         
			
        lines1 += [ HLine(_contextManaged = False) ]


        try:
          if csummary[0][0][benchmark]['infoOpBest']['cut']['class'] == "PileupLinearCorrectionThreshold":
            ### Create the Pileup reach table
            cutReach=[]
            for etBinIdx in range( len(etbins)-1 ):
              #### Make cut reach lines	
              margins = csummary[etBinIdx][0][benchmark]['summaryInfoOp']['margins']
              cutReach = []
              for idx, value in enumerate(margins):
                cutReachLine=[]
                for etaBinIdx in range( len(etabins)-1 ):
                	cutmean = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['cutReachMean'][idx]
                	cutstd  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['cutReachStd'][idx]
                	if idx>0: 
                		cutReachLine.append('%1.2f$\pm$%1.2f (%d$\%%$)'%(cutmean,cutstd,int(value*100)))
                	else:
                		cutReachLine.append('\\cellcolor[HTML]{9AFF99}%1.2f$\pm$%1.2f'%(cutmean,cutstd))
                cutReach.append( cutReachLine )
              ### Make Margins
              for idx, cutReachLine in enumerate(cutReach):
            	  if idx>0:
            		  lines2 += [ TableLine( columns = [''] + cutReachLine   , _contextManaged = False ) ]
            	  else:
            		  lines2 += [ TableLine( columns = [  '\multirow{%d}{*}{'%(len(margins))+etbins_str[etBinIdx]+'}'] + cutReachLine   , _contextManaged = False ) ]
              lines2 += [ HLine(_contextManaged = False) ]
            lines2 += [ HLine(_contextManaged = False) ]
        except:
          pass
	


        ### Calculate the final efficiencies
        lines3 = []
        lines3 += [ HLine(_contextManaged = False) ]
        lines3 += [ HLine(_contextManaged = False) ]
        lines3 += [ TableLine( columns = ['',colorPD+r'$P_{D}[\%]$',colorSP+r'$SP[\%]$',colorPF+r'$F_{a}[\%]$'], _contextManaged = False ) ]
        lines3 += [ HLine(_contextManaged = False) ]

        detList = [];  faList = [];  spList = []
        obj1 = gCounts[benchmark]['sgn']; obj2 = gCounts[benchmark]['bkg']
        for idx in range(len(obj1['total'])):
          detList.append( (obj1['passed'][idx]/float(obj1['total'][idx]))*100 )
          faList.append( (obj2['passed'][idx]/float(obj2['total'][idx]))*100 )
          spList.append( calcSP( detList[-1], 100-faList[-1] ) ) 
        
        lines3 += [ TableLine( columns = ['CrossValidation', colorPD+'%1.2f$\pm$%1.2f'%(np.mean(detList), np.std(detList)),
                                                             colorSP+'%1.2f$\pm$%1.2f'%(np.mean(spList), np.std(spList)),
                                                             colorPF+'%1.2f$\pm$%1.2f'%(np.mean(faList), np.std(faList)),
                                                             ]   , _contextManaged = False ) ]

        obj1 = gCounts[benchmark]['sgnRef']; obj2 = gCounts[benchmark]['bkgRef']
        refValues = [ colorPD+'%1.2f'%((obj1['passed']/float(obj1['total']))*100),
                      colorSP+'%1.2f'%(calcSP(obj1['passed']/float(obj1['total']), 1-obj2['passed']/float(obj2['total']))*100),
                      colorPF+'%1.2f'%((obj2['passed']/float(obj2['total']))*100)]

        lines3 += [ TableLine( columns = ['Reference']+refValues   , _contextManaged = False ) ]

        obj1 = gCounts[benchmark]['sgnOp']; obj2 = gCounts[benchmark]['bkgOp']
        refValues = [ colorPD+'%1.2f'% ((obj1['passed']/float(obj1['total']))*100),
                      colorSP+'%1.2f'%(calcSP(obj1['passed']/float(obj1['total']), 1-obj2['passed']/float(obj2['total']))*100),
                      colorPF+'%1.2f'%((obj2['passed']/float(obj2['total']))*100)]
        lines3 += [ TableLine( columns = ['Operation']+refValues   , _contextManaged = False ) ]

        lines3 += [ HLine(_contextManaged = False) ]
        lines3 += [ HLine(_contextManaged = False) ]


       
        with BeamerSection( name = benchmark.replace('OperationPoint_','').replace('_','\_') ):
          with BeamerSlide( title = "The Cross Validation Efficiency Values"  ):          
            with Table( caption = 'The $P_{d}$, $F_{a}$ and $SP $ values for each phase space.') as table:
              with ResizeBox( size = 1. ) as rb:
                with Tabular( columns = '|lc|' + 'ccc|' * len(etbins_str) ) as tabular:
                  tabular = tabular
                  for line in lines1:
                    if isinstance(line, TableLine):
                      tabular += line
                    else:
                      TableLine(line, rounding = None)

          try:          
            if csummary[0][0][benchmark]['infoOpBest']['cut']['class'] == "PileupLinearCorrectionThreshold":
              with BeamerSlide( title = "The Pileup Reach For Each Space Phase"  ):          
                with Table( caption = 'The pileup reach values for all phase space regions. Values in parentheses means a percentage of background accepted.') as table:
                  with ResizeBox( size = 1 ) as rb:
                    with Tabular( columns = 'l' + 'c' * len(etabins_str) ) as tabular:
                      tabular = tabular
                      for line in lines2:
                        if isinstance(line, TableLine):
                          tabular += line
                        else:
                          TableLine(line, rounding = None)
          except:
            pass

          with BeamerSlide( title = "The General Efficiency"  ):          
            with Table( caption = 'The general efficiency for the cross validation method, reference and the best tuning.') as table:
              with ResizeBox( size = 0.7 ) as rb:
                with Tabular( columns = 'l' + 'c' * 3 ) as tabular:
                  tabular = tabular
                  for line in lines3:
                    if isinstance(line, TableLine):
                      tabular += line
                    else:
                      TableLine(line, rounding = None)




  @classmethod
  def compareTTsReport( cls, summaryNames, inputFiles,  dataLocation, title=None, outname=None, toPDF=True, 
                        level=LoggingLevel.INFO):

    outname = outname if outname else 'tuning_report'
    title = title if title else 'Tuning Report'

    logger = Logger.getModuleLogger("CompareTTsReport", logDefaultLevel = level )

    ### retrieve all summary files
    from copy import copy
    from RingerCore import load
    from pprint import pprint

    if dataLocation:

      rawDataArchieve = load(dataLocation)
      if type(rawDataArchieve) is list:  
        dataEntries=rawDataArchieve
        pprint(dataEntries)
        npSgn=np.array(copy(dataEntries)); npBkg=np.array(copy(dataEntries))  
        for etBinIdx in range(len(dataEntries)):
          for etaBinIdx in range(len(dataEntries[0])):
            npSgn[etBinIdx][etaBinIdx]=npSgn[etBinIdx][etaBinIdx][0]
            npBkg[etBinIdx][etaBinIdx]=npBkg[etBinIdx][etaBinIdx][1]
      else:
        logger.info('Reading data quantities from %s',dataLocation)
        from TuningTools.CreateData import TuningDataArchieve
        isEtDependent, isEtaDependent, nEtBins, nEtaBins, tdVersion = \
            TuningDataArchieve.load(dataLocation, retrieveBinsInfo=True, retrieveVersion=True)
        dataEntries = [[None for _ in range(nEtaBins) ] for __ in range(nEtBins)]
        npSgn=np.array(copy(dataEntries)); npBkg=np.array(copy(dataEntries)) 
        for etBinIdx in range(nEtBins):
          for etaBinIdx in range(nEtaBins):
            logger.debug('Extracting event number information from [et=%d,eta=%d]',etBinIdx,etaBinIdx)
            tdArchieve = TuningDataArchieve.load(dataLocation, etBinIdx = etBinIdx if isEtDependent else None,
                                     etaBinIdx = etaBinIdx if isEtaDependent else None,
                                     loadEfficiencies = False,
                                     loadCrossEfficiencies = False
                                     )
            dataEntries[etBinIdx][etaBinIdx] = (tdArchieve.signalPatterns.shape[0], tdArchieve.backgroundPatterns.shape[0] )
            npSgn[etBinIdx][etaBinIdx]=dataEntries[etBinIdx][etaBinIdx][0]
            npBkg[etBinIdx][etaBinIdx]=dataEntries[etBinIdx][etaBinIdx][1]


    csummaryList = []
    ### Loading all summaries
    logger.info('Reading all summaries...')
    for f in inputFiles:
      logger.debug('Reading %s...',f)
      try:
        csummary = load(f)
        csummaryList.append(csummary)
      except:
        logger.fatal('Impossible to read %s.',f)



    ### Get the et/eta from the first file. All files must be have the same et/eta grid
    ### retrieve et/eta bins from the summary
    csummary=csummaryList[0]
    etbins = []; etabins = []
    for idx, c in enumerate(csummary[0]):  
      if idx > 0:  etabins.append( round(c['etaBin'][1],2) )
      else:
        etabins.extend( [round(c['etaBin'][0],2), round(c['etaBin'][1],2)] )
    
    for idx, c in enumerate(csummary):
      if idx > 0:  etbins.append( round(c[0]['etBin'][1],2) )
      else:
        etbins.extend( [round(c[0]['etBin'][0],2), round(c[0]['etBin'][1],2)] )
 
    ### Make Latex str et/eta labels
    etbins_str = []; etabins_str=[]
    for etBinIdx in range( len(etbins)-1 ):
      etbin = (etbins[etBinIdx], etbins[etBinIdx+1])
      if etbin[1] > 100 :
        etbins_str.append( r'$E_{T}\text{[GeV]} > %d$' % etbin[0])
      else:
        etbins_str.append(  r'$%d < E_{T} \text{[Gev]}<%d$'%etbin )
 
    for etaBinIdx in range( len(etabins)-1 ):
      etabin = (etabins[etaBinIdx], etabins[etaBinIdx+1])
      etabins_str.append( r'$%.2f<\eta<%.2f$'%etabin )

    logger.info('Et lenght is : %d',len(etbins))
    logger.info('Eta lenght is: %d',len(etabins))

    ### Get the benchmark name
    benchmarks=[]
    for key in csummary[0][0].keys():
      if 'OperationPoint' in key:  benchmarks.append(key)

    #if dataLocation:
    #  from TuningTools import CreateData
    #  CreateData.plotNSamples(npSgn, npBkg, np.array(etbins), np.array(etabins), outname='nPatterns.pdf')
 

    ### Create general counts for each summary
    from copy import copy
    gCounts = [{} for _ in range(len(csummaryList))]
    for idx, csummary in enumerate(csummaryList):
      for benchmark in benchmarks: 
        s=len(csummary[0][0][benchmark]['summaryInfoOp']['det'])
        ### Use this to compute the final efficiency
        counts = {
                 'sgnRef':{'total':0,'passed':0,'eff':0}, 
                 'bkgRef':{'total':0,'passed':0,'eff':0},
                 'sgn':{'total':[0 for _ in range(s)],'passed':[0 for _ in range(s)]}, 
                 'bkg':{'total':[0 for _ in range(s)],'passed':[0 for _ in range(s)]}, 
                 'sgnOp':{'total':0,'passed':0,'eff':0}, 
                 'bkgOp':{'total':0,'passed':0,'eff':0},
                 }
        gCounts[idx][benchmark] = copy(counts)

    # apply beamer
    with BeamerTexReportTemplate1( theme = 'Berlin'
                           , _toPDF = toPDF
                           , title = title
                           , outputFile = outname
                           , font = 'structurebold' ):

      for benchmark in benchmarks:
        
        colorPD = '\\cellcolor[HTML]{9AFF99}' if 'Pd' in benchmark else ''
        colorPF = '\\cellcolor[HTML]{9AFF99}' if 'Pf' in benchmark else ''
        colorSP = '\\cellcolor[HTML]{9AFF99}' if 'SP' in benchmark else ''
 
        ### Prepare tables
        lines1 = []
        lines1 += [ HLine(_contextManaged = False) ]
        lines1 += [ HLine(_contextManaged = False) ]
        lines1 += [ TableLine( columns = ['','','kinematic region'] + reduce(lambda x,y: x+y,[['',s,''] for s in etbins_str]), _contextManaged = False ) ]
        lines1 += [ HLine(_contextManaged = False) ]
        lines1 += [ TableLine( columns = ['Det. Region','Method','Type'] + reduce(lambda x,y: x+y,[[colorPD+r'$P_{D}[\%]$',colorSP+r'$SP[\%]$',colorPF+r'$P_{F}[\%]$'] \
                                                          for _ in etbins_str]), _contextManaged = False ) ]
        lines1 += [ HLine(_contextManaged = False) ]



        for etaBinIdx in range( len(etabins)-1 ):
          
          for idx, csummary in enumerate(csummaryList):
          
            valuesCV = []; valuesREF = []; valuesBest = []
            
            for etBinIdx in range( len(etbins)-1 ):
              
              ### Get all values needed
              det    = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['detMean']*100
              fa     = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['faMean']*100
              sp     = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['spMean']*100
              opdet  = csummary[etBinIdx][etaBinIdx][benchmark]['infoOpBest']['det']*100
              opfa   = csummary[etBinIdx][etaBinIdx][benchmark]['infoOpBest']['fa']*100
              opsp   = csummary[etBinIdx][etaBinIdx][benchmark]['infoOpBest']['sp']*100
              detstd = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['detStd']*100
              fastd  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['faStd']*100
              spstd  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['spStd']*100
              refdet = csummary[etBinIdx][etaBinIdx]['rawBenchmark']['signalEfficiency']['efficiency']
              reffa  = csummary[etBinIdx][etaBinIdx]['rawBenchmark']['backgroundEfficiency']['efficiency']
              refsp  = calcSP( csummary[etBinIdx][etaBinIdx]['rawBenchmark']['signalEfficiency']['efficiency'],
                               100-csummary[etBinIdx][etaBinIdx]['rawBenchmark']['backgroundEfficiency']['efficiency']) 
              
              ### Make general efficiencies
              sgnTotal = dataEntries[etBinIdx][etaBinIdx][0]
              bkgTotal = dataEntries[etBinIdx][etaBinIdx][1]
              detList  = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['det']
              faList   = csummary[etBinIdx][etaBinIdx][benchmark]['summaryInfoOp']['fa']
              
              ### Update all counts for each sort
              for jdx in range(len(detList)):
                gCounts[idx][benchmark]['sgn']['total'][jdx] += sgnTotal
                gCounts[idx][benchmark]['sgn']['passed'][jdx]+= int(sgnTotal*(detList[jdx]))
                gCounts[idx][benchmark]['bkg']['total'][jdx] += bkgTotal
                gCounts[idx][benchmark]['bkg']['passed'][jdx]+= int(bkgTotal*(faList[jdx]))
 
              ### Update all counts for the operation network
              gCounts[idx][benchmark]['sgnOp']['total'] += sgnTotal
              gCounts[idx][benchmark]['sgnOp']['passed']+= int(sgnTotal*(opdet/100.))
              gCounts[idx][benchmark]['bkgOp']['total'] += bkgTotal
              gCounts[idx][benchmark]['bkgOp']['passed']+= int(bkgTotal*(opfa/100.))
             
              ### Update all counts for the reference
              gCounts[idx][benchmark]['sgnRef']['total'] += sgnTotal
              gCounts[idx][benchmark]['sgnRef']['passed']+= int(sgnTotal*(refdet/100.))
              gCounts[idx][benchmark]['bkgRef']['total'] += bkgTotal
              gCounts[idx][benchmark]['bkgRef']['passed']+= int(bkgTotal*(reffa/100.))

              ### Append values to the table
              valuesCV   += [ colorPD+('%1.2f$\pm$%1.2f')%(det,detstd),colorSP+('%1.2f$\pm$%1.2f')%(sp,spstd),colorPF+('%1.2f$\pm$%1.2f')%(fa,fastd),    ]
              valuesREF  += [ colorPD+('%1.2f')%(refdet), colorSP+('%1.2f')%(refsp), colorPF+('%1.2f')%(reffa)]
            
         
            ### Make summary table
            if idx > 0:
              lines1 += [ TableLine( columns = [''                    , summaryNames[idx+1], 'Cross Validation'] + valuesCV   , _contextManaged = False ) ]
            else:
              lines1 += [ TableLine( columns = ['\multirow{%d}{*}{'%(len(csummaryList)+1)+etabins_str[etaBinIdx]+'}',summaryNames[idx], 'Reference'] + valuesREF   , 
                                    _contextManaged = False ) ]
              lines1 += [ TableLine( columns = [''                    , summaryNames[idx+1], 'Cross Validation'] + valuesCV    , _contextManaged = False ) ]

          lines1 += [ HLine(_contextManaged = False) ]
         
			
        lines1 += [ HLine(_contextManaged = False) ]





        lines2 = []
        lines2 += [ HLine(_contextManaged = False) ]
        lines2 += [ HLine(_contextManaged = False) ]
        lines2 += [ TableLine( columns = ['Method','Type',colorPD+r'$P_{D}[\%]$',colorSP+r'$SP[\%]$',colorPF+r'$F_{a}[\%]$'], _contextManaged = False ) ]
        lines2 += [ HLine(_contextManaged = False) ]
        obj1 = gCounts[0][benchmark]['sgnRef']; obj2 = gCounts[0][benchmark]['bkgRef']
          
        refValues = [   colorPD+'%1.2f'%((obj1['passed']/float(obj1['total']))*100),
                        colorSP+'%1.2f'%(calcSP(obj1['passed']/float(obj1['total']), 1-obj2['passed']/float(obj2['total']))*100),
                        colorPF+'%1.2f'%((obj2['passed']/float(obj2['total']))*100)]
        lines2 += [ TableLine( columns = [summaryNames[0],'Reference']+refValues   , _contextManaged = False ) ]


        for idx, gcount in enumerate(gCounts):
          detList = [];  faList = [];  spList = []
          obj1 = gcount[benchmark]['sgn']; obj2 = gcount[benchmark]['bkg']
          for jdx in range(len(obj1['total'])):
            detList.append( (obj1['passed'][jdx]/float(obj1['total'][jdx]))*100 )
            faList.append( (obj2['passed'][idx]/float(obj2['total'][jdx]))*100 )
            spList.append( calcSP( detList[-1], 100-faList[-1] ) ) 
          

          lines2 += [ TableLine( columns = [summaryNames[idx+1], 'CrossValidation', colorPD+'%1.2f$\pm$%1.2f'%(np.mean(detList), np.std(detList)),
                                                                                   colorSP+'%1.2f$\pm$%1.2f'%(np.mean(spList), np.std(spList)),
                                                                                   colorPF+'%1.2f$\pm$%1.2f'%(np.mean(faList), np.std(faList)),
                                                                                  ]   , _contextManaged = False ) ]


        lines2 += [ HLine(_contextManaged = False) ]
        lines2 += [ HLine(_contextManaged = False) ]



        with BeamerSection( name = benchmark.replace('OperationPoint_','').replace('_','\_') ):
          with BeamerSlide( title = "The Cross Validation Efficiency Values For All Methods"  ):          
            with Table( caption = 'The $P_{d}$, $F_{a}$ and $SP $ values for each phase space for each method.') as table:
              with ResizeBox( size = 1. ) as rb:
                with Tabular( columns = '|lcc|' + 'ccc|' * len(etbins_str) ) as tabular:
                  tabular = tabular
                  for line in lines1:
                    if isinstance(line, TableLine):
                      tabular += line
                    else:
                      TableLine(line, rounding = None)

          
          with BeamerSlide( title = "The General Efficiency"  ):          
            with Table( caption = 'The general efficiency for the cross validation method for each method.') as table:
              with ResizeBox( size = 0.7 ) as rb:
                with Tabular( columns = 'lc' + 'c' * 3 ) as tabular:
                  tabular = tabular
                  for line in lines2:
                    if isinstance(line, TableLine):
                      tabular += line
                    else:
                      TableLine(line, rounding = None)





 

