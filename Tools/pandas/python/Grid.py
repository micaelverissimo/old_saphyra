__all__ = ['SecondaryDataset','SecondaryDatasetCollection', 
           'GridOutput','GridOutputCollection', 'GridNamespace',  
           'GridParser', 'InGridParser', 'IOGridParser', 'OutGridParser',
           'gridParser', 'inGridParser', 'ioGridParser', 'outGridParser',
           'MultiThreadGridConfigure' ]

import os
from Gaugi.messenger import Logger
from Gaugi.parsers.Logger import LoggerNamespace
from Gaugi.parsers.ClusterManager import ( JobSubmitArgumentParser, JobSubmitNamespace
                                         , clusterManagerParser ) 
from Gaugi.LimitedTypeList import LimitedTypeList
from Gaugi.gtypes import BooleanStr, NotSet
from Gaugi.Configure import CastToTypeOptionConfigure

def extract_scope(did):
  """
  Taken from rucio client v1.13.2 itself
  """
  # Try to extract the scope from the DSN
  if did.find(':') > -1:
    if len(did.split(':')) > 2:
      raise RuntimeError('Too many colons. Cannot extract scope and name')
    scope, name = did.split(':')[0], did.split(':')[1]
    if name.endswith('/'):
      name = name[:-1]
    return scope, name
  else:
    scope = did.split('.')[0]
    if did.startswith('user') or did.startswith('group'):
      scope = ".".join(did.split('.')[0:2])
    if did.endswith('/'):
      did = did[:-1]
    return scope, did


################################################################################
# Grid parser related objects
################################################################################
class GridJobArgumentParser( JobSubmitArgumentParser ):
  prefix = 'grid'

class SecondaryDataset( object ):
  """
  Implements a helper class for panda run SecondaryDataset option:

  https://twiki.cern.ch/twiki/bin/view/PanDA/PandaRun#How_to_use_multiple_input_datase
  """

  def __init__(self, key, nFilesPerJob,  container, MatchingPattern = None, nSkipFiles = None, reusable = False ):
    self.key = key
    self.container = container
    self.nFilesPerJob = nFilesPerJob
    self.MatchingPattern = MatchingPattern
    self.nSkipFiles = nSkipFiles
    self.reusable = reusable

  def __str__(self):
    values = []
    values.append(self.key)
    values.append(str(self.nFilesPerJob))
    values.append(self.container)
    if self.MatchingPattern is not None: values.append(self.MatchingPattern)
    if self.nSkipFiles is not None: values.append(self.nSkipFiles)
    return ':'.join(values)

  def __repr__(self):
    return 'SecondaryDataset(' + str(self) + '|reusable=' + str(self.reusable) + ')'

class SecondaryDatasetCollection( object ):
  __metaclass__ = LimitedTypeList
  _acceptedTypes = SecondaryDataset,

class GridOutput( object ):
  """
  Implements a helper class for panda run SecondaryDataset option:

  https://twiki.cern.ch/twiki/bin/view/PanDA/PandaRun#How_to_use_multiple_input_datase
  """

  def __init__(self, key = None, regexp = None ):
    self.key = key
    if not regexp:
      raise ValueError('regexp must be a valid.')
    self.regexp = regexp

  def __str__(self):
    values = []
    if self.key: values.append(self.key)
    values.append(self.regexp)
    return ':'.join(values)

  def __repr__(self):
    return 'GridOutput(' + str(self) + ')'

class GridOutputCollection( object ):
  __metaclass__ = LimitedTypeList
  _acceptedTypes = GridOutput,

