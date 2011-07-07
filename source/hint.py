#! /usr/bin/env python
"""Hyperinterval finder

Finds hyperintervals in a (numerical) database that have high density.

(c) 2011 Jouke Witteveen
"""

# Units are nats when using natural logarithms
from math import log
import argparse
import operator
import random
itemgetter = operator.itemgetter


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

#db = tuple( ( x, ) for x in range( 0, 10000, 10 ) )
#db = tuple( ( random.gauss( 0, 1 ), ) for i in range( 10000 ) )
db = tuple( tuple( float( col ) for col in row.split() )
            for row in args.database )
if not ( 3 <= args.sample <= len( db ) ):
  print( "sample size should be between 3 and the number of records in the database" )
  raise SystemExit
if not ( 0 <= args.perseverance <= args.sample - 3 ):
  print( "perseverance should be between 0 and the sample size minus three" )
  raise SystemExit
sample = random.sample( db, args.sample )
debug = args.log


### DATABASE DEPENDENT FUNCTIONS ###

def measure_init( db ):
  """Establish a bounding box around the database and normalizing factors for
     all columns, so that distances become comparable."""
  global db_scale
  db_lb = tuple( min( db, key = itemgetter( i ) )[i]
                 for i in range( len( db[0] ) ) )
  db_ub = tuple( max( db, key = itemgetter( i ) )[i]
                 for i in range( len( db[0] ) ) )
  db_scale = tuple( map( lambda x, y: abs( x - y ), db_lb, db_ub ) )
  return db_lb, db_ub


def distance( a, b ):
  """The distance between two database records."""
  # A rectilinear distance suits the model
  return sum( map( lambda x, y, z: abs( ( x - y ) / z ), a, b, db_scale ) )


def volume( a, b ):
  """The volume of the hypercube between two database records.

     Subspaces are given a 'thickness' of epsilon, except for the point
     subspace, which is given volume 0.
     The volume of the bounding box around the database is normalized to 1."""
  if a == b: return 0
  epsilon = .000001
  V = 1
  for side in map( lambda x, y, z: abs( ( x - y ) / z ), a, b, db_scale ):
    V *= ( side or epsilon )
  return V


def hint_init( sample ):
  """The hyperinterval is initialized as the region between the two sampled
     points that are closest together."""
  return min( ( distance( a, b ), ( a, b ) )
              for a in sample for b in sample if a != b )[1]


def covered( hint, sample = None ):
  """The number of records covered by the hyperinterval.

     This is a candidate for optimization.
     The hint only grows so it should be possible to make it incremental."""
  count = 0
  for row in ( sample or db ):
    for i, x in enumerate( row ):
      if not ( hint[0][i] <= x <= hint[1][i] ): break
    else: count += 1
  return count


### INVARIABLE MACHINERY ###

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


size = volume( *measure_init( db ) )
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

hint = hint_init( sample )
hint_origin = tuple( map( lambda x, y: ( x + y ) / 2, *hint ) )
if debug:
  debug.write( "#left\tright\tsize\tcoverage\tcomplexity\n" )
print( "Initial hyperinterval:         ", hint )

# Next: grow the hint.
# BUG: The hint could potentially cover the entire database (out of the model)!
# BUG: The boundaries are often found in low density regions. The sample is not
#      the most accurate source of coordinates in those situations.

## Quick hack-up, using that the sample is sorted
##for ub in sample[1:]:
#for ub in sample[sample.index( hint[1] ):]:
#  #for lb in reversed( sample[:sample.index( ub )] ):
#  for lb in reversed( sample[:sample.index( hint[0] ) + 1] ):
#    complexity = comp_hint_comp( [lb, ub] )
#  if debug: debug.write( "\n\n" )

# More decent attempt to do the above
complexity = comp_hint_comp( hint )
sample_out = [ row for row in sample if row < hint[0] or row > hint[1] ]
perseverance = args.perseverance
while sample_out:
  candidate = sample_out.pop(
    min( enumerate( distance( row, hint[0] ) + distance( row, hint[1] )
                    for row in sample_out ), key = itemgetter( 1 ) )[0] )
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
  print( "Sample exhausted. Try a larger sample, or lower your perseverance." )
print( "Most informative hyperinterval:", hint )
