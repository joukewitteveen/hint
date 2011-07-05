#! /usr/bin/env python
"""Hyperinterval finder

Finds hyperintervals in a (numerical) database that have high density.

(c) 2011 Jouke Witteveen
"""

# Units are nats when using natural logarithms
from math import log
from operator import itemgetter
import argparse
import random

parser = argparse.ArgumentParser( description = "Hyperinterval finder." )
parser.add_argument( '-s', '--sample', metavar = 'SIZE', type = int,
                     required = True, help = "sample size to determine hyperinterval boundaries" )
parser.add_argument( 'database', type = open, help = "database file containing one line per entry" )
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
sample = random.sample( db, args.sample )
debug = args.log


### DATABASE DEPENDENT FUNCTIONS ###

def distance( a, b ):
  """The distance between two database records."""
  # TODO: Very one dimensional...
  return abs( a[0] - b[0] )


def volume( a, b ):
  """The hypervolume of the hypercube between two database records."""
  # TODO: Also very one dimensional...
  return distance( a, b )


def hint_init():
  """The hyperinterval is initialized as the region between the two sampled
     points that are closest together."""
  # TODO: Sorting is handy, but only works in the one dimensional case...
  sample.sort()
  deltas = [ distance( a, b ) for a, b in zip( sample[1:], sample[:-1] ) ]
  index, size = min( enumerate( deltas ), key = itemgetter( 1 ) )
  return tuple( sample[index:index + 2] ), size


def covered( hint, sample = None ):
  """The number of records covered by the hyperinterval.
     This is a candidate for optimization (i.e. make it incremental)."""
  count = 0
  for row in ( sample or db ):
    # TODO: Also one dimensional...
    if hint[0] <= row <= hint[1]:
      count += 1
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
  if( debug ):
    debug.write( "{}\t{}\t{}\t{}\t{}\n".format( hint[0][0], hint[1][0],
                                                hint_size,
                                                inside_count / len( db ),
                                                complexity ) )
  return complexity


# TODO: one dimensional thinking over here (min/max)
size = volume( min( db ), max( db ) )
print( "Single uniform complexity:                   ",
       len( db ) * log( size ) )
# Taking into account model selection cost
"""Discretization is completely ignored.
   Partly this can be justified (log(dx) is model independent).
   The cost of specifying the luckiness region is also ignored.
   This can hardly be justified.
   For now: just add a constant C for all this ;-)."""
print( "Comparative single uniform sample complexity:",
       len( sample ) * log( size / len( sample ) ) )
print( "Comparative single uniform complexity:       ",
       len( db ) * log( size / len( db ) ) )

hint, hint_size = hint_init()
if( debug ):
  debug.write( "#left\tright\tsize\tcoverage\tcomplexity\n" )
print( "Initial hyperinterval:    ", hint )
print( "Size of the hyperinterval:", hint_size )

# Next: grow the hint.
# BUG: the hint could potentially cover the entire database (out of the model)!

## Quick hack-up, using that the sample is sorted
##for ub in sample[1:]:
#for ub in sample[sample.index( hint[1] ):]:
#  #for lb in reversed( sample[:sample.index( ub )] ):
#  for lb in reversed( sample[:sample.index( hint[0] ) + 1] ):
#    complexity = comp_hint_comp( [lb, ub] )
#  if( debug ): debug.write( "\n\n" )

# More decent attempt to do the above
complexity = comp_hint_comp( hint )
sample_out = [ row for row in sample if row < hint[0] or row > hint[1] ]
perseverance = args.perseverance
while( sample_out ):
  candidate = sample_out.pop(
    min( enumerate( distance( row, hint[0] ) + distance( row, hint[1] )
                    for row in sample_out ), key = itemgetter( 1 ) )[0] )
  if( candidate < hint[0] ):
    hint_candidate = candidate, hint[1]
  else:
    hint_candidate = hint[0], candidate
  complexity_candidate = comp_hint_comp( hint_candidate )
  if( complexity_candidate < complexity ):
    complexity, hint = complexity_candidate, hint_candidate
    perseverance = args.perseverance
  else:
    perseverance -= 1
    if( perseverance < 0 ): break
else:
  print( "Sample exhausted. Try a larger sample, or lower your perseverance." )
print( "Most informative hyperinterval:", hint )