class MultiThreadGridConfigure( CastToTypeOptionConfigure ):
  """
  This class can be used to auto-configure multi-thread jobs submition by
  estimating how much memory it will be required through the use of the input
  file size and a multiplication factor.
  """
  _castType = int
  alwaysAutoConfigure = True

  _inputFile = NotSet

  def __init__( self, mem_multiplier = 3., single_thread_mem_limit = 3000
              , mt_ncores = 8, useRucio = True, **kw ):
    """
    * mem_multiplier: estimate job memory usage by multiplying input file size by <mem_multiplier>
    * single_thread_mem_limit: the upper limit (in mbs) to submit single thread jobs
    * mt_ncores: number of cores for multi-thread job
    * useRucio: whether we should use rucio to acquire file size
    """
    self.mem_multiplier = mem_multiplier
    self.single_thread_mem_limit = single_thread_mem_limit
    self.mt_ncores = mt_ncores
    self.useRucio = useRucio
    self.job_memory_consumption = None
    self.mt_job = False
    CastToTypeOptionConfigure.__init__( self, **kw )

  def setInputFile( self, path ):
    if not self.useRucio:
      from Gaugi import expandPath
      path = expandPath( path )
      if not os.path.isfile( path ):
        self._fatal( 'Attempted to set input file to a non-existent path: %s', path, ValueError )
    self._inputFile = path

  def getInputFile( self ):
    if self._inputFile not in (None, NotSet):
      return self._inputFile
    else:
      self._fatal( 'Input file was not set.', RuntimeError )

  inputFile = property( getInputFile, setInputFile )

  def auto( self ):
    """
    Check memory size of file in rucio container and submit multi-thread jobs
    accordingly to grid limit
    """
    if self.useRucio:
      try:
        from rucio.client import DIDClient
        from rucio.common.exception import DataIdentifierNotFound
      except ImportError:
        self._fatal("Please set rucio client.", ImportError)
      didClient = DIDClient()
      if isinstance(self.inputFile, SecondaryDataset):
        container = self.inputFile.container
      else:
        container = self.inputFile
      #from Gaugi.RucioTools import extract_scope
      scope, dataset = extract_scope(container)
      try:
        d = didClient.list_files(scope, dataset).next()
        files = list( didClient.list_files(scope, dataset) )
        if len(files) > 1:
          self._fatal("More than one file in container, possibly wrong container input.")
        job_memory_consumption = ( files[0]['bytes'] * self.mem_multiplier ) / 1024.**(2)
        if job_memory_consumption > self.single_thread_mem_limit:
          self._info( "Setting multi-thread job for file %s since its forseen memory consumption is %.0f MB."
                     , files[0]['name'], job_memory_consumption )
          self._choice = self.mt_ncores  
          self.mt_job = True
        else:
          self._debug( "Setting single-thread job for file %s since its forseen memory consumption is %.0f MB."
                     , files[0]['name'], job_memory_consumption )
          self._choice = 1
          self.mt_job = False
        self.job_memory_consumption = job_memory_consumption
      except DataIdentifierNotFound, e:
        self._fatal(("Could not retrieve number of files on informed data DID. "
                     "Did you send the dataset to the GRID (e.g. by running add_container?). "
                     "Rucio error:\n%s"), e, RuntimeError)
    else:
      self._fatal("Estimation only available when using rucio.", NotImplementedError)

