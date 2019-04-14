#!/usr/bin/env python
from RingerCore import Logger, LoggerNamespace, ArgumentParser, emptyArgumentsPrintHelp

parser    = ArgumentParser()

parser.add_argument('-o', '--output',action='store', default="merge.root", 
                    help='output merged file')
parser.add_argument('-n', '--nFilesPerMerge', type=int, default=2, 
                    help='Number of files per merge')
parser.add_argument('-i', '--input' ,action='store', nargs='+',required=True, 
                    help='input file')


mainLogger = Logger.getModuleLogger(__name__)

#***************************** Main ******************************
emptyArgumentsPrintHelp( parser )

args = parser.parse_args( namespace = LoggerNamespace() )
mainLogger.info('Starting merging files...')
poutput = args.output.replace('.root','')

import numpy as np
mainLogger.info(('Trying to merge %d files')%(len(args.input)))

files = args.input
files.sort()
imerge=0

all_merged_files=str()
while len(files) > 0:

  group=str()
  for count in range(args.nFilesPerMerge):
    if len(files) > 0:
      group += ' ' + files.pop(0)
    else: # Protection because zero file
      break

  merged_name  = ('%s.%d.root')%(poutput ,imerge)
  command = ('hadd %s %s')%(merged_name,group)
  mainLogger.info(command)
  os.system(command)
  imerge+=1
  all_merged_files += ' '+merged_name
# Loop over input files

command = ('hadd %s %s')%(args.output ,all_merged_files)
os.system(command)


