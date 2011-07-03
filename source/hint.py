#! /usr/bin/env python
"""Hyperinterval finder

Finds hyperintervals in a (numerical) database that have high density.

(c) 2011 Jouke Witteveen
"""

# Units are nats
from math import log
import argparse
import random

parser = argparse.ArgumentParser( description = 'Hyperinterval finder.' )
parser.add_argument( '-s', '--sample', metavar = 'SIZE', type = int,
                     required = True, help = 'sample size to determine initial interval boundaries' )
parser.add_argument( 'database', type = open, help = 'database file containing one line per entry' )
args = parser.parse_args()

# In this form the database is one dimensional.
db = tuple( float( row ) for row in args.database.readlines() )
sample = random.sample( db, args.sample )


"""The distance between two database records is use case dependent.
   Write your own distance function!"""
def distance( a, b ):
  # Very one dimensional...
  return abs( a - b )


"""The hyperinterval is initialized as the region between the two sampled
   points that are closest together."""
def hint_init():
  # In the one dimensional case sorting is possible (and handy).
  sample.sort()
  deltas = [ a - b for a, b in zip( sample[1:], sample[:-1] ) ]
  size = min( deltas )
  return sample[deltas.index( size ):][:2], size


"""The number of records covered by the hyperinterval.
   This is a candidate for optimization (i.e. make it incremental)"""
def covered( hint ):
  count = 0
  for record in db:
    if hint[0] <= record <= hint[1]:
      count += 1
  return count


# TODO: very 1D thinking over here
lower = min( db )
upper = max( db )
size = distance( lower, upper )
print( "Single uniform complexity:                   ",
       len( db ) * log( size ) )
# Taking into account model selection cost
## Discretization is completely ignored.
## Partly this can be justified (log(dx) is model independent).
## The cost of specifying the luckiness region is also ignored.
## This can hardly be justified.
## For now: just add a constant C for all this ;-).
print( "Comparative single uniform sample complexity:",
       len( sample ) * log( size / len( sample ) ) )
print( "Comparative single uniform complexity:       ",
       len( db ) * log( size / len( db ) ) )

hint, hint_size = hint_init()
print( "Comparative hint sample complexity:          ",
       ( len( sample ) - 2 ) * log( ( size - hint_size ) / len( sample ) )
       + 2 * log( hint_size / 2 ) )
inside_count = covered( hint )
print( "Comparative hint complexity:                 ",
       ( len( db ) - inside_count ) * log( ( size - hint_size ) / len( db ) )
       + inside_count * log( hint_size / inside_count ) )

# Next: grow(/shrink?) the hint.

