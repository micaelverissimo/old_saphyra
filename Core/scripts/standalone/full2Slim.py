#!/usr/bin/env python

from RingerCore import Logger,  LoggingLevel, emptyArgumentsPrintHelp

# Local class to extract the ntuple from the list of files 
class CopyTree( Logger ):

  def __init__(self, outputDS):
    Logger.__init__(self)
    from ROOT import TFile
    # Check if the type is correct
    if not '.root' in outputDS:  outputDS+='.root'
    self._file = TFile( outputDS, 'recreate' )
    self._outputDS=outputDS
    self._logger.info( ('Create root file with name: %s') \
                        %(outputDS) )


  def __call__(self, inputDS_list, basepath, trigger , treename):
    
    if not type(inputDS_list) is list:  inputDS_list = [inputDS_list]
    from ROOT import TChain, TObject
    self._file.cd();  self._file.mkdir( basepath+'/'+trigger )
    self._file.cd( basepath+'/'+trigger )
    cobject = TChain()
    for inputDS in inputDS_list:
      self._logger.info( ('Copy tree name %s in %s to %s')%(treename,\
                           inputDS, self._outputDS) )
      location = inputDS+'/'+basepath+'/'+trigger+'/'+treename
      cobject.Add( location )

    if cobject.GetEntries() == 0:
      self._logger.warning(('There is no events into this path: %s')%(location))
      del cobject
      return False
    else:
      self._logger.info(('Copy %d events...')%(cobject.GetEntries()))
      try:# Copy protection
        copy_cobject = cobject.CloneTree(-1)
        try:# Write protection
          copy_cobject.Write("", TObject.kOverwrite)
          del copy_cobject
        except:# error
          del copy_cobject
          self._logger.error('Can not write the tree')
          return False
      except:# error
        del cobject
        self._logger.error('Can not copy the tree')
        return False
    del cobject

    # Everything is good
    return True

        
  def save(self):
    self._logger.info( ('Saving file %s') % (self._outputDS) )
    self._file.Close()




######################### __main__ ############################
from RingerCore import expandFolders, csvStr2List, ArgumentParser
from pprint import pprint

mainFilterParser = ArgumentParser()

mainFilterParser.add_argument('-i','--inputFiles', action='store', 
                               metavar='InputFiles', required = True, nargs='+',
                               help = "The input files that will be used to generate a extract file")

mainFilterParser.add_argument('-t', '--trigger', action='store', default='e0_perf_L1EM15',
                               required = True,
                               help = "Trigger list to keep on the filtered file.")

mainFilterParser.add_argument('--basepath', action='store', default='HLT/Egamma/Expert',
                               help = "the basepath to the ntuple")

mainFilterParser.add_argument('-o','--output', action='store', default='NTUPLE.*.root',
                               help = "output file name.")

mainFilterParser.add_argument('--treename', action='store', default='trigger',
                               help = "The ntuple name")

emptyArgumentsPrintHelp( mainFilterParser )

mainLogger = Logger.getModuleLogger( __name__, LoggingLevel.INFO )
mainLogger.info('Start ntuple extraction...')
# retrieve args
args=mainFilterParser.parse_args()

# Treat special arguments
if len( args.inputFiles ) == 1:
  args.inputFiles = csvStr2List( args.inputFiles[0] )

args.inputFiles = expandFolders( args.inputFiles )
mainLogger.verbose("All input files are:")
pprint(args.inputFiles)

if '*' in args.output:
  output = args.output.replace('*', args.trigger.replace('HLT_',''))
else:
  output = args.output

# Copy the tree to an slim file
obj  = CopyTree( output )
if obj( args.inputFiles, args.basepath, args.trigger, args.treename) :
  obj.save()
else:
  if os.path.exists( output ):  
    os.system( ('rm -rf %s')%(output) )

del obj












