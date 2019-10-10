__all__ = ['DataCurationParser', 'dataCurationParser']

from Gaugi import ArgumentParser, BooleanStr, NotSet
from TuningTools.CrossValid import CrossValidMethod
from TuningTools.dataframe.EnumCollection  import RingerOperation

################################################################################
# Create tuningJob file related objects
################################################################################
def DataCurationParser( tuningDataRequired = True, extraDescr = '' ):
  dataCurationParser = ArgumentParser(add_help = False
                                  ,description = 'Apply transformation and cross-validation to tuning data.')
  tuningDataArgs = dataCurationParser.add_argument_group( "Data curation required arguments", extraDescr)
  tuningDataArgs.add_argument('-d', '--data', action='store', nargs='+',
      metavar='data', required = tuningDataRequired, default = NotSet,
      help = "The data file that will be used to tune the discriminators")
  tuningOptArgs = dataCurationParser.add_argument_group( "Data curation optional arguments", extraDescr)
  tuningOptArgs.add_argument('-op','--operation', default = None, type=RingerOperation,
                       required = False,
                       help = """The Ringer operation determining in each Trigger
                       level or what is the offline operation point reference.""" )
  tuningOptArgs.add_argument('-r','--refFile', default = None,
                       help = """The Ringer references to set the discriminator point.""")
  tuningOptArgs.add_argument('--saveMatPP', action='store', default = NotSet, type=BooleanStr,
      help = """Whether to save pre-processings to a matlab file.""")
  #tuningOptArgs.add_argument('--savePPFile', action='store', default = NotSet, type=BooleanStr,
  #    help = """Whether to save pre-processings to pre-processed version of the tuning data.""")
  crossValArgs = dataCurationParser.add_argument_group( "Cross-validation configuration", extraDescr)
  # TODO Make these options mutually exclusive
  crossValArgs.add_argument('-x', '--crossFile', action='store', default = NotSet,
      help = """The cross-validation file path, pointing to a file
              created with the create tuning job files""")
  crossValArgs.add_argument('-xc', '--clusterFile', action='store', default = NotSet,
      help = """The subset cross-validation file path, pointing to a file
              created with the create tuning job files""")
  crossValArgs.add_argument('-xm', '--crossValidMethod', type=CrossValidMethod, default = NotSet,
      help = """Which cross validation method to use when no cross-validation
                object was specified.""")
  crossValArgs.add_argument('-xs', '--crossValidShuffle', type=BooleanStr, default = NotSet,
      help = """Which cross validation method to use when no cross-validation
                object was specified.""")
  ppArgs = dataCurationParser.add_argument_group( "Pre-processing configuration", extraDescr)
  ppArgs.add_argument('-pp','--ppFile', default = NotSet,
          help = """ The file containing the pre-processing collection to apply. """)
  return dataCurationParser
dataCurationParser = DataCurationParser()
