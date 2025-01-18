# How to run Experiment 1?

In the repository root, verify if the script is running and generating logs without errors:

```
bash experiments/exp1.sh
```

It should generate a fil in experiments named `experiments/exp1_raw_times`.

After running `bash experiments/exp1.sh` multiple times, run


```
cd experiments 
python exp_stats.py
```