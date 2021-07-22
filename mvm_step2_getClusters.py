# %%
import os
import math
import subprocess


# %%
def func_getClusters(mvm_str, comp_thr, group_dir, mvm_dict):

    # Determine cluster size (K)
    h_cmd = f"""
        head -n 136 {group_dir}/MC_thresholds.txt | \
            tail -n 1 | \
            awk '{{print $7}}'
    """
    h_thr = subprocess.Popen(h_cmd, shell=True, stdout=subprocess.PIPE)
    k_thr = math.ceil(float(h_thr.communicate()[0].decode("utf-8")))

    for comp in mvm_dict:
        h_cmd = f"""
            cd {group_dir}

            3dClusterize \
                -nosum \
                -1Dformat \
                -inset MVM_{mvm_str}+tlrc \
                -idat {mvm_dict[comp][0]} \
                -ithr {mvm_dict[comp][1]} \
                -NN 1 \
                -clust_nvox {k_thr} \
                -bisided -{comp_thr} {comp_thr} \
                -pref_map Clust_{comp} \
                > Table_{comp}.txt
        """
        if not os.path.exists(os.path.join(group_dir, f"Clust_{comp}+tlrc.HEAD")):
            h_clust = subprocess.Popen(h_cmd, shell=True, stdout=subprocess.PIPE)
            h_clust.wait()


# %%
def main():

    group_dir = "/fslhome/amhedges/compute/Context/analyses"
    # mvm_dict = {"Hit-Miss": [2, 3], "CR-FA": [4, 5]}
    # thresh_dict = {14: 4.2208, 28: 3.6896, 42: 3.5442, 56: 3.4764, 70: 3.4372}
    mvm_dict = {
        "study": {"Congurent": {"A-B": [2, 3, 4.2208]}, "ConBehavior": ""},
        "test": {"Behavior": "", "ConBehaviorT": ""},
    }


if __name__ == "__main__":
    main()
