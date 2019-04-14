__all__ = ['makeSummaryMonSlides']

from RingerCore.tex.TexAPI import *
from RingerCore.tex.BeamerAPI import *
from RingerCore import load

def calcPerformance(anex,netBin,netaBin):
  from RingerCore import calcSP
  import numpy as np
  signalPassRef=0
  signalPassBest=0
  signalTotal=0
  backgroundPassRef=0
  backgroundPassBest=0
  backgroundTotal=0

  backgroundPassTuning = {k:0 for k in anex[0][0]['sortMaximuns'][0].keys()}
  signalPassTuning = dict(backgroundPassTuning)
  for et in xrange(netBin):
    for eta in xrange(netaBin):
      nsignal               = anex[et][eta]['nsignal']
      perf                  = anex[et][eta]['perf']
      nbackground           = anex[et][eta]['nbackground']
      for k in signalPassTuning.keys():
        signalPassTuning[k]     += anex[et][eta]['sortMaximuns'][0][k]*nsignal/10.0
        backgroundPassTuning[k] += anex[et][eta]['sortMaximuns'][1][k]*nbackground/10.0
      signalPassRef         += nsignal * perf['refBench']['det']/100.0
      signalPassBest        += nsignal * perf['bestNetBench']['det']/100.0 
      signalTotal           += nsignal 
      backgroundPassRef     += nbackground * perf['refBench']['fa']/100.0
      backgroundPassBest    += nbackground * perf['bestNetBench']['fa']/100
      backgroundTotal       += nbackground 
      #
    #
  pdArray = np.array(signalPassTuning.values())/(signalTotal/10.0)*100 
  pfArray = np.array(backgroundPassTuning.values())/(backgroundTotal/10.0)*100
  spList = [ calcSP(signalPassTuning[k]*100/(signalTotal/10.0), 100 - backgroundPassTuning[k]*100/(backgroundTotal/10.0)) 
              for k in signalPassTuning.keys()]
  spMeanTuning = np.mean(spList)
  spStdTuning = np.std(spList)

  pdMeanTuning = pdArray.mean()
  pdStdTuning  = pdArray.std()
  
  pfMeanTuning = pfArray.mean()
  pfStdTuning  = pfArray.std()

  pdBest = signalPassBest/float(signalTotal)*100
  pdRef  = signalPassRef/float(signalTotal)*100

  pfBest = backgroundPassBest/float(backgroundTotal)*100
  pfRef  = backgroundPassRef/float(backgroundTotal)*100

  spBest  = calcSP(pdBest, 100 - pfBest)
  spRef  = calcSP(pdRef, 100 - pfRef)

  return  { 'spTuning':spMeanTuning ,
         'spStdTuning':spStdTuning ,
         'pdTuning':pdMeanTuning ,
         'pdStdTuning':pdStdTuning  ,
         'pfTuning':pfMeanTuning ,
         'pfStdTuning':pfStdTuning  ,
         'pdBest':'%.2f'%(pdBest ),
         'pdRef':'%.2f'%(pdRef ),
         'pfBest':'%.2f'%(pfBest ),
         'pfRef':'%.2f'%(pfRef  ),
         'spBest':'%.2f'%(spBest),  
         'spRef':'%.2f'%(spRef),  
           }
                

  
     
