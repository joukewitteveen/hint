"""Generic database measurement

General purpose hyperinterval tools.
This file is part of Hint, the hyperinterval finder.

(c) 2011 Jouke Witteveen
"""

# Units are nats when using natural logarithms
from math import log


def bounding_hint( *a ):
  """The smallest hyperinterval covering all arguments."""
  return tuple( map( min, *a ) ), tuple( map( max, *a ) )


def is_covered( a, hint ):
  """Whether record a is covered by the hyperinterval."""
  for i, x in enumerate( a ):
    if not ( hint[0][i] <= x <= hint[1][i] ): return False
  return True


def covered( hint, db ):
  """The number of records covered by the hyperinterval."""
  count = 0
  for row in db:
    if is_covered( row, hint ): count += 1
  return count

