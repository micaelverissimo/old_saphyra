#!/usr/bin/env python

import os
import re
import numpy as np

from RingerCore import Logger, LoggingLevel, mkdir_p, ArgumentParser

from ROOT import TChain, TFile, TObject

class RootFile(Logger):
  matchLine = re.compile('(.*\.root)\.\d+')
  def __init__(self, input_, output):
    Logger.__init__( self )
    self.f     = TFile.Open(output, 'recreate')
    self.input_ = input_

  def dump(self, location, ntuples ):
    if any(ntuples):
      self.f.cd()
      self.f.mkdir(location)
      self.f.cd(location)
        
      for ntuple in ntuples:
        t_chain = TChain()
        for f in self.input_:
          f = 'tmpDir/' + f
          m = self.matchLine.match(f)
          if m:
            newName = m.group(1)
            os.rename(f, newName)
            f = newName
          self._logger.info( 'ntuple: %s | file: %s', ntuple, f)
          t_chain.Add( f + '/' + location + '/' + ntuple)
        t_ntuple = t_chain.CloneTree(-1)
        t_ntuple.Write("", TObject.kOverwrite)
   
  def save(self):
    self.f.Close()
    
defaultTrigList = [
            'e24_medium_L1EM18VH',
            'e24_lhmedium_L1EM18VH',
            'e24_tight_L1EM20VH',
            #'e24_vloose_L1EM20VH',
            #'e5_loose_idperf',
            #'e5_lhloose_idperf',
            #'e5_tight_idperf',
            #'e5_lhtight_idperf',
            'e24_medium_idperf_L1EM20VH',
            'e24_lhmedium_idperf_L1EM20VH'
            ]
    
parser = ArgumentParser()
parser.add_argument('--inDS',  action='store', required=True,
    help = "Input container to retrieve data")
parser.add_argument('--outFolder', action='store', default="dumpOutput")
parser.add_argument('--triggerList', nargs='+', default=defaultTrigList )
parser.add_argument('--numberOfSamplesPerPackage', type=int,  default=50)
args=parser.parse_args()

mainLogger = Logger.getModuleLogger( __name__, LoggingLevel.INFO )

if os.path.exists( 'dq2_ls.txt' ):
  os.system('rm dq2_ls.txt')

if args.inDS[-1] != '/':
  args.inDS += '/'

if args.outFolder[-1] != '/':
  args.outFolder += '/'

mkdir_p( args.outFolder )
mkdir_p( 'tmpDir' )

os.system('dq2-ls -fH '+args.inDS+' >& dq2_ls.txt')

with open('dq2_ls.txt','r') as f:
  lines    = f.readlines()
  samples = []
  dataset = ''
  fileLine = re.compile('\[ \]\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+')
  for s in lines:
    m = fileLine.match(s)
    if m:
      samples.append( m.group(1) )

  package = []
  package_list = []

  for i in range(len(samples)):
    package.append(samples[i])
    if len(package) == args.numberOfSamplesPerPackage or i == len(samples)-1:
      package_list.append( package )
      package = []

  for i in range(len(package_list)):
    mainLogger.info('---------------------------- DOWNLOADING PACKAGE %d  -------------------------------', i)
    string = 'dq2-get -H tmpDir -t 15 -f ' + ','.join(package_list[i]) + ' ' + args.inDS
    mainLogger.info('%s', string)
    os.system( string )
    mainLogger.info('---------------------------- FINISHED DOWNLOADING PACKAGE %d -------------------------------', i)

    oStr = args.outFolder + 'sample.'+ args.inDS[:-1] +'._'+str(i)+'.root'
    mainLogger.info( oStr )
    rFile = RootFile( package_list[i], oStr )
    rFile.dump('Offline/Egamma/Ntuple',['electron'])
    rFile.dump('Trigger/HLT/Egamma/Ntuple',  args.triggerList)
    if 'Zee' in  args.inDS:
      rFile.dump('Trigger/HLT/Egamma/TPNtuple', args.triggerList)
    rFile.save()
    os.system('rm -rf tmpDir/user.*')


