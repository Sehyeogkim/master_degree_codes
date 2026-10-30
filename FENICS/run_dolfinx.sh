#!/bin/bash
#SBATCH -J GMRES_96
#SBATCH -o GMRES_96.o%j
#SBATCH -p defaults
#SBATCH -N 1
#SBATCH -n 96
#SBATCH --ntasks-per-node=96
#SBATCH --nodelist=harvey03

echo "=============================================="
echo "SUBMIT_DATE           = " `date`
echo "SLURM_JOBID           = " $SLURM_JOBID
echo "SLURM_JOB_NAME        = " $SLURM_JOB_NAME
echo "SLURM_JOB_PARTITION   = " $SLURM_JOB_PARTITION
echo "SLURM_JOB_NODELIST    = " $SLURM_JOB_NODELIST
echo "SLURM_NNODES          = " $SLURM_NNODES
echo "SLURM_NTASKS          = " $SLURM_NTASKS
echo "SLURM_NTASKS_PER_NODE = " $SLURM_NTASKS_PER_NODE
echo "SLURMTMPDIR           = " $SLURMTMPDIR
echo "working directory     = " $SLURM_SUBMIT_DIR
echo "=============================================="

# Activate conda environment FIRST (before loading modules)
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dolfinx

# Load modules (but don't let them override conda's libstdc++)
source /HL8/HMod/modules/5.1.1/init/bash
module purge
module load cmake/3.25.2 gcc/11.3.0

# Prioritize conda's libraries over system libraries
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Load DOLFINx environment variables
if [ -f ~/.dolfinx_env ]; then
    source ~/.dolfinx_env
fi

# Additional DOLFINx-specific environment variables
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export HDF5_USE_FILE_LOCKING=FALSE

# Note: DOLFINX_MPI_COMM_WORLD_SIZE and DOLFINX_MPI_COMM_WORLD_RANK are not needed
# MPI is handled automatically by mpi4py and DOLFINx

echo "Starting Time is `date`"
echo "Using DOLFINx environment"
echo "Number of MPI processes: $SLURM_NTASKS"
echo "Python version: $(python3 --version)"

# Run DOLFINx simulation
srun -n $SLURM_NTASKS python3 -u /home/jeff/project/44_fluid_overall_samples/fenics_LU.py

echo "clear"
echo "Closing Time is `date`"
