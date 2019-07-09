#!/usr/bin/env python

from Gaugi  import LoggingLevel, Logger, expandFolders
import argparse
import os
mainLogger = Logger.getModuleLogger("prometheus.job")
parser = argparse.ArgumentParser(description = '', add_help = False)
parser = argparse.ArgumentParser()

parser.add_argument('-f','--files', action='store', 
        dest='files', required = True, nargs='+',
            help = "The input files.")

parser.add_argument('-d','--dataset', action='store', 
        dest='dataset', required = True,
            help = "The dataset name.")

parser.add_argument('-r','--rse', action='store', 
        dest='rse', required = False, default = 'CERN-PROD_SCRATCHDISK',
            help = "The number of threads")

parser.add_argument('-l','--add_rules', action='store_true', 
        dest='add_rules', required = False, default = False,
            help = "Add rules...")

rules = [
  'BNL-OSG2_SCRATCHDISK',
  'CERN-PROD_SCRATCHDISK',
  'FZK-LCG2_SCRATCHDISK',
  'DESY-HH_SCRATCHDISK',
  'MWT2_UC_SCRATCHDISK',
]

from Gaugi import emptyArgumentsPrintHelp
emptyArgumentsPrintHelp(parser)



args = parser.parse_args()
# get user name
user = os.environ['USER']
# make the full dataset name
scope = 'user.%s' % user

command_add_dataset = "rucio add-dataset user.{USER}:{DATASET}"
command_upload      = "rucio --verbose upload --rse {RSE} --scope {SCOPE} {FILE} user.{USER}:{DATASET}"
command_attach      = "rucio attach user.{USER}:user.{USER}.{DATASET} user.{USER}:{DATASET}"
command_add_rule    = 'rucio add-rule --lifetime "$((120*24*3600))" user.{USER}:{DATASET} 1 {RULE}'

files = expandFolders( args.files )


mainLogger.info('Creating the dataset...')
os.system( command_add_dataset.format( DATASET = args.dataset, USER=user ) )

for file in files:
  mainLogger.info('Upload %s', file)
  cmd = command_upload.format( DATASET = args.dataset, FILE=file, RSE=args.rse, SCOPE=scope, USER=user) 
  print(cmd)
  os.system(cmd)
  #cmd = command_attach.format( USER=user, DATASET=args.dataset)  
  #print(cmd)
  #os.system(cmd)


if args.add_rules:
  for rule in rules:
    cmd = command_add_rule.format( DATASET = args.dataset, USER=user, RULE=rule )
    print(cmd)
    os.system(cmd)




