# Get all files name for the dataset (ds) passed
def get_list_files( ds ):
  import os
  print(('Getting list of files in %s')%(ds))
  command = ('rucio list-files %s | cut -f2 -d  "|" >& rucio_list_files.txt') % (ds) 
  print(command)
  os.system(command)
  files = list()
  with open('rucio_list_files.txt') as f:
    lines = f.readlines()
    for line in lines:  
      # remove skip line
      line = line.replace('\n','')
      # remove spaces
      for s in line:  
        if ' ' in line:  line = line.replace(' ','')
      # remove corrupt files
      if line.endswith('.2'):  
        print(('Remove corrupt file: %s')%(line))
        continue
      files.append( line )
    # remove junk lines
    files.pop(0);  files.pop(-1)
    files.pop(0);  files.pop(-1)
    files.pop(0);  files.pop(-1)
    files.sort()

  return files


f=  get_list_files("user.jodafons.job_config.ringer.mlp1to20.10sorts.10inits")
from pprint import pprint
pprint(f)

print(len(f))
