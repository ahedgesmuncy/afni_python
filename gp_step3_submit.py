"""
Notes:

Wrapper script for step3_decon.py.

Update paths in "set up" section.

decon_type can be dmBLOCK, GAM, 2GAM, or TENT
"""

# %%
import os
from datetime import datetime
import fnmatch
import subprocess
import time
import json


# set up
parent_dir = "/fslhome/amhedges/compute/Context"
code_dir = os.path.join(parent_dir, "code/afni_python")
decon_type = "2GAM"
decon_dict = {
    "study": ["tf_study_Con.txt", "tf_study_Incon.txt", "tf_study_ConCR.txt", "tf_study_ConFA.txt", "tf_study_ConHit.txt", "tf_study_ConMiss.txt", "tf_study_InconCR.txt", "tf_study_InconFA.txt", "tf_study_InconHit.txt", "tf_study_InconMiss.txt", "tf_study_NA.txt"],
    "test": ["tf_test_CR.txt", "tf_test_FA.txt", "tf_test_Hit.txt", "tf_test_Miss.txt", "tf_test_ConCR.txt", "tf_test_ConFA.txt", "tf_test_ConHit.txt", "tf_test_ConMiss.txt", "tf_test_InconCR.txt", "tf_test_InconFA.txt", "tf_test_InconHit.txt", "tf_test_InconMiss.txt", "tf_test_NA.txt", "tf_test_NANA.txt"]
}


def main():

    # set up stdout/err capture
    deriv_dir = os.path.join(parent_dir, "derivatives")
    current_time = datetime.now()
    out_dir = os.path.join(
        deriv_dir, f'Slurm_out/TS3_{current_time.strftime("%H%M_%d-%m-%y")}'
    )
    os.makedirs(out_dir)

    # submit job for each subj/sess/phase
    subj_list = [x for x in os.listdir(deriv_dir) if fnmatch.fnmatch(x, "sub-*")]
    subj_list.sort()

    # determine which subjs to run
    run_list = []
    for subj in subj_list:
        decon_list = list(decon_dict.keys())
        sess = os.listdir(os.path.join(parent_dir, "dset", subj))[0]

        check_file1 = os.path.join(
            deriv_dir,
            subj,
            sess,
            f"{decon_list[0]}_single_stats_REML+tlrc.HEAD",
        )
        check_file2 = os.path.join(
            deriv_dir,
            subj,
            sess,
            f"{decon_list[1]}_single_stats_REML+tlrc.HEAD",
        )
        if not os.path.exists(check_file1) or not os.path.exists(check_file2):
            run_list.append(subj)

    # make batch list
    # if len(run_list) > 10:
    #     batch_list = run_list[0:10]
    # else:
    #     batch_list = run_list
    batch_list = run_list

    for subj in batch_list:
        sess = os.listdir(os.path.join(parent_dir, "dset", subj))[0]

        h_out = os.path.join(out_dir, f"out_{subj}.txt")
        h_err = os.path.join(out_dir, f"err_{subj}.txt")

        # write decon_dict to json in subj dir
        with open(
            os.path.join(deriv_dir, subj, sess, "decon_dict.json"), "w"
        ) as outfile:
            json.dump(decon_dict, outfile)

        sbatch_job = f"""
            sbatch \
                -J "GP3{subj.split("-")[1]}" \
                -t 50:00:00 \
                --mem=4000 \
                --ntasks-per-node=6 \
                -o {h_out} -e {h_err} \
                --wrap="module load python/3.8 \n \
                python {code_dir}/gp_step3_decon.py \
                    {subj} \
                    {decon_type} \
                    {deriv_dir}"
        """
        sbatch_submit = subprocess.Popen(
            sbatch_job, shell=True, stdout=subprocess.PIPE
        )
        job_id = sbatch_submit.communicate()[0]
        print(job_id.decode("utf-8"))
        time.sleep(1)


if __name__ == "__main__":
    main()

# %%
