#!/bin/python

#+-----------------------------------+
#+----------Chandni Desai------------+
#+----------Genomics Core------------+
#+-----Scripps Research Institute----+
#+----------Jan 20th, 2014-----------+
#------------------------------------+


import os,sys,re,regex
from datetime import datetime

#Edit --1 : Modified the script to save the list of headers into a list
#-----------Read the above list and extract just those lines from f3.qual, f5.csfasta and f5.qual

# Edit -2 : 23 Jan ,2014 : 11:25 EST
#+---- 1. Removed slurp mode of file intake
#+-----2. Replaced array with hash lookup

# Bug fix : Jan 24, 2014 :~ Fixed regex string match from anywhere in the string to beginning of string

# Apr 24, 2014 :~ Modified the script to accept 2 barcodes, and segregate the reads into 3 bins. hardcoded for 2 mismatches only

if(len(sys.argv) != 8):
	print "-" * 150
	print "USAGE : python solid_demultiplex_pipeline.py BARCODE1 BARCODE2 <F3.csfasta> <F3.qual> <F5.csfasta> <F5.qual> <output directory> <sample_prefix>"
	print "Example :  python solid_demultiplex_pipeline.py T233232 T342561 abc_file_has_F3.csfasta xyz_file_has_F3.qual asfc_file_has_F5.csfasta sdfs_file_has_F5.qual /home/dpuru/folder_name"
	print "This script will output 4 files in the mentioned folder, with all reads extracted for provided bar codes : -"
	print "f3.csfasta"
	print "f3.qual"
	print "f5.csfasta"
	print "f5.qual"
	print "-" * 150
	exit()

# argument 0 is the script name itself
BARCD=[]
BARCD1=sys.argv[1] #get 1st BARCODE (T233232)
BARCD2=sys.argv[2] #get 2nd BARCODE (T302032)
F3CSFA=sys.argv[3]
F3QUAL=sys.argv[4]
F5CSFA=sys.argv[5]
F5QUAL=sys.argv[6]
OUTDIR=sys.argv[7]

if not os.path.exists(OUTDIR):
	os.makedirs(OUTDIR)

dateString = datetime.now().strftime("%Y%m%d-%H%M%S")

CUROUTDIR=OUTDIR+"/"+dateString

os.makedirs(CUROUTDIR) #create a unique folder for current run metadata
DIRBARCD1=CUROUTDIR+"/"+BARCD1
os.makedirs(CUROUTDIR+"/"+BARCD1)

DIRBARCD2=CUROUTDIR+"/"+BARCD2
os.makedirs(CUROUTDIR+"/"+BARCD2)

DIRNAIVE=CUROUTDIR+"/NAIVE"
os.makedirs(CUROUTDIR+"/NAIVE")

headerhash1={} #hash to save all headers for re-use
headerhash2={} #hash to save all headers for re-use
headerhash3={} #hash to save all headers for re-use

# Create a summary file

print "===== Summary of this run will get saved in README ====="

with open(CUROUTDIR+"/README","a",0) as SUM:
	SUM.write("-"*75 + "\n")
	SUM.write("Output folder : " + OUTDIR + "\n")
	SUM.write("-"*75 + "\n")
	SUM.write("Input parameters : \n")
	SUM.write("Barcode 1\t: " + BARCD1 + "\n")
	SUM.write("Barcode 2\t: " + BARCD2 + "\n")
	SUM.write("F3 csfasta file\t: " + F3CSFA + "\n")
	SUM.write("F3 qual file\t: " + F3QUAL + "\n")
	SUM.write("F5 csfasta file\t: " + F5CSFA + "\n")
	SUM.write("F5 qual file\t: " + F5QUAL + "\n")
	SUM.write("-"*75 + "\n")


#+----reading in F3.csfasta file

prev_row=""
cur_row=""

with open(F3CSFA) as f:
	for line in f :
		cur_row=line.rstrip('\n')

		if(regex.findall("\A("+BARCD1+"){e<=2}", cur_row)):
			with open(DIRBARCD1+"/f3.csfasta","a",0) as f3csout:
				f3csout.write(prev_row)
				f3csout.write(os.linesep)
				elem=prev_row.split('_F3')[0]
				headerhash1[elem]=1
				f3csout.write(cur_row)
				f3csout.write(os.linesep)
			prev_row=cur_row
		elif(regex.findall("\A("+BARCD2+"){e<=2}", cur_row)):
			with open(DIRBARCD2+"/f3.csfasta","a",0) as f3csout:
				f3csout.write(prev_row)
				f3csout.write(os.linesep)
				elem=prev_row.split('_F3')[0]
				headerhash2[elem]=1
				f3csout.write(cur_row)
				f3csout.write(os.linesep)
			prev_row=cur_row
		elif(re.match(">", cur_row)) :
			prev_row=cur_row
		elif(cur_row != '\n') : 
			with open(DIRNAIVE+"/f3.csfasta","a",0) as f3csout:
				f3csout.write(prev_row)
				f3csout.write(os.linesep)
				elem=prev_row.split('_F3')[0]
				headerhash3[elem]=1
				f3csout.write(cur_row)
				f3csout.write(os.linesep)
			#prev_row=cur_row


#+----reading in F3.qual file
with open(F3QUAL) as fh:
	for row in fh:
		fof=row.split('_F3')[0]
	 
		if fof in headerhash1:
			with open(DIRBARCD1+"/f3.qual","a",0) as f3ql :
				f3ql.write(row)
				f3ql.write(next(fh))

		elif fof in headerhash2:
			with open(DIRBARCD2+"/f3.qual","a",0) as f3ql :
				f3ql.write(row)
				f3ql.write(next(fh))
		
		elif fof in headerhash3:
			with open(DIRNAIVE+"/f3.qual","a",0) as f3ql :
				f3ql.write(row)
				f3ql.write(next(fh))


#+----reading in F5.csfasta file

with open(F5CSFA) as fh:
	for row in fh:
		fof=row.split('_F5-P2')[0]
	 
		if fof in headerhash1:
			with open(DIRBARCD1+"/f5.csfasta","a",0) as f5csout :
				f5csout.write(row)
				f5csout.write(next(fh))

		elif fof in headerhash2:
			with open(DIRBARCD2+"/f5.csfasta","a",0) as f5csout :
				f5csout.write(row)
				f5csout.write(next(fh))
			
		elif fof in headerhash3:
			with open(DIRNAIVE+"/f5.csfasta","a",0) as f5csout :
				f5csout.write(row)
				f5csout.write(next(fh))

#+----reading in F5.qual file

with open(F5CSFA) as fh:
	for row in fh:
		fof=row.split('_F5-P2')[0]
	 
		if fof in headerhash1:
			with open(DIRBARCD1+"/f5.qual","a",0) as f5ql :
				f5ql.write(row)
				f5ql.write(next(fh))

		elif fof in headerhash2:
			with open(DIRBARCD2+"/f5.qual","a",0) as f5ql :
				f5ql.write(row)
				f5ql.write(next(fh))
			
		elif fof in headerhash3:
			with open(DIRNAIVE+"/f5.qual","a",0) as f5ql :
				f5ql.write(row)
				f5ql.write(next(fh))


#End of script#



