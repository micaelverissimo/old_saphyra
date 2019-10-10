__all__ = ['__version__']

# Main package modules:
from . import coreDef
__all__.extend( coreDef.__all__              )
from .coreDef import *
#
#from . import CreateData
#__all__.extend( CreateData.__all__           )
#from .CreateData import *
##
#from . import CreateTuningJobFiles
#__all__.extend( CreateTuningJobFiles.__all__ )
#from .CreateTuningJobFiles import *
##
#from . import Neural
#__all__.extend( Neural.__all__               )
#from .Neural import *
##
#from . import PreProc
#__all__.extend( PreProc.__all__              )
#from .PreProc import *
##
#from . import SecPreProc
#__all__.extend( SecPreProc.__all__              )
#from .SecPreProc import *
##
#from . import TuningJob
#__all__.extend( TuningJob.__all__            )
#from .TuningJob import *
##
#from . import CrossValid
#__all__.extend( CrossValid.__all__           )
#from .CrossValid import *
##
#from . import DataCurator
#__all__.extend( DataCurator.__all__           )
#from .DataCurator import *
##
#from . import TuningWrapper
#__all__.extend( TuningWrapper.__all__        )
#from .TuningWrapper import *
##
#from . import DecisionMaking
#__all__.extend( DecisionMaking.__all__       )
#from .DecisionMaking import *
##
#from . import CrossValidStat
#__all__.extend( CrossValidStat.__all__       )
#from .CrossValidStat import *
##
#from . import SubsetGenerator
#__all__.extend( SubsetGenerator.__all__      )
#from .SubsetGenerator import *
#
#from . import dataframe
#__all__.extend( dataframe.__all__            )
#from dataframe import *
#
## parsers sub-package modules
#from . import parsers
#__all__.extend( parsers.__all__              )
#from parsers import *
#
#from . import export
#__all__.extend( export.__all__           )
#from export import *
#
#from . import tableboard
#__all__.extend( tableboard.__all__           )
#from tableboard import *



from Gaugi import masterLevel
masterLevel.mute( 'StoreGate'                )
__version__ = 1.0
#__version__ = TuningToolsGit.tag


# make compatible with old pickle files
import Gaugi as Gaugi
import sys
sys.modules['RingerCore']=Gaugi


