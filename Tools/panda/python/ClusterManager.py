__all__ = ['JobSubmitArgumentParser', 'JobSubmitNamespace'
          , 'ClusterManager', 'has_Panda', 'has_PBS', 'has_Torque', 'has_LSF'
          , 'cluster_default', 'clusterManagerParser'
          , 'OptionRetrieve', 'BooleanOptionRetrieve', 'SubOptionRetrieve'
          , 'ClusterManagerConfigure', 'clusterManagerConf', 'EnumStringOptionRetrieve']

import re, pipes

from Gaugi.messenger import Logger, LoggingLevel
from Gaugi.parsers.ParsingUtils import ( _ActionsContainer, _MutuallyExclusiveGroup
                                            , _ArgumentGroup, ArgumentParser, argparse
                                            , ArgumentError )
from Gaugi.gtypes import EnumStringification, NotSet
from Gaugi.Configure import ( EnumStringificationOptionConfigure, Holder
                                 , cmd_exists )
from Gaugi.utilities import get_attributes

class OptionRetrieve( argparse.Action ):

  def __init__( self
              , option
              , dest = None
              , option_strings = []
              , value=None
              , addEqual = True
              , nargs=None
              , const=None
              , default=None
              , type=None
              , choices=None
              , required=False
              , help=None
              , metavar=None ):
    super(OptionRetrieve, self).__init__( option_strings = option_strings
                                        , dest           = dest
                                        , nargs          = nargs
                                        , const          = const
                                        , default        = default
                                        , type           = type
                                        , choices        = choices
                                        , required       = required
                                        , help           = help
                                        , metavar        = metavar
                                        )
    self.option = option
    self.value = value
    self.addEqual = addEqual

  def __bool__(self):
    return self.value is None

  def __call__(self, parser, namespace, value, option_string=None):
    self.value = value
    setattr(namespace, self.dest, self)

  def __str__(self):
    if self.value is not None:
      return ( self.option + ('=' if self.addEqual else ' ') 
             + ( pipes.quote( self.value ) if isinstance(self.value, basestring) else str(self.value) )
             )
    else: return ''

  def __repr__(self):
    return self.__class__.__name__ + '(' + str(self) + ')'

class BooleanOptionRetrieve( OptionRetrieve ):
  def __str__(self):
    if self.value:
      return self.option
    else: return ''

class EnumStringOptionRetrieve( OptionRetrieve ):
  def __str__(self):
    if self.value is not None:
      return self.option + ' ' + self.type.tostring(self.value)
    else: return ''


class SubOptionRetrieve( OptionRetrieve ):

  def __init__( self
              , option
              , suboption
              , dest = None
              , option_strings = []
              , addEqual = True
              , value=None
              , nargs=None
              , const=None
              , default=None
              , type=None
              , choices=None
              , required=False
              , help=None
              , metavar=None ):
    super(SubOptionRetrieve, self).__init__( option         = option
                                           , value          = value
                                           , addEqual       = addEqual
                                           , option_strings = option_strings
                                           , dest           = dest
                                           , nargs          = nargs
                                           , const          = const
                                           , default        = default
                                           , type           = type
                                           , choices        = choices
                                           , required       = required
                                           , help           = help
                                           , metavar        = metavar
                                           )
    self.suboption = suboption

  def __str__(self):
    if self.value is not None:
      return self.option + ' ' + self.suboption + ('=' if self.addEqual else ' ') + pipes.quote( str(self.value) )
    else: return ''

