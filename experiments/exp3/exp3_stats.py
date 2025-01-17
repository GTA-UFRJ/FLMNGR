from numpy import mean
from scipy import stats

filename = "exp3_raw_times"

try:
    with open(filename,"r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: The file '{filename}' was not found.")

metric_to_samples_map = {}
for line in lines:
    if line == "---- RESULTS ----\n":
        continue
    metric_key = line.split(" = ")[0]
    sample_value = float(line.split(" = ")[1].split(" ")[0])
    if metric_to_samples_map.get(metric_key) is None: 
        metric_to_samples_map[metric_key] = [sample_value]
    else:
        metric_to_samples_map[metric_key].append(sample_value)

for metric_name, metric_samples in metric_to_samples_map.items():
    metric_mean = mean(metric_samples)
    metric_error = stats.sem(metric_samples) * stats.t.ppf((1+0.95)/2., len(metric_samples)-1)
    print(f"{metric_name} = {metric_mean} +- {metric_error} s")
