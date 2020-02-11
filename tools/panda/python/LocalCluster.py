__all__ = [ 'LsfParser', 'PbsParser'
          , 'lsfParser', 'pbsParser'
          , 'LSFArgumentParser', 'PBSJobArgumentParser'
          , 'LocalClusterNamespace', 'PBSOutputMerging']

import os
from Gaugi.messenger import Logger
from Gaugi.parsers.ClusterManager import ( JobSubmitArgumentParser, JobSubmitNamespace
                                              , clusterManagerParser, ClusterManager, AvailableManager
                                              , OptionRetrieve, BooleanOptionRetrieve, SubOptionRetrieve
                                              , clusterManagerConf, EnumStringOptionRetrieve
                                              )
from Gaugi import get_attributes, EnumStringification, BooleanStr, NotSet


class PBSOutputMerging( EnumStringification ):
  """
  Specified how to merge the output of a PBS/TorqueJob. When set to: 
    n -> no merge is performed to the output;
    oe -> stderr is merged to stdout;
    eo -> stdout is merged to stderr.
  """

  n  = 0
  oe = 1
  eo = 2

class LSFArgumentParser( JobSubmitArgumentParser ):
  prefix = 'lsf'
class PBSJobArgumentParser( JobSubmitArgumentParser ):
  prefix = 'pbs'

def PbsParser():
  pbsParser = PBSJobArgumentParser(description = 'Run job on local cluster using PBS/Torque',
                                   parents = [clusterManagerParser],
                                   conflict_handler = 'resolve')
  pbsGroup = pbsParser.add_argument_group('PBS/Torque Arguments', '')
  pbsGroup.add_job_submission_option('-Q','--queue',action='store', required = False,
                                      help = "Specify the job queue.")
  OMP_NUM_THREADS = int(os.environ.get('OMP_NUM_THREADS',1))
  pbsGroup.add_job_submission_option( '--nodes', option='-l',suboption='nodes', action=SubOptionRetrieve, required = False
                                    , type=int
                                    , help = "Specify the job number of nodes.")
  pbsGroup.add_job_submission_option( '--ncpus', option='-l',suboption='ncpus', action=SubOptionRetrieve, required = False
                                    , default = OMP_NUM_THREADS, type=int
                                    , help = "Specify the job number of nodes.")
  pbsGroup.add_job_submission_option( '--walltime', option='-l', suboption='walltime', required = False
                                    , action=SubOptionRetrieve
                                    , help = "Specify the job wall time limit using format [hh:mm:ss].")
  pbsGroup.add_job_submission_option( '--mem', option='-l', suboption='mem',action=SubOptionRetrieve
                                    , required = False
                                    , help = "Specify the job memory size.")
  pbsGroup.add_job_submission_option( '-oe', '--combine-stdout-sterr', option='-j', action=EnumStringOptionRetrieve
                                    , required = False, type=PBSOutputMerging, default=PBSOutputMerging.oe
                                    , help = PBSOutputMerging.__doc__)
  pbsGroup.add_job_submission_option( '-stdout', action='store', required = False
                                    , help = "Name of standard output file.")
  pbsGroup.add_job_submission_option( '-stderr', action='store', required = False
                                    , help = "Name of standard output error file.")
  pbsGroup.add_job_submission_option( '-V','--copy-environment', option = '-V', action=BooleanOptionRetrieve
                                    , required = False, type = BooleanStr
                                    , help = "Copy current environment to the job.")
  pbsGroup.add_job_submission_option( '-N','--job-name', option = '-N', action=OptionRetrieve
                                    , help = "Specifies name for job submitted.", addEqual=False)
  pbsGroup.add_job_submission_option( '-M','--mail-address',action='store', required = False
                                    , help = "Specify mail address.")
  pbsGroup.add_job_submission_option( '-D','--job-dependency',action='store', required = False
                                    , type = int
                                    , help = "Specifies that current job depends on other job.")
  pbsGroup.add_job_submission_option( '-j','--job-dependency',action='store', required = False
                                    , type = int
                                    , help = "Specifies that current job depends on other job.")
  # Arguments which are not propagated to the job, but handle how to set it up
  pbsGroup.add_argument('--debug', required = False, type = BooleanStr, default=False,
                        help = "Specify that this should be run on debug mode.")
  pbsGroup.add_argument( '--nFiles', required = False
                       , default = None, type=int
                       , help = """Specify the number of files in the input directory to be used.""")
  pbsGroup.add_argument('--max-job-slots', type = int, default = 48,
                       help = "Specify the maximum job slots that can be submitted with this name" )
  return pbsParser
pbsParser = PbsParser()
## TODO
def LsfParser():
  return None
lsfParser = None

################################################################################
## LocalClusterNamespace
class LocalClusterNamespace( JobSubmitNamespace, Logger, ):
  """
    Improves argparser workspace object to support creating a string object
    with the input options.
  """

  def __init__(self, localCluster = None, **kw):
    Logger.__init__( self, kw )
    if localCluster in (None, NotSet):
      localCluster = clusterManagerConf()
    self.localCluster = AvailableManager.retrieve( localCluster )
    if self.localCluster is ClusterManager.LSF:
      self.prefix = LSFArgumentParser.prefix
      prog = 'bsub'
    elif self.localCluster is ClusterManager.PBS:
      self.prefix = PBSJobArgumentParser.prefix
      from socket import gethostname
      prog = 'qsub'
      # Work on environment
      if "service1" in gethostname():
        import re
        THEANO_FLAGS = os.getenv('THEANO_FLAGS')
        m = re.search('cxx=([^,]*)(,*)?',THEANO_FLAGS)
        if m:
          CXX_THEANO_FLAGS = m.group(1)
          os.environ['THEANO_FLAGS'] = re.sub('cxx=[^,]*', "cxx=ssh service1 " + CXX_THEANO_FLAGS, THEANO_FLAGS)
          self._debug("Set THEANO_FLAGS to: %s", os.getenv('THEANO_FLAGS'))
        else:
          self._warning("THEANO FLAGS continues equal to: %s", os.getenv('THEANO_FLAGS') )
    else:
      self._fatal("Not implemented LocalClusterNamespace for cluster manager %s", AvailableManager.retrieve(self.localCluster), NotImplementedError)
    JobSubmitNamespace.__init__( self, prog = prog)

  def setExec(self, value):
    """
      Add the execution command on grid.
    """
    self.exec_ = value 

  def run(self):
    "Execute the command"
    full_cmd_str = self.prog + ' \\\n'
    full_cmd_str += self._parse_standard_args()
    if hasattr(self,'exec_') and '-' in self.exec_: full_cmd_str += ' -- ' 
    full_cmd_str += self.parse_exec()
    full_cmd_str += self.parse_special_args()
    return self._run_command(full_cmd_str)

  def parse_exec(self):
    full_cmd_str = ''
    # Add execute grid command if available
    if hasattr(self,'exec_'):
      #full_cmd_str += self._formated_line( '--' )
      full_cmd_str += self.parseExecStr(self.exec_, addQuote = False)
    return full_cmd_str

  def parse_special_args(self):
    return ''
