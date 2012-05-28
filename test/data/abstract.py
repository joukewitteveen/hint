#! /usr/bin/env python

fr = open( 'abstracts.sparse', 'r' )
fw = open( 'abstracts.full', 'w' )

for line in fr:
  record = ['0'] * 3933
  for i in line.split():
    record[int(i)] = '1'
  fw.write('\t'.join(record)+'\n')