# Basic grid parser
def GridParser():
  gridParser = GridJobArgumentParser( add_help = False, parents = [clusterManagerParser] )
  gridParserGroup = gridParser.add_argument_group('GRID Arguments', '')
  gridParserGroup.add_job_submission_option('--site',default = 'AUTO',
      help = "The site location where the job should run.",
      required = False,)
  shortSites = ['ANALY_CERN_SHORT','ANALY_CONNECT_SHORT','ANALY_BNL_SHORT']
  gridParserGroup.add_job_submission_csv_option('--excludedSite', 
      #default = 'ANALY_CERN_CLOUD,ANALY_CERN_SHORT,ANALY_CONNECT_SHORT,ANALY_BNL_SHORT', # Known bad sites
      #default = 'ANALY_CERN_CLOUD,ANALY_SLAC,ANALY_CERN_SHORT,ANALY_CONNECT_SHORT,ANALY_BNL_SHORT,ANALY_BNL_EC2E1,ANALY_SWT2_CPB', # Known bad sites
      default = 'ANALY_DESY-HH_UCORE,ANALY_BNL_MCORE,ANALY_MWT2_SL6,ANALY_MWT2_HIMEM,ANALY_DESY-HH,ANALY_FZK_UCORE,ANALY_FZU,DESY-HH_UCORE,FZK-LCG2_UCORE',
      help = "The excluded site location.", 
      required = False, )
  gridParserGroup.add_job_submission_option_group('--debug', default = None,
      const='--express --debugMode --allowTaskDuplication --disableAutoRetry --useNewCode',
      help = "Submit GRID job on debug mode.", action='store_const',
      required = False )
  gridParserGroup.add_job_submission_option('--nCore', type=int,
      required = False, help = """Number of cores to be used by the job.""")
  gridParserGroup.add_job_submission_option('--nJobs', type=int,
      required = False, help = """Number of jobs to submit.""")
  gridParserGroup.add_job_submission_option('--excludeFile', 
      required = False, default = '"*.o,*.so,*.a,*.gch,Download/*,InstallArea/*,RootCoreBin/*,RootCore/*,*new_env_file.sh,"',
      help = """Files to exclude from environment copied to grid.""")
  gridParserGroup.add_job_submission_option('--disableAutoRetry', type=BooleanStr,
      required = False,
      help = """Flag to disable auto retrying jobs.""")
  gridParserGroup.add_job_submission_option('--followLinks', type=BooleanStr,
      required = False,
      help = """Flag to disable auto retrying jobs.""")
  gridParserGroup.add_job_submission_option('--mergeOutput', type=BooleanStr,
      required = False,
      help = """Flag to enable merging output.""")
  #gridParserGroup.add_job_submission_option('--mergeScript', 
  #    required = False, 
  #    help = """The script for merging the files. E.g.: 'your_merger.py -o %%OUT -i %%IN'""")
  gridParserGroup.add_job_submission_csv_option('--extFile', 
      required = False, 
      help = """External file to add.""")
  gridParserGroup.add_job_submission_option('--match', 
      required = False, 
      help = """Use only files matching with given pattern.""")
  gridParserGroup.add_job_submission_option('--antiMatch', 
      required = False,
      help = """Use all files but those matching with given pattern.""")
  gridParserGroup.add_job_submission_option('--cloud', 
      required = False, default=False,
      help = """The cloud where to submit the job.""")
  gridParserGroup.add_job_submission_option('--nGBPerJob', 
      required = False,
      help = """Maximum number of GB per job.""")
  gridParserGroup.add_job_submission_option('--skipScout', type=BooleanStr,
      required = False,
      help = """Flag to disable auto retrying jobs.""")
  gridParserGroup.add_job_submission_option('--memory', type=int,
      required = False,
      help = """Needed memory to run in MB.""")
  gridParserGroup.add_job_submission_option('--long', type=BooleanStr,
      required = False,
      help = """Submit for long queue.""")
  gridParserGroup.add_job_submission_option('--useNewCode', type=BooleanStr,
      required = False,
      help = """Flag to disable auto retrying jobs.""")
  gridParserGroup.add_job_submission_option('--allowTaskDuplication', type=BooleanStr,
      required = False,
      help = """Flag to disable auto retrying jobs.""")
  gridParserGroup.add_job_submission_option('--crossSite',
      required = False, type=int,
      help = """Split jobs over many sites.""")
  mutuallyEx1 = gridParserGroup.add_mutually_exclusive_group( required=False )
  mutuallyEx1.add_job_submission_option('-itar','--inTarBall', 
      metavar='InTarBall', 
      help = "The environemnt tarball for posterior usage.")
  mutuallyEx1.add_job_submission_option('-otar','--outTarBall',
      metavar='OutTarBall',  
      help = "The environemnt tarball for posterior usage.")
  mutuallyEx1.title = 'GRID Mutually Exclusive Arguments'
  return gridParser 
gridParser = GridParser()
################################################################################
## Temporary classes only to deal with diamond inherit scheme
def _InParser():
  _inParser = GridJobArgumentParser(add_help = False)
  _inParserGroup = _inParser.add_argument_group('GRID Input Dataset Arguments', '')
  _inParserGroup.add_job_submission_option('--inDS','-i', action='store', 
                         required = True,
                         help = "The input Dataset ID (DID)")
  _inParserGroup.add_job_submission_csv_option('--secondaryDSs', action='store',
                         required = False, default = SecondaryDatasetCollection(),
                         help = "The secondary Dataset ID (DID), in the format name:nEvents:place")
  _inParserGroup.add_job_submission_option('--forceStaged', type=BooleanStr,
      required = False, default = False,
      help = """Force files from primary DS to be staged to local
      disk, even if direct-access is possible.""")
  _inParserGroup.add_job_submission_option('--forceStagedSecondary', type=BooleanStr,
      required = False,
      help = """Force files from secondary DS to be staged to local
                disk, even if direct-access is possible.""")
  _inParserGroup.add_job_submission_csv_option('--reusableSecondary', 
      required = False,
      help = """Allow reuse secondary dataset.""")
  _inParserGroup.add_job_submission_option('--nFiles', type=int,
      required = False,
      help = """Number of files to run.""")
  _inParserGroup.add_job_submission_option('--nFilesPerJob', type=int,
      required = False,
      help = """Number of files to run per job.""")
  return _inParser 
