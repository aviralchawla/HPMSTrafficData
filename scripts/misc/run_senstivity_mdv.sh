#!/bin/bash
#SBATCH --partition=bluemoon
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --mem=30G
#SBATCH --time=30:00:00
#SBATCH --job-name="mdv_trc_sentivity"
source ~/.bash_profile

echo "Starting sbatch script myscript.sh at:`date`"
echo "  running host:    ${SLURMD_NODENAME}"
echo "  assigned nodes:  ${SLURM_JOB_NODELIST}"
echo "  partition used:  ${SLURM_JOB_PARTITION}"
echo "  jobid:           ${SLURM_JOBID}"

conda activate hpms
module load gcc/10.5.0

python senstivity_mdv.py --run $1
