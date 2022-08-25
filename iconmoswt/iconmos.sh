#!/bin/bash
#SBATCH --job-name=mos                 # Job name, will show up in squeue output
#SBATCH --time=0-23:59:59              # Runtime in DAYS-HH:MM:SS format
#SBATCH --partition=cipI                # On which Partition #main,calc,calclong, cip
#SBATCH --output=job1_%j.out           # File to which standard out will be written
#SBATCH --error=job1_%j.err            # File to which standard err will be written
#SBATCH --mail-type=ALL                # Type of email notification- BEGIN,END,FAIL,ALL
##SBATCH --nodelist=cip20               # [01-22] nodelist cip 1-22 up 64 gb mem

python3=/home/mammatus95/Dokumente/miniconda3/bin/python3

#rm dahlem.db
#cp ../db/dahlem.db ./dahlem.db

time ${python3} moswt.py 

python3 autosubmit3.py -f Berlin.txt




