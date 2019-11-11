#!/bin/sh
#
# This script is used to run the hybrid  mpi/openmp  version of fds6
# Set tasks-per-node to the same number as number of grids/mesh in your simulation
# Set cpus-per-task to round_down(20/tasks-per-node)   
# Eg. having 3 grids, 20/3 = 6.6666  rounded to 6 
# That would give tasks-per-node=3 and cpus-per-task=6, using 18 processor in total out of 20.
#
# Request number of nodes (e.g. 10 processors below on 1 node)
#SBATCH -N 1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#
# job time, change for what your job requires (here 30 min)
#SBATCH -t 10:00:00
# 
# filenames stdout and stderr 
#SBATCH -o stdout.out
#SBATCH -e stderr.out
#
#SBATCH  -A  snic2019-3-50
#
#SBATCH --mail-user=bjarne.husted@brand.lth.se
#SBATCH --mail-type=ALL
if [ $# -ne 1 ]; then
    echo --------------------------------------------
    echo Error when executing $0 
    echo misssing name of fds input file
    echo usage: sbatch -J filename.fds run_fds6_mpi.sh  filename.fds
    echo example: sbatch -J roomfire.fds run_fds6_mpi.sh  roomfire.fds
    echo --------------------------------------------
    exit 1
fi
filename_fds=$1
dir_name=$PWD
echo $dir_name
cd $dir_name
# Enable modules and add software
module load intel/2018a
# Set number of openmp threads
# export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
# Run on all nodes and create output for monitoring simulation progress
srun  /home/bph/fds6.7.1_ori  $filename_fds >regoutput.out 2>terminaloutput.out