################################################################################
def _OutParser():
  _outParser = GridJobArgumentParser(add_help = False)
  _outParserGroup = _outParser.add_argument_group('GRID Output Dataset Arguments', '')
  _outParserGroup.add_job_submission_option('--outDS','-o', action='store', 
                          required = True,
                          help = "The output Dataset ID (DID)")
  _outParserGroup.add_job_submission_csv_option('--outputs', required = True,
      default = GridOutputCollection(),
      help = """The output format.""")
  return _outParser
################################################################################
## Input and output grid parser
def IOGridParser():
  ioGridParser = GridJobArgumentParser(add_help = False, 
                                       parents = [_InParser(), _OutParser(), GridParser()],
                                       conflict_handler = 'resolve')
  return ioGridParser
ioGridParser = IOGridParser()

## Input grid parser
def InGridParser():
  inGridParser = GridJobArgumentParser(add_help = False, 
                                       parents = [_InParser(), GridParser()],
                                       conflict_handler = 'resolve')
  return inGridParser
inGridParser = InGridParser()

## Output grid parser
def OutGridParser():
  outGridParser = GridJobArgumentParser(add_help = False, 
                                        parents = [_OutParser(), GridParser()],
                                        conflict_handler = 'resolve')
  return outGridParser
outGridParser = OutGridParser()

class LargeDIDError(ValueError):
  def __init__(self, in_):
    ValueError.__init__(self, ('Size of --outDS is larger (%d) than 132 char, '
                        'the maximum value allowed by CERN grid. '
                        'Current DID is valid until: %s') % (len(in_), in_[:132]))

