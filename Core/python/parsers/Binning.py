__all__ = ['addBinningOptions']

from RingerCore import NotSet
def addBinningOptions( parser, label = '' ):
  parser.add_argument('--%set-bins' % (label + '-' if label else '')
          , nargs='+', default = NotSet, type = int,
          help = """ The et bins to use within this job. 
              When not specified, all bins available on the file will be tuned
              separately.
              If specified as a integer or float, it is assumed that the user
              wants to run the job only for the specified bin index.
              In case a list is specified, it is transformed into a
              MatlabLoopingBounds, read its documentation on:
                http://nbviewer.jupyter.org/github/wsfreund/RingerCore/blob/master/readme.ipynb#LoopingBounds
              for more details.
          """)
  parser.add_argument('--%seta-bins' % (label + '-' if label else ''), nargs='+'
          , default = NotSet, type = int,
          help = """ The eta bins to use within this job. Check %s
              help for more information.  """ % ('--%set-bins' % (label + '-' if label else '')) )
