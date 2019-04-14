#!/usr/bin/env python

import os
import re
import numpy as np

from RingerCore import Logger, LoggingLevel, mkdir_p, expandFolders, ArgumentParser

from ROOT import TChain, TFile, TObject

# FIXME This can be added as a merge job to the PhysVal creation
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
          m = self.matchLine.match(f)
          if m:
            newName = m.group(1)
            os.rename(f, newName)
            f = newName
          self._logger.info( 'ntuple: %s | file: %s', ntuple, f)
          t_chain.Add(f+'/'+location+'/'+ntuple)
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
parser.add_argument('--inFolderList', nargs='+', required=True,
    help = "Input container to retrieve data")
parser.add_argument('--signalDS', action='store_true',
    help = "Whether the dataset contains TPNtuple")
parser.add_argument('--outfile', action='store', default="mergedOutput.root",
    help = "Name of the output file")
parser.add_argument('--triggerList', nargs='+', default=defaultTrigList,
    help = "Trigger list to keep on the filtered file.")
args=parser.parse_args()

mainLogger = Logger.getModuleLogger( __name__, LoggingLevel.INFO )

files = expandFolders( args.inFolderList )

rFile = RootFile( files, args.outfile )
rFile.dump('Offline/Egamma/Ntuple', ['electron'])
rFile.dump('Trigger/HLT/Egamma/Ntuple',  args.triggerList)
if args.signalDS:
  rFile.dump('Trigger/HLT/Egamma/TPNtuple', args.triggerList)
rFile.save()