class _JobSubmitActionsContainer( _ActionsContainer ):

  def add_argument(self, *args, **kwargs):
    if 'action' in kwargs: 
      lAction = kwargs['action']
      try:
        if issubclass(lAction, SubOptionRetrieve):
          if 'default' in kwargs and kwargs['default'] not in (None, NotSet):
            kwargs['default'] = SubOptionRetrieve( option = kwargs['option']
                                                 , suboption = kwargs['suboption']
                                                 , value = kwargs['default'] )
        elif issubclass(lAction, OptionRetrieve):
          if 'default' in kwargs and kwargs['default'] not in (None, NotSet):
            kwargs['default'] = OptionRetrieve( option = kwargs['option']
                                              , value = kwargs['default'] )
      except TypeError, e:
        pass
    _ActionsContainer.add_argument(self, *args, **kwargs)

  def add_job_submission_option(self, *l, **kw):
    kw['dest'], kw['metavar'] = self._getDest(*l)
    self.add_argument(*l, **kw)

  def add_job_submission_csv_option(self, *l, **kw):
    kw['dest'], kw['metavar'] = self._getDest( *l, extraSpec = '_CSV')
    if kw.pop('nargs','+') != '+':
      raise ValueError('Cannot specify nargs different from \'+\' when using csv option')
    kw['nargs'] = '+'
    if not 'default' in kw:
      kw['default'] = []
    self.add_argument(*l, **kw)

  def add_job_submission_option_group(self, *l, **kw):
    "Add a group of options that will be set if true or another group to be set when false"
    kw['dest'], kw['metavar'] = self._getDest( *l, extraSpec = '_Group')
    self.add_argument(*l, **kw)

  #def add_job_submission_suboption(self, mainOption, suboption, *l, **kw):
  #  extraSpec = ('_Suboption_' + mainOption + '_' + suboption)
  #  kw['dest'], kw['metavar'] = self._getDest(*l, extraSpec = extraSpec)
  #  self.add_argument(*l, **kw)

  def add_argument_group(self, *args, **kwargs):
    kwargs['prefix'] = self.prefix
    group = _JobSubmitArgumentGroup(self, *args, **kwargs)
    self._action_groups.append(group)
    return group

  def add_mutually_exclusive_group(self, **kwargs):
    kwargs['prefix'] = self.prefix
    group = _JobSubmitMutuallyExclusiveGroup(self, **kwargs)
    self._mutually_exclusive_groups.append(group)
    return group

  def _getDest(self, *l, **kw):
    extraSpec = kw.pop('extraSpec', '')
    search = [item.startswith('--') for item in l]
    if search and any(search):
      idx = search.index( True ) 
      try:
        return self.prefix + extraSpec + '__' + l[idx].lstrip('--').replace('-','_'), l[idx].lstrip('--').upper().replace('-','_')
      except AttributeError:
        raise AttributeError("Class (%s) prefix attribute was not specified." % self.__class__.__name__)
    else:
      search = [item.startswith('-') for item in l]
      if search and any(search):
        idx = search.index( True ) 
        try:
          return self.prefix + extraSpec + '_' + l[idx].lstrip('-').replace('-','_'), l[idx].lstrip('-').upper().replace('-','_')
        except AttributeError:
          raise AttributeError("Class (%s) prefix attribute was not specified." % self.__class__.__name__)
    return 


class JobSubmitArgumentParser( _JobSubmitActionsContainer, ArgumentParser ):
  """
  This class separate the options to be parsed in two levels:
    -> One group of options that will be used to specify the job submition;
    -> Another group which may be used for general purpose, usually
    used to specify the job parameters.

  The second group should use the standard add_argument method. The first group,
  however, should be created using the add_job_submission_option, they will be 
  added to a destination argument which will use a prefix specified through the
  'prefix' class attribute.
  """
  def __init__(self,*l,**kw):
    _JobSubmitActionsContainer.__init__(self)
    ArgumentParser.__init__(self,*l,**kw)
    try:
      self.add_argument('--dry-run', action='store_true',
          help = """Only print resulting command, but do not execute it.""")
    except argparse.ArgumentError:
      pass