def makeSummaryMonSlides(outputs,nbins,choicesfile):
  from scipy.io import loadmat
  
  f =  loadmat(choicesfile) 
  choices = dict()
  choices['Pd'] = f['choices']['Pd'][0][0]
  choices['Pf'] = f['choices']['Pf'][0][0]
  choices['SP'] = f['choices']['SP'][0][0]

  nbinchoices = 0
  for etchoices in choices['Pd']:
    nbinchoices += len(etchoices)
  if not nbins == nbinchoices:
    raise NameError('Choices Archieve Error')

  net = len(choices['Pd'])
  neta = len (choices['Pd'][0])
  unbinned = False
  if net == 1 and neta == 1:
    unbinned = True
  f = load('{}/anex.pic.gz'.format(outputs+'_et0_eta0'))
  benchmarkNames = f['perf'].keys()
   
  for benchmarkName in benchmarkNames:
    slideAnex = []
    for et in xrange(net):
      etlist = []
      for eta in xrange( neta):
        etaDict = dict()
        neuron = choices[benchmarkName.split('_')[-1]][et][eta]
        basepath=outputs
        basepath+=('_et%d_eta%d')%(et,eta)
        f =  load ('{}/anex.pic.gz'.format(basepath))
        etaDict['nsignal'] = f['nsignal']
        etaDict['nbackground'] = f['nbackground']

        etstr =  f['bounds']['etbinstr']
        etastr =  f['bounds']['etabinstr']
        perfs  = f['perf'][benchmarkName]

        refBench = perfs['config_'+str(neuron).zfill(3)].getRef()
        perfBench = perfs['config_'+str(neuron).zfill(3)].getPerf()
        bestNetBench = perfs['config_'+str(neuron).zfill(3)].rawOp()
        etaDict['sortMaximuns']= perfs['config_'+str(neuron).zfill(3)].getSortPerfs()

        detR = (refBench['det'])
        spR  = (refBench['sp'])
        faR  = (refBench['fa'])

        detRstr = r'{:.2f}'.format(detR)
        spRstr  = r'{:.2f}'.format(spR)
        faRstr  = r'{:.2f}'.format(faR)

        perf= dict()

        perf['refBench'] = dict()
        perf['refBench']['det'] = detR
        perf['refBench']['sp'] = spR
        perf['refBench']['fa'] = faR
       
        refBench = [detRstr,spRstr,faRstr]

        
        detP = (perfBench['detMean'],perfBench['detStd'])
        spP  = (perfBench['spMean'],perfBench['spStd'])
        faP  = (perfBench['faMean'],perfBench['faStd'])
        detPstr = r'%.2f$\pm$%.2f'%(detP)
        spPstr  = r'%.2f$\pm$%.2f'%(spP)
        faPstr  = r'%.2f$\pm$%.2f'%(faP)
        perf['perfBench'] = dict()
        perf['perfBench']['det'] = detP
        perf['perfBench']['sp'] = spP
        perf['perfBench']['fa'] = faP

        perfBench = [detPstr,spPstr,faPstr]


        detB = (bestNetBench['det']*100)
        spB  = (bestNetBench['sp']*100)
        faB  = (bestNetBench['fa']*100)
        
        detBstr = r'{:.2f}'.format(detB)
        spBstr  = r'{:.2f}'.format(spB)
        faBstr  = r'{:.2f}'.format(faB)

        perf['bestNetBench'] = dict()
        perf['bestNetBench']['det'] = detB
        perf['bestNetBench']['sp'] = spB
        perf['bestNetBench']['fa'] = faB

        bestNetBench = [ detBstr,spBstr,faBstr]
        perfs = [refBench,perfBench,bestNetBench]  
      
        graphSections = [
              'All Sorts(Validation)' ,
              'All ROC Sorts(Validation)',
              'All Sorts(Operation)' ,  
              'All ROC Sorts(Operation)',
              'Best Network',  
              'Best Operation Output',  
              ]

        figures = [
              '{}/figures/{}/neuron_{}/plot_{}_neuron_{}_sorts_val.pdf'.format(basepath,benchmarkName,neuron,benchmarkName,neuron),
              '{}/figures/{}/neuron_{}/plot_{}_neuron_{}_sorts_roc_tst.pdf'.format(basepath,benchmarkName,neuron,benchmarkName,neuron),
              '{}/figures/{}/neuron_{}/plot_{}_neuron_{}_sorts_op.pdf'.format(basepath,benchmarkName,neuron,benchmarkName,neuron)      ,  
              '{}/figures/{}/neuron_{}/plot_{}_neuron_{}_sorts_roc_op.pdf'.format(basepath,benchmarkName,neuron,benchmarkName,neuron),
              '{}/figures/{}/neuron_{}/plot_{}_neuron_{}_best_op.pdf'.format(basepath,benchmarkName,neuron,benchmarkName,neuron)       ,  
              '{}/figures/{}/neuron_{}/plot_{}_neuron_{}_best_op_output.pdf'.format(basepath,benchmarkName,neuron,benchmarkName,neuron),  
                 ]
        figuresDict= dict(zip(graphSections,figures))
        etaDict['neuron'] = neuron
        etaDict['figures'] = figuresDict
        etaDict['graphSections'] = graphSections
        etaDict['perfs'] = perfs 
        etaDict['perf'] = perf
        etaDict['etastr'] = etastr 
        etaDict['etstr'] = etstr 

        etlist.append(etaDict)
        # for eta
      slideAnex.append(etlist)
      #for et
    totalPerfs = calcPerformance(slideAnex,net,neta)
    


    with BeamerTexReportTemplate1( theme = 'Berlin'
                                 , _toPDF = True
                                 , title = benchmarkName
                                 , outputFile = benchmarkName
                                 , font = 'structurebold' ):
      with BeamerSection(name = 'Performance'):
        if not unbinned:
          l1 = ['']
         
          sideline =  '{|c|ccc|}'
      
          l1.extend([r'Pd(\%)',r'SP(\%)',r'PF(\%)'])
          bodylines = []
          la = [r'\hline'+'\n'+r'\text{CrossValidation}' ]
          lb = ['Reference']
          lc = [ 'bestNetBench']
          refBench =[totalPerfs['pdRef'],totalPerfs['spRef'],totalPerfs['pfRef']]
          bestNetBench = [totalPerfs['pdBest'],totalPerfs['spBest'],totalPerfs['pfBest']]

          detP = (totalPerfs['pdTuning'],totalPerfs['pdStdTuning'])
          spP  = (totalPerfs['spTuning'],totalPerfs['spStdTuning'])
          pfP  = (totalPerfs['pfTuning'],totalPerfs['pfStdTuning'])
          
          detPstr = r'%.2f$\pm$%.2f'%(detP)
          spPstr  = r'%.2f$\pm$%.2f'%(spP)
          pfPstr  = r'%.2f$\pm$%.2f'%(pfP)
          
          perfBench = [detPstr,spPstr,pfPstr]

          la.extend(perfBench)
          lb.extend(refBench)
          lc.extend(bestNetBench)
          bodylines.extend([la,lb,lc])
          linhas=[]
          linhas.append(l1)
          linhas.extend(bodylines)
          with BeamerSubSection(name= 'General Performance'):
            BeamerTableSlide(title =  'General Performance',
                           linhas = linhas,
                           sideline = sideline,
                           caption = 'Efficiences',
                           )

          l1 = ['','']
          l2 = ['','']
          sideline =  '{|c|c|'
          for et in xrange(net):
            sideline += 'ccc|'
            l1.extend(['',slideAnex[et][0]['etstr'],''])
            l2.extend([r'Pd(\%)',r'SP(\%)',r'PF(\%)'])
          sideline +='}'
          etlines = []
          for eta in xrange(neta):
            la = [r'\hline'+ slideAnex[0][eta]['etastr'],'CrossValidation' ]
            lb = [r'','Reference']
            lc = [r'', 'bestNetBench']
            for et in xrange(net):
              prfs = slideAnex [et][eta]['perfs']
              refBench = prfs[0]
              perfBench = prfs[1]
              bestNetBench = prfs[2]

              la.extend(perfBench)
              lb.extend(refBench)
              lc.extend(bestNetBench)
            etlines.extend([la,lb,lc])
          linhas=[]
          linhas.append(l1)
          linhas.append(l2)
          linhas.extend(etlines)
          with BeamerSubSection(name= 'All Bins Performance'):
            BeamerTableSlide(title =  'All Bins Performance',
                           linhas = linhas,
                           sideline = sideline,
                           caption = 'Efficiences',
                           )
            

        for et in xrange(net):
          l1 = ['','']
          l2 = ['','']
          sideline =  '{|c|c|ccc|}'
          l1.extend(['',slideAnex[et][0]['etstr'],''])
          l2.extend([r'Pd(\%)',r'SP(\%)',r'PF(\%)'])
          etlines = []
          for eta in xrange(neta):
            if unbinned:
              la = [r'\hline','CrossValidation' ]
            else:
              la = [r'\hline'+ slideAnex[0][eta]['etastr'],'CrossValidation' ]
            lb = [r'Neuron','Reference']
            lc = [r'', 'bestNetBench']
            neuron = slideAnex [et][eta]['neuron']
            prfs = slideAnex [et][eta]['perfs']
            lc[0] = '%d'%neuron
            refBench = prfs[0]

            perfBench = prfs[1]

            bestNetBench = prfs[2]

            la.extend(perfBench)
            lb.extend(refBench)
            lc.extend(bestNetBench)
            etlines.extend([la,lb,lc])
          linhas=[]
          if not unbinned:
            linhas.append(l1)
          linhas.append(l2)
          linhas.extend(etlines)
          if unbinned:
            BeamerTableSlide(title =  'Performance',
                           linhas = linhas,
                           sideline = sideline,
                           caption = 'Efficiences',
                           )
          else:
            with BeamerSubSection (name= slideAnex[et][0]['etstr']):
              BeamerTableSlide(title =  'Performance',
                           linhas = linhas,
                           sideline = sideline,
                           caption = 'Efficiences',
                           )

      with BeamerSection( name = 'Figures' ):
        if unbinned:
          neuron = slideAnex [0][0]['neuron']
          graphSections = slideAnex [0][0]['graphSections']
          figures = slideAnex [0][0]['figures']
          for graph in graphSections:
            BeamerFigureSlide(title = graph + ' Neuron: '+ str(neuron) ,
                          path = figures[graph]
                               )
        else:
          for et in xrange(net):
            with BeamerSubSection (name= slideAnex[et][0]['etstr']):
              for eta in xrange(neta):
                neuron = slideAnex [et][eta]['neuron']
                graphSections = slideAnex [et][eta]['graphSections']
                figures = slideAnex [et][eta]['figures']

                with BeamerSubSubSection (name= slideAnex[et][eta]['etastr'] + ', Neuron: {}'.format(neuron)):
                  for graph in graphSections:
                    BeamerFigureSlide(title = graph,
                                       path = figures[graph]
                                      )
  return

