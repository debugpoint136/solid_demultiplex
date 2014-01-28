#!/bin/python

#+-----------------------------------+
#+------sOLid demultiplexing---------+
#+-----------------------------------+
#+-----------------------------------+
#+----------Jan 20th, 2014-----------+
#------------------------------------+


import os,sys,re,regex

#Edit --1 : Modified the script to save the list of headers into a list
#-----------Read the above list and extract just those lines from f3.qual, f5.csfasta and f5.qual

# Edit -2 : 23 Jan ,2014 : 11:25 EST
#+---- 1. Removed slurp mode of file intake
#+-----2. Replaced array with hash lookup

#Edit - 3 :  28 Jan, 2014 : 04:25 EST
#+-----1. Changed the script to accept only 1 barcode
#+-----2. Allowed 2 mismatches in the barcode detection

# TBD : Chunkify the whole process and parallelize it

if(len(sys.argv) != 7):
	print "-" * 150
	print "USAGE : python solid_demultiplex_pipeline.py <BARCODE> <F3.csfasta> <F3.qual> <F5.csfasta> <F5.qual> <output directory> <sample_prefix>"
	print "Example :  python solid_demultiplex_pipeline.py T233232 abc_file_has_F3.csfasta xyz_file_has_F3.qual asfc_file_has_F5.csfasta sdfs_file_has_F5.qual /home/dpuru/folder_name"
	print "This script will output 4 files in the mentioned folder, with all reads extracted for provided bar codes : -"
	print "f3.csfasta"
	print "f3.qual"
	print "f5.csfasta"
	print "f5.qual"
	print "-" * 150
	exit()

# argument 0 is the script name itself

BARCD=sys.argv[1] #which BARCODE (T233232)
F3CSFA=sys.argv[2]
F3QUAL=sys.argv[3]
F5CSFA=sys.argv[4]
F5QUAL=sys.argv[5]
OUTDIR=sys.argv[6]

if not os.path.exists(OUTDIR):
	os.makedirs(OUTDIR)

headerhash={} #hash to save all headers for re-use


#+----reading in F3.csfasta file

prev_row=""
cur_row=""
with open(OUTDIR+"/f3.csfasta","a",0) as f3csout:
	with open(F3CSFA) as f:
		for line in f :
			cur_row=line.rstrip('\n')

			if(regex.findall("("+BARCD+"){e<=2}", cur_row)):
				f3csout.write(prev_row)
				f3csout.write(os.linesep)
				elem=prev_row.split('_F3')[0]
				headerhash[elem]=1
				f3csout.write(cur_row)
				f3csout.write(os.linesep)
			prev_row=cur_row


#+----reading in F3.qual file
with open(OUTDIR+"/f3.qual","a",0) as f3ql :
	with open(F3QUAL) as fh:
		for row in fh:
			fof=row.split('_F3')[0]
	 
			if fof in headerhash:
				f3ql.write(row)
				f3ql.write(next(fh))

#+----reading in F5.csfasta file

with open(OUTDIR+"/f5.csfasta","a",1) as f5csout :
	with open(F5CSFA) as fh:
		for line in fh:
			fof=line.split('_F5-P2')[0]
		
			if fof in headerhash:
  				f5csout.write(line)
				f5csout.write(next(fh))

#+----reading in F5.qual file

with open(OUTDIR+"/f5.qual","a",0) as f5ql :

	with open(F5QUAL) as fh:
		for line in fh:
  			fof=line.split('_F5-P2')[0]
  		
  			if fof in headerhash:
  				f5ql.write(line)
				f5ql.write(next(fh))


#End of script#



