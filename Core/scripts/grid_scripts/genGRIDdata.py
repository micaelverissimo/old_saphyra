#!/usr/bin/env python

from TuningTools.parsers import ArgumentParser, argparse, createDataParser, TuningToolGridNamespace

from RingerCore import emptyArgumentsPrintHelp, ioGridParser, loggerParser

## Create our paser
# Add base parser options (this is just a wrapper so that we can have this as
# the first options to show, as they are important options)
parentParser = ArgumentParser( add_help = False )
parentParser.add_argument('-s','--inDS-SGN', action='store', 
    metavar='inDS_SGN', required = True, nargs='+', dest = 'grid_inDS', 
    help = "The signal files that will be used to tune the discriminators")
parentParser.add_argument('-b','--inDS-BKG', action='store', 
    metavar='inDS_BKG', required = True, nargs='+',
    help = "The background files that will be used to tune the discriminators")
## The main parser
parser = ArgumentParser(description = 'Generate input file for TuningTool on GRID',
                                 parents = [createDataParser, parentParser, ioGridParser, loggerParser],
                                 conflict_handler = 'resolve')
## Change parent options
# Hide sgnInputFiles
parser.add_argument('--sgnInputFiles', action='store_const', 
    metavar='SignalInputFiles', required = False, const = '', default = '',
    help = argparse.SUPPRESS)
# Hide bkgInputFiles
parser.add_argument('--bkgInputFiles', action='store_const', 
    metavar='BackgroundInputFiles', required = False, const = '', default = '',
    help = argparse.SUPPRESS)
# Hide output
parser.add_argument('--output', action='store_const', 
    default = '', const = '', required = False,
    help = argparse.SUPPRESS)
# Hide forceStaged and make it always be true
parser.add_argument('--forceStaged', action='store_const',
    required = False,  dest = 'grid_forceStaged', default = False, 
    const = False, help = argparse.SUPPRESS)
# Hide forceStagedSecondary and make it always be true
parser.add_argument('--forceStagedSecondary', action='store_const',
    required = False, dest = 'grid_forceStagedSecondary', default = False,
    const = False, help = argparse.SUPPRESS)
# Make inDS point to inDS-SGN if used
parser.add_argument('--inDS','-i', action='store', nargs='?',
    required = False, default = False,  dest = 'grid_inDS',
    help = argparse.SUPPRESS)
# Make nFiles not usable by user
parser.add_argument('--nFiles', action='store_const',
    required = False, default = 0, const = 0, dest = 'grid_nFiles',
    help = argparse.SUPPRESS)
# Make nFilesPerJob not usable by user
parser.add_argument('--nFilesPerJob', nargs='?', type=int,
    required = False, dest = 'grid_nFilesPerJob',
    help = argparse.SUPPRESS)
# Make nJobs not usable by user
parser.add_argument('--nJobs', action='store_const',
    required = False, default = 1, const = 1, dest = 'grid_nJobs',
    help = argparse.SUPPRESS)
# Make extFile not usable by user
parser.add_argument('--extFile', action='store_const', 
    required = False, dest = 'grid_extFile', default = '', const = '',
    help = argparse.SUPPRESS)
# Make secondary datasets not usable by user
parser.add_argument('--secondaryDSs', action='store_const',
    required = False, default = '', const = '', dest = 'grid_secondaryDS',
    help = argparse.SUPPRESS )
# Make outputs not usable by user
parser.add_argument('--outputs', action='store_const',
    required = False, default = '"tuningData*"', const = '"tuningData*"', 
    dest = 'grid_outputs',
    help = argparse.SUPPRESS )
# Force secondary to be reusable:
parser.add_argument('--reusableSecondary', action='store_const',
    required = False, default = 'BKG', const = 'BKG', dest = 'grid_reusableSecondary',
    help = """Allow reuse secondary dataset.""")

emptyArgumentsPrintHelp(parser)

# Retrieve parser args:
args = parser.parse_args( namespace = TuningToolGridNamespace('prun') )
from RingerCore.Logger import Logger
mainLogger = Logger.getModuleLogger( __name__, args.output_level )
# Treat special argument
if len(args.reference) > 2:
  mainLogger.fatal("--reference set to multiple values: %r" % args.reference, ValueError)
if len(args.reference) is 1:
  args.reference.append( args.reference[0] )
if args.operation != 'Offline' and not args.treePath:
  mainLogger.fatal("If operation is not set to Offline, it is needed to set the TreePath manually.")

if ( len(args.inDS_BKG) > 1 or len(args.grid_inDS) > 1):
  mainLogger.fatal("Cannot use multiple datasets in this version.", NotImplementedError)

from subprocess import check_output

# TODO For now we only support one container for signal and one for background.
# We need to change it so that we can input multiple containers. This can be
# simply done by adding them as secondary datasets, copying the idea as done
# below (and looping through the input arguments:
def getNFiles( ds ):
  if ds[-1] != '/': ds += '/'
  mainLogger.debug("Retriving \"%s\" number of files...", ds)
  output=check_output('dq2-ls -n %s | cut -f1' % ds, shell=True)
  mainLogger.debug("Retrieved command output: %s", output[:-1])
  try:
    nFiles=int(output)
    if nFiles < 1:
      mainLogger.fatal(("Couldn't retrieve the number of files on the output "
        "dataset %s. The output retrieven was: %s.") % ( ds , output ) )
    if args.gridExpand_debug and nFiles > 3:
      nFiles = 3
    return nFiles
  except ValueError:
    mainLogger.fatal(("Seems that grid environment is not set. Try again after "
        "setting grid environment."))

# Fix primary dataset number of files:
nSgnFiles = getNFiles( args.grid_inDS[0] )
args.grid_nFiles = nSgnFiles
args.grid_nFilesPerJob = nSgnFiles

# Now work with secondary dataset:
nBkgFiles = getNFiles( args.inDS_BKG[0] )

# Fix secondaryDSs string:
args.grid_secondaryDS="BKG:%d:%s" % (nBkgFiles, args.inDS_BKG[0])

from RingerCore.util import printArgs, conditionalOption
printArgs( args, mainLogger.debug )

# Prepare to run
args.setExec("""source ./setrootcore.sh; 
               {gridCreateData}
                 --sgnInputFiles %IN
                 --bkgInputFiles %BKG
                 --operation {operation}
                 --reference {referenceSgn} {referenceBkg}
                 {treePath};
             """.format( gridCreateData = "\$ROOTCOREBIN/user_scripts/TuningTools/run_on_grid/gridCreateData.py",
                         operation=args.operation,
                         referenceSgn=args.reference[0],
                         referenceBkg=args.reference[1],
                         treePath = conditionalOption('--treePath ', args.treePath),
                         ) 
            )

# And run
args.run_cmd()