class JobSubmitNamespace( Logger, argparse.Namespace ):

  def __init__(self, prog = None, **kw):
    Logger.__init__( self, kw )
    if prog is not None:
      self.prog = prog
    else:
      try:
        self.prog = self.__class__.prog
      except AttributeError:
        raise AttributeError("Not specified class (%s) prog attribute!" % self.__class__.__name__)
    if not hasattr(self,'prefix'):
      try:
        self.prefix = self.__class__.ParserClass.prefix
      except AttributeError:
        raise AttributeError("Not specified class (%s) ParserClass attribute!" % self.__class__.__name__)
    argparse.Namespace.__init__( self )
    self.fcn = os.system

  def __call__(self):
    "Execute the command"
    self.run()

  def run(self):
    "Execute the command"
    full_cmd_str = self.prog + ' \\\n'
    full_cmd_str += self.parse_exec()
    full_cmd_str += self.parse_special_args()
    full_cmd_str += self._parse_standard_args()
    return self._run_command(full_cmd_str)

  def parse_exec(self):
    "Overload this method to specify how the exec command string should be written."
    return ''

  def parse_special_args(self):
    "Overload this method treat special parameters."
    return ''

  def has_job_submission_option(self, option):
    try:
      self._find_job_submission_option(option)
      return True
    except KeyError:
      return False

  def get_job_submission_option(self, option):
    return getattr(self, self._find_job_submission_option(option))

  def set_job_submission_option(self, option, val):
    return setattr(self, self._find_job_submission_option(option), val)

  def append_to_job_submission_option(self, option, val):
    try:
      from RingerCore.LimitedTypeList import LimitedTypeList
      if hasattr(val,'__metaclass__') and issubclass(val.__metaclass__, LimitedTypeList):
        attr = self.get_job_submission_option(option)
        attr += val
      elif isinstance(val, (tuple,list)):
        self.get_job_submission_option(option).extend(val)
      else:
        self.get_job_submission_option(option).append(val)
    except AttributeError, e:
      raise TypeError('Option \'%s\' is not a collection. Details:\n%s' % (option,e))

  def _find_job_submission_option(self, option):
    import re
    search = re.compile('^' + self.prefix + '(_.+)?_{1,2}' + option + '$')
    matches = [key for key in get_attributes(self, onlyVars = True) if bool(search.match( key ))]
    lMatches = len(matches)
    if lMatches > 1:
      self._warning("Found more than one match for option %s, will return first match. Matches are: %r.", option, matches)
    elif lMatches == 0:
      self._fatal("Cannot find job submission option: %s", option, KeyError)
    return matches[0]

  def parseExecStr(self, execStr, addQuote = True, addSemiColomn=True):
    retStr = ''
    import textwrap
    execStr = [textwrap.dedent(l) for l in execStr.split('\n')]
    execStr = [l for l in execStr if l not in (';','"','')]
    
    if addQuote:

      if addSemiColomn:
        if execStr[-1][-2:] != ';"': 
          if execStr[-1][-1] == '"':
            execStr[-1] = execStr[-1][:-1] + ';"'
          else:
            execStr[-1] += ';"' 
      else:
        if not execStr[-1][-1] == '"':
          execStr[-1] += '"'


    for i, l in enumerate(execStr):
      if i == 0:
        moreSpaces = 2
      else:
        moreSpaces = 4
      retStr += self._formated_line( l, moreSpaces = moreSpaces )
    return retStr

  def _nSpaces(self):
    "Specify the base number of spaces after entering the command."
    return len(self.prog) + 1

  def _formated_line(self, line, moreSpaces = 0 ):
    return (' ' * (self._nSpaces() + moreSpaces) ) + line + ' \\\n'
    
  def _parse_standard_args(self):
    """
    Here we deal with the standard arguments
    """
    cmd_str = ''
    nSpaces = self._nSpaces()
    # Add extra arguments
    for name, value in get_attributes(self):
      csv = False
      suboption = False
      parseName = True
      if name.startswith(self.prefix):
        name = name.replace(self.prefix,'',1)
        if name.startswith('_Group'):
          if value:
            name = value
            value = True
            parseName = False
          else:
            continue
        elif name.startswith('_CSV'):
          csv = True
          name = name.replace('_CSV','',1)
        elif name.startswith('_Suboption_'):
          suboption = True
          name = name.replace('_Suboption_','',1)
          option = name.split('')
        if parseName: name = name[:2].replace('_', '-') + name[2:]
      else:
        continue
      tVal = type(value)
      if tVal is bool:
        if value:
          cmd_str +=  self._formated_line( name )
      elif isinstance(value, OptionRetrieve) and value:
        cmd_str +=  self._formated_line( str(value) )
      elif value in (None, NotSet):
        continue
      elif isinstance(value, list):
        if value:
          if csv:
            cmd_str +=  self._formated_line( name + '=' + ','.join( [str(v) for v in value]) )
          else:
            cmd_str +=  self._formated_line( name + '=' + ' '.join( [str(v) for v in value]) )
      else:
        cmd_str +=  self._formated_line( name + '=' + str(value) )
    return cmd_str

  def _run_command(self, full_cmd_str):
    # We show command:
    self._info("Command:\n%s", full_cmd_str)
    full_cmd_str = re.sub('\\\\ *\n','', full_cmd_str )
    full_cmd_str = re.sub(' +',' ', full_cmd_str)
    self._debug("Command without spaces:\n%s", full_cmd_str)
    # And run it:
    if not self.dry_run:
      ret = self.fcn(full_cmd_str)
      if ret:
        self._error("Command failed")
      return ret
    return None

