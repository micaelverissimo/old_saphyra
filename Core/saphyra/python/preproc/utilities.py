
__all__ = ["GetRingerBounds"]


def GetRingerBounds( layer ):
  if layer == 1: # PS
    bounds = (0,7)
  elif layer == 2: # EM1
    bounds = (8, 71)
  elif layer == 3: # EM2
    bounds = (72, 79)
  elif layer == 4: # EM3
    bounds = (80,87)
  elif layer == 5: # HAD1
    bounds = (88,91)
  elif layer == 6: # HAD2
    bounds = (92,95)
  elif layer == 7: # HAD3
    bounds = (96,99)
  else: # All concatened rings
    bounds = (0,99)
  number_of_rings = bounds[1]-bounds[0] +1
  return bounds, number_of_rings


