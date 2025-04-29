import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Configure text rendering
rcParams['mathtext.fontset'] = 'stix'
rcParams['font.family'] = 'STIXGeneral'

# Response scale definitions
response_labels = ["Strongly Disagree", "Disagree", "Slightly Disagree", "Neutral",
                   "Slightly Agree", "Agree", "Strongly Agree"]
response_colors = ["#4B6FBA", "#9BB1DB", "#C3C3C3", "#E8C39E",
                   "#F4A582", "#E08214", "#B2182B"]

# Data with hypothesis labels
question_data = {
    # H1 group
    "H1: Turn-taking\nfeels natural": [5, 5, 7, 4, 4, 5, 7, 7, 6, 5, 5],

    # H2 group (a and b together)
    "H2a: Movements\nsync with conversation": [4, 5, 7, 6, 4, 4, 6, 2, 4, 5, 6],
    "H2b: Robot actively\nlistens": [6, 4, 7, 7, 5, 4, 5, 6, 7, 6, 7],

    # H3 group
    "H3: Responses\nadapt to conversation": [5, 2, 7, 5, 7, 5, 6, 7, 7, 6, 7],

    # H4 group (a and b together)
    "H4a: Voice appropriate\nfor well-being support": [4, 6, 7, 5, 3, 4, 6, 5, 5, 6, 7],
    "H4b: Adapts to participant's\ntone/emotion": [3, 3, 7, 5, 3, 2, 6, 7, 5, 6, 6],

    # H5 group (a-f together)
    "H5a: Comfortable\nsharing emotions": [6, 6, 7, 5, 7, 4, 7, 6, 6, 7, 6],
    "H5b: Comfortable sharing\npersonal experiences": [6, 6, 7, 6, 7, 3, 7, 6, 6, 6, 7],
    "H5c: Satisfied with\nrobot's responses": [4, 5, 7, 6, 5, 2, 6, 6, 7, 7, 7],
    "H5d: Robot is\nempathetic": [5, 4, 7, 6, 5, 3, 7, 7, 6, 7, 6],
    "H5e: Felt positive\nduring interaction": [5, 6, 7, 5, 6, 4, 7, 6, 6, 7, 7],
    "H5f: Helps appreciate\naspects of life": [5, 3, 7, 4, 7, 5, 7, 6, 7, 7, 7],

    # Additional items
    # "Robot is\nsocially intelligent": [5, 5, 7, 6, 5, 4, 5, 5, 6, 6, 7],
    # "Robot is\nemotionally intelligent": [5, 5, 7, 5, 5, 2, 5, 5, 6, 6, 5]
}

# Prepare data
questions = list(question_data.keys())
responses = np.array(list(question_data.values())).T

# Calculate response distribution
response_counts = np.zeros((len(questions), len(response_labels)))
for i, res in enumerate(responses.T):
    unique, counts = np.unique(res, return_counts=True)
    for u, c in zip(unique, counts):
        response_counts[i, u - 1] = c
response_percent = (response_counts / response_counts.sum(axis=1, keepdims=True)) * 100

# p-values (in same order as questions)
p_values = [
    0.0020,  # H1
    0.0625,  # H2a
    0.0020,  # H2b
    0.0049,  # H3
    0.0098,  # H4a
    0.0850,  # H4b
    0.0010,  # H5a
    0.0010,  # H5b
    0.0078,  # H5c
    0.0039,  # H5d
    0.0010,  # H5e
    0.0039,  # H5f
    0.0010,  # Socially intelligent
    0.0156  # Emotionally intelligent
]

# Create significance markers
significance_markers = []
for p in p_values:
    if p < 0.001:
        significance_markers.append('**')
    elif p < 0.05:
        significance_markers.append('*')
    else:
        significance_markers.append('')

# Create positions with new grouping logic
positions = []
current_pos = 0
current_main_group = None
in_h5_group = False

for i, q in enumerate(questions):
    # Extract main group identifier
    if 'H' in q:
        main_group = q.split(':')[0][:2]  # Gets 'H1', 'H2', etc.
        is_h5_subitem = main_group == 'H5' and any(c in q.split(':')[0] for c in ['a', 'b', 'c', 'd', 'e', 'f'])
    else:
        main_group = "Other"
        is_h5_subitem = False

    # Handle H5 sub-items as one continuous group
    if is_h5_subitem:
        if not in_h5_group:  # First H5 sub-item
            if current_main_group is not None:  # Not the first item
                current_pos += 0.8  # Space before H5 group
            in_h5_group = True
            current_main_group = 'H5'
        positions.append(current_pos)
        current_pos += 0.65  # Normal within-group spacing
        continue

    # Normal grouping logic for non-H5 items
    if main_group != current_main_group:
        if current_main_group is not None:  # Not the first item
            current_pos += 0.8  # Space between groups
        current_main_group = main_group
        in_h5_group = False

    positions.append(current_pos)
    current_pos += 0.65  # Space within group

# Create figure
fig, ax = plt.subplots(figsize=(15, 8.5))

# Plot bars
bottom = np.zeros(len(questions))
for i, color in enumerate(response_colors):
    ax.barh(positions, response_percent[:, i], left=bottom,
            height=0.6, color=color, label=response_labels[i])
    bottom += response_percent[:, i]

# Format labels with p-value markers
formatted_labels = []
for marker, q in zip(significance_markers, questions):
    if 'H' in q:
        hyp, desc = q.split(':', 1)
        parts = desc.split('\n')
        # Add marker before hypothesis label
        label = f"{marker} $\mathbf{{{hyp}}}$: {parts[0].strip()}" if marker else f"  $\mathbf{{{hyp}}}$: {parts[0].strip()}"
        if len(parts) > 1:
            # Add appropriate spacing for second line
            spacer = ' ' * len(marker) if marker else '  '
            label += f"\n{spacer}{parts[1].strip()}"
    else:
        parts = q.split('\n')
        label = f"{marker} {parts[0]}" if marker else f"  {parts[0]}"
        if len(parts) > 1:
            spacer = ' ' * len(marker) if marker else '  '
            label += f"\n{spacer}{parts[1]}"
    formatted_labels.append(label)

ax.set_yticks(positions)
ax.set_yticklabels(formatted_labels, fontsize=14)
ax.invert_yaxis()

# Adjust margins to prevent cutoff
plt.subplots_adjust(left=0.46, right=0.95, bottom=0.18, top=0.92)  # Increased from 0.42 to 0.45

# Styling
ax.set_xlim(0, 100)
ax.grid(axis="x", linestyle=":", alpha=0.4)
ax.set_xticks(np.arange(0, 101, 20))
ax.set_xticklabels([f"{x}%" for x in np.arange(0, 101, 20)], fontsize=14)

# Legend - moved up by changing bbox_to_anchor y-coordinate from -0.13 to -0.10
legend = ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c, label=l)
                            for c, l in zip(response_colors, response_labels)],
                   loc="lower center",
                   bbox_to_anchor=(0.5, -0.10),  # Changed from -0.13 to -0.10
                   ncol=len(response_labels),
                   fontsize=12,
                   frameon=False)

plt.tight_layout()
plt.show()