
__all__ = [ "CrossValMethod" ]

from Gaugi import EnumStringification


# used in the archieve procedure
class CrossValMethod( EnumStringification ):
  KFold = 0
  LeaveOneOut = 1
  StratifiedKFold = 2


