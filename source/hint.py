#! /usr/bin/env python
"""Hyperinterval finder

Finds hyperintervals in a (numerical) database that have high density.

(c) 2011 Jouke Witteveen
"""

# Units are nats when using natural logarithms
from math import log
from sys import float_info
import argparse
import random


### ARGUMENT PARSING AND VALIDATION ###

parser = argparse.ArgumentParser( description = "Hyperinterval finder." )
parser.add_argument( '-s', '--sample', metavar = 'SIZE', type = int,
                     required = True, help = "sample size to determine hyperinterval boundaries" )
parser.add_argument( 'database', type = argparse.FileType( 'r' ),
                     help = "database file containing one line per entry" )
parser.add_argument( '-p', '--perseverance', type = int, default = 0,
                     help = "eagerness to not end up in local minima" )
parser.add_argument( '-l', '--log', metavar = 'FILE',
                     type = argparse.FileType( 'w' ), required = False,
                     help = "log file to record all considered hyperintervals" )
args = parser.parse_args()

db = tuple( tuple( map( float, row.split() ) ) for row in args.database )
if not ( 3 <= args.sample <= len( db ) ):
  print( "sample size should be between 3 and the number of records in the database" )
  raise SystemExit
if not ( 0 <= args.perseverance <= args.sample - 3 ):
  print( "perseverance should be between 0 and the sample size minus three" )
  raise SystemExit
sample = random.sample( db, args.sample )
debug = args.log


### DATABASE DEPENDENT FUNCTIONS ###

def measure_init( db, sample ):
  """Establish a bounding box around the database and normalizing factors for
     all columns, so that distances become comparable."""
  global db_scale
  db_lb, db_ub = bounding_hint( *db )
  db_scale = tuple( map( lambda x, y: abs( x - y ), db_lb, db_ub ) )
  # Runtime is quadratic in the sample size. That is slow.
  hint_init.candidates = sorted( [ ( a, b ) for a in sample for b in sample
                                                            if not a is b ],
                                 key = lambda ab: distance( *ab ) )
  return db_lb, db_ub


def distance( a, b ):
  """The distance between two database records."""
  # A rectilinear distance suits the model
  return sum( map( lambda x, y, z: abs( ( x - y ) / z ), a, b, db_scale ) )


def volume( a, b, epsilon = float_info.epsilon**( 1 / len( db[0] ) ) ):
  """The volume of the hyperinterval between two database records.

     Subspaces are given a 'thickness' of epsilon.
     A record with itself yields a hyperinterval of volume 0.
     Two identical records yield a hyperinterval of strictly positive volume.
     The volume of the bounding box around the database is normalized to 1."""
  if a is b: return 0
  V = 1
  for side in map( lambda x, y, z: abs( ( x - y ) / z ), a, b, db_scale ):
    V *= ( side or epsilon )
  return max( V, float_info.min )


def hint_init( sample, *exclude ):
  """The hyperinterval is initialized as the region between the two sampled
     points that are closest together.

     Points in excluded intervals are not considered."""
  global hint_origin
  exclude = [ a for a in exclude if a not in hint_init.excluded ]
  hint_init.candidates = [ ( x, y ) for x, y in hint_init.candidates
                           if not is_covered( x, *exclude ) and
                              not is_covered( y, *exclude ) ]
  hint_init.excluded.extend( exclude )
  if len( hint_init.candidates ) == 0:
    print( "Sample exhausted." )
    raise SystemExit
  hint_origin = tuple( map( lambda x, y: ( x + y ) / 2,
                            *hint_init.candidates[0] ) )
  return bounding_hint( *hint_init.candidates[0] )
hint_init.excluded = list()


### INVARIABLE MACHINERY ###

def bounding_hint( *a ):
  """The smallest hyperinterval covering all arguments."""
  return tuple( map( min, *a ) ), tuple( map( max, *a ) )


def is_covered( a, *hints ):
  """Checks whether a database record is covered by any of the hyperintervals
     provided."""
  for hint in hints:
    for i, x in enumerate( a ):
      if not ( hint[0][i] <= x <= hint[1][i] ): break
    else: return True
  return False


def covered( hint, sample = None ):
  """The number of records covered by the hyperinterval."""
  count = 0
  for row in ( sample or db ):
    if is_covered( row, hint ): count += 1
  return count


def comp_hint_comp( hint ):
  """Comparative hint complexity calculation."""
  inside_count = covered( hint )
  outside_count = len( db ) - inside_count
  hint_size = volume( hint[0], hint[1] )
  complexity = \
    outside_count * log( ( size - hint_size ) / outside_count ) \
    + inside_count * log( hint_size / inside_count )
  if debug:
    debug.write( "{}\t{}\t{}\t{}\t{}\n".format(
      -distance( hint[0], hint_origin ), distance( hint[1], hint_origin ),
      hint_size, inside_count / len( db ), complexity ) )
  return complexity


# BUG: The hint could potentially cover the entire database (out of the model)!
# BUG: The boundaries are often found in low density regions. The sample is not
#      the most accurate source of coordinates in those situations.
def grow_hint( hint, sample ):
  """Grow the hyperinterval to its maximal informativeness."""
  complexity = comp_hint_comp( hint )
  sample_out = [ row for row in sample if not is_covered( row, hint ) ]
  perseverance = args.perseverance
  while sample_out:
    candidate = sample_out.pop(
      min( enumerate( distance( row, hint[0] ) + distance( row, hint[1] )
                      for row in sample_out ), key = lambda a: a[1] )[0] )
    hint_candidate = tuple( map( min, candidate, hint[0] ) ), \
                     tuple( map( max, candidate, hint[1] ) )
    complexity_candidate = comp_hint_comp( hint_candidate )
    if complexity_candidate < complexity:
      complexity, hint = complexity_candidate, hint_candidate
      perseverance = args.perseverance
    else:
      perseverance -= 1
      if perseverance < 0: break
  else:
    print( "Sample exhausted. "
           "Try a larger sample, or lower your perseverance." )
  return hint


size = volume( *measure_init( db, sample ) )
if __name__ == "__main__":
  # If the volume is normalized to 1, the following prints 0.
  # This is not a bug.
  print( "Single uniform complexity:                   ",
         len( db ) * log( size ) )
  """Discretization is completely ignored.
     Partly this can be justified (log(dx) is model independent).
     The cost of specifying the luckiness region is also ignored.
     This can hardly be justified.
     For now: just add a constant C for all this ;-)."""
  # Taking into account model selection cost
  #print( "Comparative single uniform sample complexity:",
  #       len( sample ) * log( size / len( sample ) ) )
  print( "Comparative single uniform complexity:       ",
         len( db ) * log( size / len( db ) ) )


def run():
  global hint_history
  run.iteration += 1
  if __name__ != "__main__":
    print( "=> RUN", run.iteration )
  hint = hint_init( sample, *hint_history )
  if debug:
    if run.iteration == 1:
      debug.write( "#left\tright\tsize\tcoverage\tcomplexity\n" )
    else: debug.write( "\n\n" )
  print( "Initial hyperinterval:         ", hint )
  hint = grow_hint( hint, sample )
  print( "Most informative hyperinterval:", hint )
  hint_history.append( hint )
run.iteration = 0


hint_history = list()
if __name__ == "__main__": run()
