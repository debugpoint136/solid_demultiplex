#!/bin/bash

#+----shell script to parse the input parameters a
#+----split the input files into 10 chunks
#+----invoke python script and qsub 10 parallel

properties=`readlink -f input.parameters`
echo "Parsing properties File..."
echo "..."

IFS=$'\n';
for i in `cat $properties`;do
key=`echo $i | awk -F'=' '{print $1}'`
value=`echo $i | awk -F'=' '{print $2}'`
[[ $key == "solid.project.name" ]] && project=$value;
[[ $key == "solid.f3.csfasta.name" ]] && f1=$value;
[[ $key == "solid.f3.qual.name" ]] && f2=$value;
[[ $key == "solid.f5.csfasta.name" ]] && f3=$value;
[[ $key == "solid.f5.qual.name" ]] && f4=$value;
[[ $key == "solid.output.folder" ]] && output=$value;
[[ $key == "solid.barcode1" ]] && barcd1=$value;
[[ $key == "solid.barcode2" ]] && barcd2=$value;
done

#remove all the trailing whitespace from the parsed parameters :-
output="${output%"${output##*[![:space:]]}"}" 
project="${project%"${project##*[![:space:]]}"}"
f1="${f1%"${f1##*[![:space:]]}"}"
f2="${f2%"${f2##*[![:space:]]}"}"
f3="${f3%"${f3##*[![:space:]]}"}"
f4="${f4%"${f4##*[![:space:]]}"}"

#define where to pick the python script from
pyscript=/gpfs/home/cdesai/Testing/sandbox/apr27/SOLiD_demultiplex_pipeline_apr242014.py

#define the number of chunks you want to process?
chunknum=20

#check if the output folder exists or not, else create
tmpfldr=$output/tmp
chunkflder=$tmpfldr/chunks
common=$output/common
[ ! -d $output ] && `mkdir $output`;
[ ! -d $tmpfldr ] && `mkdir $tmpfldr`;
[ ! -d $common ] && `mkdir $common`;
[ ! -d $chunkflder ] && `mkdir $chunkflder`;
[ ! -d $output/$project ] && `mkdir $output/$project`;

rm -rf $chunkflder/*

#check all the input files are available :-
[[ ! -e $f1 ]] && echo "$f1 file not found. Script aborting..." && exit 1;
[[ ! -e $f2 ]] && echo "$f2 file not found. Script aborting..." && exit 1;
[[ ! -e $f3 ]] && echo "$f3 file not found. Script aborting..." && exit 1;
[[ ! -e $f4 ]] && echo "$f4 file not found. Script aborting..." && exit 1;

#+---copy files into shared folder :-
cp $properties $common
cp $pyscript $common

#get basenames

f1path=${f1%/*}
f1name=$(basename $f1)
[ ! -d $chunkflder/$f1name ] && `mkdir $chunkflder/$f1name`;
rm -rf $chunkflder/$f1name/*


f2path=${f2%/*}
f2name=$(basename $f2)
[ ! -d $chunkflder/$f2name ] && `mkdir $chunkflder/$f2name`;
rm -rf $chunkflder/$f2name/*


f3path=${f3%/*}
f3name=$(basename $f3)
[ ! -d $chunkflder/$f3name ] && `mkdir $chunkflder/$f3name`;
rm -rf $chunkflder/$f3name/*


f4path=${f4%/*}
f4name=$(basename $f4)
[ ! -d $chunkflder/$f4name ] && `mkdir $chunkflder/$f4name`;
rm -rf $chunkflder/$f4name/*


#Create grep command files

echo "Spawning scripts to farm out grep on cluster..."

f1lines=`wc -l $f1 | awk '{print $1}'`

# calculating them number of lines in each chunk

chunklines=$((f1lines / chunknum))

cd $chunkflder/$f1name
split -l $chunklines $f1 f1_ &
PID1=$!
echo $PID1 is running ...

cd $chunkflder/$f2name
split -l $chunklines $f2 f2_ &
PID2=$!
echo $PID2 is running ...

cd $chunkflder/$f3name
split -l $chunklines $f3 f3_ &
PID3=$!
echo $PID3 is running ...


cd $chunkflder/$f4name
split -l $chunklines $f4 f4_ &
PID4=$!
echo $PID4 is running ...

# exec intermediary scripts : -




echo "Splitting $f1name ..."
wait $PID1

echo "Splitting $f2name ..."
wait $PID2

echo "Splitting for $f3name ..."
wait $PID3

echo "Splitting $f4name ..."
wait $PID4

sleep 2s


echo "Files split successfully!"

echo "..."
sleep 1s

# generate the qsub files for queuing here :-

cd $chunkflder/$f1name
ls -1 > $common/chunk_list

cd $common

cnt=1

for i in `cat chunk_list`;do

chunkout=chunk_$cnt

[ ! -d $chunkout ] && `mkdir $chunkout`;

base=${i:3:4}

echo "#!/bin/sh" > $base.cmd

echo "#PBS -l nodes=1:ppn=8" >> $base.cmd
echo "#PBS -l walltime=96:00:00" >> $base.cmd
echo "#PBS -l mem=24gb" >> $base.cmd
echo "#PBS -q workq" >> $base.cmd
echo "#PBS -m ae" >> $base.cmd

echo "python $pyscript \\" >> $base.cmd
echo "	 $barcd1 $barcd2 \\" >> $base.cmd
echo "	$chunkflder/$f1name/f1_$base \\" >> $base.cmd
echo "	$chunkflder/$f2name/f2_$base \\" >> $base.cmd
echo "	$chunkflder/$f3name/f3_$base \\" >> $base.cmd
echo "	$chunkflder/$f4name/f4_$base \\" >> $base.cmd
echo "$common/$chunkout" >> $base.cmd

echo "Queuing $cnt on cluster..."
qsub $base.cmd


cnt=$((cnt+1))

done

#including post processing steps :-
echo "#!/bin/sh" > $output/postproc.cmd
echo "" >> $output/postproc.cmd

echo "#---SELECT which folder yyyymmdd-hhmmss do you want to concatenate below----" >> $output/postproc.cmd
echo "select=20140423-231504" >> $output/postproc.cmd
echo "" >> $output/postproc.cmd

echo "cat $common/chunk*/$select/NAIVE/f3.qual > $project/NAIVE/f3.qual" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/NAIVE/f3.csfasta > $project/NAIVE/f3.csfasta" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/NAIVE/f3.qual > $project/NAIVE/f3.qual" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/NAIVE/f5.csfasta > $project/NAIVE/f5.csfasta" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/NAIVE/f5.qual > $project/NAIVE/f5.qual" >> $output/postproc.cmd
echo "" >> $output/postproc.cmd

echo "cat $common/chunk*/$select/$barcd1/f3.csfasta > $project/$barcd1/f3.csfasta" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/$barcd1/f3.qual > $project/$barcd1/f3.qual" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/$barcd1/f5.csfasta > $project/$barcd1/f5.csfasta" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/$barcd1/f5.qual > $project/$barcd1/f5.qual" >> $output/postproc.cmd
echo "" >> $output/postproc.cmd

echo "cat $common/chunk*/$select/$barcd2/f3.csfasta > $project/$barcd2/f3.csfasta" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/$barcd2/f3.qual > $project/$barcd2/f3.qual" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/$barcd2/f5.csfasta > $project/$barcd2/f5.csfasta" >> $output/postproc.cmd
echo "cat $common/chunk*/$select/$barcd2/f5.qual > $project/$barcd2/f5.qual" >> $output/postproc.cmd
