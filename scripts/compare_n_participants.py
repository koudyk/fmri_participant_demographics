"""Plot median number of participants through time from multiple sources.

The plot shows the median for each year from 3 sources:
- David & al annotations distributed in https://github.com/poldracklab/ScanningTheHorizon
- Annotations of NeuroSynth abstracts distributed in https://github.com/poldracklab/ScanningTheHorizon
- Sample sizes automatically extracted from nqdc data.
"""
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd

import utils

MIN_PAPERS = 30
NS_NAME = "Poldrack & al. / NeuroSynth"
DAVID_NAME = "Poldrack & al. / David & al."
NQDC_NAME = "nqdc"

demographics_data = utils.load_n_participants(MIN_PAPERS).loc[
    :, ["publication_year", "count", "n_groups"]
]
# restrict to single-group studies
demographics_data = demographics_data[demographics_data["n_groups"] == 1]
demographics_data["Data source"] = NQDC_NAME
neurosynth_data = utils.load_neurosynth_sample_sizes().loc[
    :, ["publication_year", "count"]
]
neurosynth_data["Data source"] = NS_NAME
david_data = utils.load_david_sample_sizes().loc[
    :, ["publication_year", "count"]
]
david_data["Data source"] = DAVID_NAME
data = pd.concat(
    [demographics_data, neurosynth_data, david_data], axis=0, ignore_index=True
)

fig, ax = plt.subplots()
percentile = 50
sns.lineplot(
    data=data,
    x="publication_year",
    y="count",
    hue="Data source",
    hue_order=(DAVID_NAME, NS_NAME, NQDC_NAME),
    palette=np.asarray(utils.TAB10_COLORS[:3])[[2, 0, 1]],
    style="Data source",
    estimator=lambda x: np.percentile(x, percentile),
    ax=ax,
)
ax.set_xlabel("Publication year")
ax.set_ylabel("Median sample size")
ax.legend(loc="upper left")

plots_dir = utils.get_results_dir("participants_demographics_data", "plots")
fig.savefig(
    plots_dir.joinpath("n_participants_all_sources.pdf"), bbox_inches="tight"
)