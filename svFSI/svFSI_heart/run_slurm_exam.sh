#!/bin/bash
#SBATCH -J heart_genBC              # job name
#SBATCH -o heart_genBC.o%j          # output and error file name (%j expands to jobID)
#SBATCH -p defaults            # group name(partition name)  "skylake or cascade"
#SBATCH -N 1                    # total number of nodes requested
#SBATCH -n 96                   # total number of mpi tasks requested
#SBATCH --ntasks-per-node=96    # number of cores requested per the compute node
#SBATCH --nodelist=harvey04     # Specifiy nodes

echo "=============================================="
echo "SUBMIT_DATE           = "`date`
echo "SLURM_JOBID           = "$SLURM_JOBID
echo "SLURM_JOB_NAME        = "$SLURM_JOB_NAME
echo "SLURM_JOB_PARTITION   = "$SLURM_JOB_PARTITION
echo "SLURM_JOB_NODELIST    = "$SLURM_JOB_NODELIST
echo "SLURM_NNODES          = "$SLURM_NNODES
echo "SLURM_NTASKS          = "$SLURM_NTASKS
echo "SLURM_NTASKS_PER_NODE = "$SLURM_NTASKS_PER_NODE
echo "SLURMTMPDIR           = "$SLURMTMPDIR
echo "working directory     = "$SLURM_SUBMIT_DIR
echo "=============================================="

source /HL8/HMod/modules/5.1.1/init/bash
module purge
module load cmake/3.25.2 gcc/11.3.0 mpi/gcc-11.3.0/openmpi-4.1.5
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib64/:/home/jkim/repos/svSolverPrivate/build/svSolver-build/bin/:/home/jkim/repos/svSolverPrivate/build/svSolver-build/lib/:/opt/cvbml/libraries/VTK-8.2.0/lib64/

echo Starting Time is `date`
mpirun -np $SLURM_NTASKS /opt/cvbml/repos/svFSI/build/svFSI-build/bin/svFSI fluid_test.inp
echo Closing Time is `date`
