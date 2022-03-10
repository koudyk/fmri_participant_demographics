import pprint
import json

import pandas as pd
from sklearn import metrics
from matplotlib import pyplot as plt


import utils


def get_y(samples, extractor_name, remove_outliers):
    result = {}
    extracted_n = samples.loc[:, extractor_name]
    if remove_outliers:
        kept_y_true = annotated_n < annotated_n.quantile(0.9)
        kept = kept_y_true & extracted_n.notnull()
        result["n_annotations"] = int(kept_y_true.sum())
    else:
        kept = extracted_n.notnull()
        result["n_annotations"] = len(annotated_n)
    result["n_detections"] = int(kept.sum())
    result["y_true"] = annotated_n[kept].values
    result["y_pred"] = extracted_n[kept].values
    return result


def score_extraction(samples, extractor_name, remove_outliers):
    scores = {}
    y = get_y(samples, extractor_name, remove_outliers)
    scores["n_detections"] = y["n_detections"]
    scores["n_annotations"] = y["n_annotations"]
    for metric_name in (
        "r2_score",
        "mean_absolute_error",
        "median_absolute_error",
        "mean_absolute_percentage_error",
    ):
        scores[metric_name] = getattr(metrics, metric_name)(
            y["y_true"], y["y_pred"]
        )
    return scores


results_dir = utils.get_results_dir("n_participants")
samples = pd.read_csv(results_dir.joinpath("n_participants.csv"), index_col=0)

all_scores = {}
annotated_n = samples.iloc[:, 0]
for extractor_name in samples.columns[1:]:
    extractor_scores = {}
    for remove_outliers in (False, True):
        extractor_scores[
            f"remove_outliers_{remove_outliers}"
        ] = score_extraction(samples, extractor_name, remove_outliers)
    all_scores[extractor_name] = extractor_scores

results_dir.joinpath("scores.json").write_text(
    json.dumps(all_scores, indent=4), "utf-8"
)
pprint.pprint(all_scores)

for remove_outliers in (False, True):
    fig, axes = plt.subplots(1, 2, sharex=True, sharey=True)
    xy_min, xy_max = 0, 0
    for ax, extractor_name in zip(axes, all_scores.keys()):
        y = get_y(samples, extractor_name, remove_outliers)
        ax.set_title(
            f"{extractor_name}\n"
            f"{y['n_detections']} / {y['n_annotations']} detections"
        )
        ax.scatter(y["y_true"], y["y_pred"], alpha=0.3)
        xy_min = min((xy_min, ax.get_xlim()[0], ax.get_ylim()[0]))
        xy_max = max((xy_max, ax.get_xlim()[1], ax.get_ylim()[1]))
        ax.set_aspect(1.0)
    axes[0].set_xlim((xy_min, xy_max))
    fig.savefig(
        results_dir.joinpath(f"remove_outliers_{remove_outliers}.png"),
        bbox_inches="tight",
    )