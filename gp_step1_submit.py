"""
Notes:

Wrapper script for step1_preproc.py.

Usage - update "set up" section.

phase_list = list of phases gathered within a single session.
    For example, if a study and then a test phase were both scanned
    during the same session, then phase_list = ["study", "test"]
"""
# %%
import os
from datetime import datetime
import subprocess
import time
import fnmatch

# set up
parent_dir = "/fslhome/amhedges/compute/Context"
code_dir = os.path.join(parent_dir, "code/afni_python")
phase_list = ["study", "test"]
blip_toggle = 0  # 1 = on, 0 = off


# %%
def main():

    # set up stdout/err capture
    current_time = datetime.now()
    out_dir = os.path.join(
        parent_dir,
        f'derivatives/Slurm_out/TS1_{current_time.strftime("%H%M_%d-%m-%y")}',
    )
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # submit job for each subj/sess/phase
    subj_list = [
        x
        for x in os.listdir(os.path.join(parent_dir, "dset"))
        if fnmatch.fnmatch(x, "sub-*")
    ]
    subj_list.sort()

    # determine which subjs to run
    run_list = []
    for subj in subj_list:
        sess = os.listdir(os.path.join(parent_dir, "dset", subj))[0]
        check_file = os.path.join(
            parent_dir,
            "derivatives",
            subj,
            sess,
            f"run-1_{phase_list[0]}_scale+tlrc.HEAD",
        )
        if not os.path.exists(check_file):
            run_list.append(subj)

    # make batch list
    if len(run_list) > 20:
        batch_list = run_list[0:20]
    else:
        batch_list = run_list

    for subj in batch_list:

        h_out = os.path.join(out_dir, f"out_{subj}.txt")
        h_err = os.path.join(out_dir, f"err_{subj}.txt")

        sbatch_job = f"""
            sbatch \
                -J "GP1{subj.split("-")[1]}" \
                -t 20:00:00 \
                --mem=4000 \
                --ntasks-per-node=6 \
                -o {h_out} -e {h_err} \
                --wrap="module load python/3.8 \n \
                python {code_dir}/gp_step1_preproc.py \
                    {subj} \
                    {parent_dir} \
                    {blip_toggle} \
                    {' '.join(phase_list)}"
        """
        sbatch_submit = subprocess.Popen(sbatch_job, shell=True, stdout=subprocess.PIPE)
        job_id = sbatch_submit.communicate()[0]
        print(job_id.decode("utf-8"))
        time.sleep(1)


if __name__ == "__main__":
    main()
