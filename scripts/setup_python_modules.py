

import glob
import os
CURRENT_PATH = os.environ["CMAKE_PROJECT_PATH"]
stage1 = glob.glob(CURRENT_PATH+'/*/python')
stage2 = glob.glob(CURRENT_PATH+'/*/*/python')
python_paths = stage1+stage2


for pypath  in python_paths:
  if 'build' in pypath: continue
  PATH =  pypath
  TARGET = pypath.split('/')
  TARGET = TARGET[len(TARGET)-2]
  command = 'ln -sf {PATH} {TARGET}'.format(PATH=PATH, TARGET=TARGET)
  print command
  os.system(command)
