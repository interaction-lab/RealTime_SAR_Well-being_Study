import scipy.stats as stats
import numpy as np
import pandas as pd

# Input data
data = {
    "Turn-taking feels natural": [5, 5, 7, 4, 4, 5, 7, 7, 6, 5, 5],
    "Robot actively listens": [6, 4, 7, 7, 5, 4, 5, 6, 7, 6, 7],
    "Movements sync with conversation": [4, 5, 7, 6, 4, 4, 6, 2, 4, 5, 6],
    "Content of responses adapted to inputs": [5, 2, 7, 5, 7, 5, 6, 7, 7, 6, 7],
    "Voice suited for wellbeing coach": [4, 6, 7, 5, 3, 4, 6, 5, 5, 6, 7],
    "Tone and emotions adapted": [3, 3, 7, 5, 3, 2, 6, 7, 5, 6, 6],
    "Comfortable sharing emotions": [6, 6, 7, 5, 7, 4, 7, 6, 6, 7, 6],
    "Comfortable sharing personal experiences": [6, 6, 7, 6, 7, 3, 7, 6, 6, 6, 7],
    "Satisfied with robot's response": [4, 5, 7, 6, 5, 2, 6, 6, 7, 7, 7],
    "Robot seems empathetic": [5, 4, 7, 6, 5, 3, 7, 7, 6, 7, 6],
    "Talking with robot feels positive": [5, 6, 7, 5, 6, 4, 7, 6, 6, 7, 7],
    "Robot is socially intelligent": [5, 5, 7, 6, 5, 4, 5, 5, 6, 6, 7],
    "Robot is emotionally intelligent": [5, 5, 7, 5, 5, 2, 5, 5, 6, 6, 5],
    "Robot helps appreciate things in life": [5, 3, 7, 4, 7, 5, 7, 7, 7, 7, 7]
}

# Perform Wilcoxon signed-rank test for each set against value 4
for label, scores in data.items():
    scores_array = np.array(scores)
    n = len(scores_array)
    mean = np.mean(scores_array)
    sem = stats.sem(scores_array)
    std = np.std(scores_array, ddof=1)
    median = np.median(scores_array)

    # Wilcoxon signed-rank test (against 4)
    stat, p = stats.wilcoxon(scores_array - 4, alternative='two-sided', zero_method='wilcox')

    # Calculate T+ and T- manually
    diffs = scores_array - 4
    ranks = stats.rankdata(np.abs(diffs))
    T_plus = np.sum(ranks[diffs > 0])
    T_minus = np.sum(ranks[diffs < 0])

    # Calculate z-score and r effect size
    z = stats.norm.ppf(1 - p / 2) if p > 0 else float('inf')
    r = z / np.sqrt(n) * (-1 if mean < 4 else 1)

    print(f"{label} (N = {n}): M = {mean:.2f}, SEM = {sem:.2f}, SD = {std:.2f}, Median = {median:.2f}")
    print(f"Wilcoxon signed-rank test: T⁺ = {T_plus:.3f}, T⁻ = {T_minus:.3f}, z = {z:.3f}, "
          f"p = {p:.3f} (2-tailed), r = {r:.3f}")
    print(f"{'There is' if p < 0.05 else 'There is no'} statistically significant difference from 4 at the α = 0.05 level.\n")