################################################################################
## GridNamespace
# Make sure to use GridNamespace specialization for the used package when
# parsing arguments.
class GridNamespace( JobSubmitNamespace ):
  """
    Improves argparser workspace object to support creating a string object
    with the input options.
  """

  #noNumyPySites = ['ANALY_SWT2_CPB','ANALY_BNL_EC2E1']

  prog = 'prun'
  ParserClass = GridJobArgumentParser

  def __init__(self, prog = None, **kw):
    JobSubmitNamespace.__init__( self, prog = prog)

  def setBExec(self, value):
    """
      Add a build execute command.
    """
    if len(value) > 0 and value[0] != '"':
      value = '"' + value
    if value[-1] != '"':
      value += '"'
    self.bexec = value 

  def setExec(self, value):
    """
      Add the execution command on grid.
    """
    if len(value) < 1 or value[0] != '"':
      value = '"' + value
    if len(value) < 2 or value[-1] != '"':
      value += '"'
    self.exec_ = value 

  def setMergeExec(self, value):
    """
      Add the merge execution command on grid.
    """
    if len(value) < 1 or value[0] != '"':
      value = '"' + value
    if len(value) < 2 or value[-1] != '"':
      value += '"'
    self.mergeExec = value 

  def extFile(self):
    """
      Return list of extFiles needed by this GridNamespace.
    """
    return []

  def run(self):
    """
      Run the command
    """
    if not self.dry_run:
      self.pre_download()
    # We need to cd to this dir so that prun accepts the submission
    workDir=os.path.expandvars("$ROOTCOREBIN/..")
    os.chdir(workDir)
    JobSubmitNamespace.run(self)


  def parse_exec(self):
    full_cmd_str = ''
    # Add execute grid command if available
    if hasattr(self,'bexec'):
      full_cmd_str += self._formated_line( '--bexec')
      full_cmd_str += self.parseExecStr(self.bexec, addSemiColomn = False)
    if hasattr(self,'exec_'):
      full_cmd_str += self._formated_line( '--exec' )
      full_cmd_str += self.parseExecStr(self.exec_)
    if hasattr(self,'mergeExec'):
      full_cmd_str += self._formated_line( '--mergeScript' )
      full_cmd_str += self.parseExecStr(self.mergeExec, addSemiColomn = False)
    return full_cmd_str

  def parse_special_args(self):
    if hasattr(self,'mergeExec'):
      if not(self.has_job_submission_option('mergeOutput')) or not(self.get_job_submission_option('mergeOutput')):
        self.set_job_submission_option('mergeOutput', True)
    if self.has_job_submission_option('outDS'):
      outDS = self.get_job_submission_option('outDS')
      outputs = self.get_job_submission_option('outputs')
      for output in outputs:
        oList = str(output).split(':')
        if len(oList) == 2:
          did = outDS + '_' + oList[0].replace('"','')
          if len(did) > 132:
            raise LargeDIDError(did)
        else:
          if '*' in output and not output.endswith('.tgz'): output += '.tgz'
          did = outDS + '_' + output.replace('*','XYZ').replace('"','')
          if len(did) > 132:
            raise LargeDIDError(did)
    for extFile in self.extFile():
      if not extFile in self.get_job_submission_option('extFile'):
        self.append_to_job_submission_option('extFile', extFile )
    # Treat reusable secondary to include those secondaryDSs that are reusable
    self.append_to_job_submission_option('reusableSecondary', [secondaryDS.key for secondaryDS in self.get_job_submission_option('secondaryDSs')
                                                                 if secondaryDS.reusable and 
                                                                   not secondaryDS.key in self.get_job_submission_option('reusableSecondary')
                                                              ]
                                        )
    if self.get_job_submission_option('long'):
      excludedSite = self.get_job_submission_option('excludedSite')
      if self.get_job_submission_option('excludedSite'):
        for shortSite in shortSites:
          if not shortSite in excludedSite:
            self.append_to_job_submission_option('excludedSite', shortSite)
      else:
        self.set_job_submission_option('excludedSite', shortSites)
    return ''


  def check_retrieve(self, filename, md5sum, dlurl):
    filename = os.path.expandvars(filename)
    basefile = os.path.basename(filename)
    dirname = os.path.dirname( filename )
    from Gaugi.FileIO import checkFile
    if not checkFile(filename, md5sum):
      self._info('Downloading %s to avoid doing it on server side.', basefile)
      import urllib
      if not os.path.isdir( dirname ):
        from Gaugi import mkdir_p
        mkdir_p( dirname )
      urllib.urlretrieve(dlurl, filename=filename)
    else:
      self._debug('%s already downloaded.', filename)

  def pre_download(self):
    """
      Packages which need special libraries downloads to install should inherit
      from this class and overload this method to download needed libraries.
    """
    self.check_retrieve("$ROOTCOREBIN/../Downloads/boost.tgz"
                       ,"5a5d5614d9a07672e1ab2a250b5defc5"
                       ,"http://sourceforge.net/projects/boost/files/boost/1.58.0/boost_1_58_0.tar.gz"
                       )
    self.check_retrieve("$ROOTCOREBIN/../Downloads/cython.tgz"
                       ,"890b494a12951f1d6228c416a5789554"
                       ,"https://pypi.python.org/packages/c6/fe/97319581905de40f1be7015a0ea1bd336a756f6249914b148a17eefa75dc/Cython-0.24.1.tar.gz"
                       )
    self.check_retrieve("$ROOTCOREBIN/../Downloads/numpy.tgz"
                       ,"3cb325c3dff03b5bc15206c757a26116"
                       ,"https://github.com/numpy/numpy/archive/v1.10.4.tar.gz"
                       #,"http://sourceforge.net/projects/numpy/files/NumPy/1.10.4/numpy-1.10.4.tar.gz/download"
                       )
    self.check_retrieve("$ROOTCOREBIN/../Downloads/setuptools.tgz"
                       ,"0744ee90ad266fb117d59f94334185d0"
                       ,"https://pypi.python.org/packages/32/3c/e853a68b703f347f5ed86585c2dd2828a83252e1216c1201fa6f81270578/setuptools-26.1.1.tar.gz"
                       )
    self.check_retrieve("$ROOTCOREBIN/../Downloads/scipy.tgz"
                       ,"9c6bc68693d7307acffce690fe4f1076"
                       ,"https://github.com/scipy/scipy/archive/v0.18.0-1.tar.gz"
                       )