class _JobSubmitArgumentGroup( _JobSubmitActionsContainer, _ArgumentGroup ):
  def __init__(self, *args, **kw):
    self.prefix = kw.pop('prefix')
    _JobSubmitActionsContainer.__init__(self)
    _ArgumentGroup.__init__(self,*args,**kw)

class _JobSubmitMutuallyExclusiveGroup( _JobSubmitActionsContainer, _MutuallyExclusiveGroup ):
  def __init__(self, *args, **kw):
    self.prefix = kw.pop('prefix')
    _JobSubmitActionsContainer.__init__(self)
    _MutuallyExclusiveGroup.__init__(self,*args,**kw)

has_Panda = has_PBS = has_Torque = has_LSF = False

# Discover which cluster default option we should be using
import os
if os.environ.get('ATLAS_LOCAL_PANDACLI_VERSION',"") and cmd_exists('prun'):
  has_Panda = True
if cmd_exists('qsub'):
  has_PBS = has_Torque = True
if cmd_exists('bsub'):
  has_LSF = True

class ClusterManager( EnumStringification ):
  """
  Specify possible available clusters.
  """
  LSF = 1
  PBS = 2
  Torque = 2
  Panda = 3

class AvailableManager( EnumStringification ):
  """
  Specify possible available clusters.
  """
  if has_LSF: LSF = 1
  if has_PBS: PBS = 2
  if has_Torque: Torque = 2
  if has_Panda: Panda = 3

  @classmethod
  def retrieve(cls, val):
    ret = ClusterManager.retrieve( val )
    if not cls.tostring( ret ):
      raise ValueError("Cluster manager %s is not available in the current system." % ClusterManager.tostring( ret ))
    return ret

if has_Panda:
  cluster_default = ClusterManager.Panda
elif has_PBS:
  cluster_default = ClusterManager.PBS
elif has_LSF:
  cluster_default = ClusterManager.LSF
else:
  cluster_default = None

class RetrieveClusterManager( argparse.Action ):

  def __init__( self
              , dest = None
              , option_strings = []
              , nargs=None
              , const=None
              , default=None
              , type=None
              , choices=None
              , required=False
              , help=None
              , metavar=None ):
    super(RetrieveClusterManager, self).__init__( option_strings = option_strings
                                                , dest           = dest
                                                , nargs          = nargs
                                                , const          = const
                                                , default        = default
                                                , type           = type
                                                , choices        = choices
                                                , required       = required
                                                , help           = help
                                                , metavar        = metavar
                                                )

  def __call__(self, parser, namespace, value, option_string=None):
    clusterManagerConf.set( value )
    setattr( namespace, self.dest, clusterManagerConf() )


clusterManagerParser = ArgumentParser()
clusterManagerParser.add_argument( '--cluster-manager', default = cluster_default,
    type = AvailableManager, action = RetrieveClusterManager,
    help = """ Specify which cluster manager should be used in the job.""" \
      + (" Current default is: " + ClusterManager.tostring(cluster_default)) if cluster_default is not None \
      else "")

class _ConfigureClusterManager( EnumStringificationOptionConfigure ):
  """
  Singleton class for configurating the cluster-manager used for sending jobs to the cluster
  """

  _enumType = AvailableManager

  manager = property( EnumStringificationOptionConfigure.get, EnumStringificationOptionConfigure.set )

  def auto( self ):
    self._debug("Using automatic configuration for cluster-manager specification.")
    # First we discover which cluster type we will be using:
    import sys
    try:
      args, argv = clusterManagerParser.parse_known_args()
      if args.cluster_manager not in (None, NotSet):
        self.manager = args.cluster_manager
        # Consume option
        sys.argv = sys.argv[:1] + argv
      else:
        self.manager = cluster_default
    except (ArgumentError, ValueError) as e:
      self._debug("Ignored argument parsing error:\n %s", e )
      self.manager = cluster_default

ClusterManagerConfigure = Holder( _ConfigureClusterManager() )

clusterManagerConf = ClusterManagerConfigure()
