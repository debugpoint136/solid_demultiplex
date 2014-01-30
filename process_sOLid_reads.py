#!/bin/python

#+-----------------------------------+
#+------sOLid demultiplexing---------+
#+--------process reads--------------+
#+-----------------------------------+
#+----------Jan 30th, 2014-----------+
#------------------------------------+


import os,sys,time,re

# Goal : lookup all the headers of the 4 files and generate 4 files that have the intersection of headers
# no filter on barcode

if(len(sys.argv) != 6):
	print "-" * 150
	print "USAGE : python solid_demultiplex_pipeline.py <F3.csfasta> <F3.qual> <F5.csfasta> <F5.qual> <output directory> <sample_prefix>"
	print "Example :  python solid_demultiplex_pipeline.py abc_file_has_F3.csfasta xyz_file_has_F3.qual asfc_file_has_F5.csfasta sdfs_file_has_F5.qual /home/dpuru/folder_name"
	print "This script will output 4 files in the mentioned folder, with all reads extracted for provided bar codes : -"
	print "f3.csfasta"
	print "f3.qual"
	print "f5.csfasta"
	print "f5.qual"
	print "-" * 150
	exit()

# argument 0 is the script name itself

F3CSFA=sys.argv[1]
F3QUAL=sys.argv[2]
F5CSFA=sys.argv[3]
F5QUAL=sys.argv[4]
OUTDIR=sys.argv[5]

if not os.path.exists(OUTDIR):
	os.makedirs(OUTDIR)

if not os.path.exists(OUTDIR+"/tmp"):
	os.makedirs(OUTDIR+"/tmp")

TMPFLDR = OUTDIR + "/tmp"

print " the tmp folder that we are going to use is this : "
print TMPFLDR
headerhash={} #hash to save all headers for re-use


#TODO : generate 4 sets for the four files and take intersection 
#		use that set to parse the files and dump 4 seperate files in the output folder

#Part 1 :  Read in all the 4 files and grep just for the headers, on 4 parallel jobs

for a in sys.argv[1:5] :
	infile=a.rstrip('.txt')
	with open(TMPFLDR+"/"+infile+".cmd.sh", 'w') as fh:
		fh.write("#!/bin/bash")
		fh.write(os.linesep)
		cmd = "grep \">\" " +infile+" > ./"+TMPFLDR+"/"+infile+"_headers.txt"
		fh.write(cmd)
		fh.write(os.linesep)
		fh.write("touch ./"+TMPFLDR+"/"+infile+".headers.grep.completed")

	farm_cmd = "qsub bash ./"+TMPFLDR+"/"+infile+".cmd.sh" #<-----Add qsub parameters, queue name, mem, walltime etc
	os.system(farm_cmd)


#wait for the grep commands to finish up
for a in sys.argv[1:5] :
	infile = a.rstrip('.txt')
	while(1):
		if(os.path.exists(TMPFLDR+"/"+infile+".headers.grep.completed")):
			break
		else :
			time.sleep(1)


#Declare sets:
f3csfset =set()
f3qualset=set()
f5csfset =set()
f5qualset=set()

#Part 2: Read all the headers and save them in sets
	#define function
def extract_header(file,suffix,setname):
	with open(file,'r') as fh:
		for line in fh : 
			if(suffix=="_F3"):
				elem = line.lstrip('>').split('_F3')[0]
			else:
				elem = line.lstrip('>').split('_F5-P2')[0]
			
			if(setname=="f3csf"):
				f3csfset.add(elem)
			elif(setname=="f3qual"):
				f3qualset.add(elem)
			elif(setname=="f5csf"):
				f5csfset.add(elem)
			elif(setname=="f5qual"):
				f5qualset.add(elem)

n=0
for a in sys.argv[1:5] :
	infile=a.rstrip('.txt')
	header_file=TMPFLDR+"/"+infile+"_headers.txt"
	n=n+1
	if(n==1):
		extract_header(header_file,"_F3","f3csf")
	elif(n==2):
		extract_header(header_file,"_F3","f3qual")
	elif(n==3):
		extract_header(header_file,"_F5-P2","f5csf")
	elif(n==4):
		extract_header(header_file,"_F5-P2","f5qual")

#Part 3 : 

#----Take intersection of these sets : 

intersect1 = set(f3csfset).intersection(set(f3qualset))
intersect2 = set(f5csfset).intersection(set(f5qualset))

common_headers = set(intersect1).intersection(set(intersect2))

#------Part4 :

#----Read all the files and print out just the required reads

#+----reading in F3.csfasta file
with open(OUTDIR+"/f3.csfasta","a",0) as f3ql :
	with open(F3QUAL) as fh:
		for row in fh:
			if(re.match('>',row)):
				fof=row.lstrip('>').split('_F3')[0]
	 
				if fof in common_headers:
					f3ql.write(row)
					f3ql.write(next(fh))


#+----reading in F3.qual file
with open(OUTDIR+"/f3.qual","a",0) as f3ql :
	with open(F3QUAL) as fh:
		for row in fh:
			if(re.match('>',row)):
				fof=row.lstrip('>').split('_F3')[0]
	 			if fof in common_headers:
					f3ql.write(row)
					f3ql.write(next(fh))
			else : continue

#+----reading in F5.csfasta file

with open(OUTDIR+"/f5.csfasta","a",1) as f5csout :
	with open(F5CSFA) as fh:
		for line in fh:
			if(re.match('>',row)):
				fof=line.lstrip('>').split('_F5-P2')[0]
		
				if fof in common_headers:
  					f5csout.write(line)
					f5csout.write(next(fh))

#+----reading in F5.qual file

with open(OUTDIR+"/f5.qual","a",0) as f5ql :

	with open(F5QUAL) as fh:
		for line in fh:
			if(re.match('>',row)):
  				fof=line.lstrip('>').split('_F5-P2')[0]
  		
  				if fof in common_headers:
  					f5ql.write(line)
					f5ql.write(next(fh))


#End of script#



