# %%
import os
import time
from datetime import datetime
import subprocess
import json

# %%
# set up
parent_dir = "/fslhome/amhedges/compute/Context/code/afni_python"
code_dir = os.path.join(parent_dir, "code")
atlas_dir = "/fslhome/amhedges/Templates/vold2_mni"
prior_dir = os.path.join(atlas_dir, "priors_ACT")


# %%
# mvm_dict = {phase: {decon: [{WSVAR: sub-brick},{comparison: [A, B]}]}}
mvm_dict = {
    "study": {
        "Congruent": [
            {"Con": 1, "Incon": 3},
            {"Con-Incon": ["Con", "Incon"]},
        ],
        "ConBehavior": [
            {
                "ConCR": 1,
                "ConFA": 3,
                "ConHit": 5,
                "ConMiss": 7,
                "InconCR": 9,
                "InconFA": 11,
                "InconHit": 13,
                "InconMiss": 15,
            },
            {
                "ConCR-ConFA": ["ConCR", "ConFA"],
                "IncCR-IncFA": ["InconCR", "InconFA"],
                "ConFA-ConHT": ["ConFA", "ConHit"],
                "IncFA-IncHT": ["InconFA", "InconHit"],
                "ConCR-ConHT": ["ConCR", "ConHit"],
                "IncCR-IncHT": ["InconCR", "InconHit"],
            },
        ],
    }
}


# %%
def main():

    # set up stdout/err capture
    current_time = datetime.now()
    out_dir = os.path.join(
        parent_dir,
        f'derivatives/Slurm_out/MVM_{current_time.strftime("%H%M_%d-%m-%y")}',
    )
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    h_out = os.path.join(out_dir, "out_mvm.txt")
    h_err = os.path.join(out_dir, "err_mvm.txt")

    # set output directory, write dicts to jsons
    group_dir = os.path.join(parent_dir, "analyses")
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)

    with open(os.path.join(group_dir, "mvm_dict.json"), "w") as outfile:
        json.dump(mvm_dict, outfile)

    sbatch_job = f"""
       sbatch \
            -J "MVM" \
            -t 50:00:00 \
            --mem=6000 \
            --ntasks-per-node=10 \
            -o {h_out} -e {h_err} \
            --wrap="module load python/3.8 \n \
                python {code_dir}/mvm_step1_test.py \
                {group_dir} \
                {atlas_dir} \
                {prior_dir} \
                {parent_dir}"
    """
    sbatch_submit = subprocess.Popen(sbatch_job, shell=True, stdout=subprocess.PIPE)
    job_id = sbatch_submit.communicate()[0]
    print(job_id.decode("utf-8"))


if __name__ == "__main__":
    main()
