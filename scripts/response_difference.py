from los_fabulosos_pixelotls.tools import load_raw_data
import numpy as np
from matplotlib import rcParams
from matplotlib import pyplot as plt

rcParams['font.size'] = 15
rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False
rcParams['figure.autolayout'] = True

# get data
print("loading, please wait")
alldat = load_raw_data('../dat')

# name conventions
regions = ["vis ctx", "thal", "hipp", "other ctx", "midbrain", "basal ganglia", "cortical subplate", "other"]
region_colors = ['blue', 'red', 'green', 'darkblue', 'violet', 'lightblue', 'orange', 'gray']
brain_groups = [
    ["VISa", "VISam", "VISl", "VISp", "VISpm", "VISrl"],  # visual cortex
    ["CL", "LD", "LGd", "LH", "LP", "MD", "MG", "PO", "POL", "PT", "RT", "SPF", "TH", "VAL", "VPL", "VPM"],  # thalamus
    ["CA", "CA1", "CA2", "CA3", "DG", "SUB", "POST"],  # hippocampal
    ["ACA", "AUD", "COA", "DP", "ILA", "MOp", "MOs", "OLF", "ORB", "ORBm", "PIR", "PL", "SSp", "SSs", "RSP", "TT"],  # non-visual cortex
    ["APN", "IC", "MB", "MRN", "NB", "PAG", "RN", "SCs", "SCm", "SCig", "SCsg", "ZI"],  # midbrain
    ["ACB", "CP", "GPe", "LS", "LSc", "LSr", "MS", "OT", "SNr", "SI"],  # basal ganglia
    ["BLA", "BMA", "EP", "EPd", "MEA"]  # cortical subplate
]

# calculate some things for all neurons

from_region = "vis ctx"  # "vis ctx", "thal", "hipp", "other ctx"
all_d_right = []
all_d_left = []
all_preference_rates = []  # mean response to right stim - mean response to left stim
all_preference_components_rates = []  # mean response to right stim, mean response to left stim
n_mistakes_right = 0
n_mistakes_left = 0
n_correct_right = 0
n_correct_left = 0

for dat in alldat:
    # get important variables from specific experiment
    dt = dat['bin_size']
    response = dat['response']  # correct responses to right stim, nogo, left stim: -1, 0, 1
    vis_right = dat['contrast_right']
    vis_left = dat['contrast_left']
    N_neurons, N_trials, N_timebins = dat['spks'].shape

    # find neurons indices from selected area
    neurons_indices_in_area = np.where(np.isin(dat['brain_area'], brain_groups[regions.index(from_region)]))[0]

    # selected trials per contrast level and response
    right_stim_correct_trials = np.where(np.logical_and((vis_right == 1)*(vis_left == 0), response < 0))[0]
    left_stim_correct_trials = np.where(np.logical_and((vis_left == 1)*(vis_right == 0), response >= 0))[0]
    right_stim_wrong_trials = np.where(np.logical_and((vis_right == 1)*(vis_left == 0), response >= 0))[0]
    left_stim_wrong_trials = np.where(np.logical_and((vis_left == 1)*(vis_right == 0), response < 0))[0]
    right_stim_trials = np.where((vis_right == 1)*(vis_left == 0))[0]
    left_stim_trials = np.where((vis_left == 1)*(vis_right == 0))[0]

    correct_right_trace = 1/dt * dat['spks'][neurons_indices_in_area][:, right_stim_correct_trials].mean(axis=1)
    wrong_right_trace = 1/dt * dat['spks'][neurons_indices_in_area][:, right_stim_wrong_trials].mean(axis=1)
    d_right = correct_right_trace-wrong_right_trace
    if np.all(~np.isnan(d_right)):
        all_d_right.append(d_right)
    n_mistakes_right += np.sum(len(right_stim_wrong_trials))
    n_correct_right += np.sum(len(right_stim_correct_trials))

    correct_left_trace = 1/dt * dat['spks'][neurons_indices_in_area][:, left_stim_correct_trials].mean(axis=1)
    wrong_left_trace = 1/dt * dat['spks'][neurons_indices_in_area][:, left_stim_wrong_trials].mean(axis=1)
    d_left = correct_left_trace-wrong_left_trace
    if np.all(~np.isnan(d_left)):
        all_d_left.append(d_left)
    n_mistakes_left += np.sum(len(left_stim_wrong_trials))
    n_correct_left += np.sum(len(left_stim_correct_trials))

    mean_right_rate = 1/dt * dat['spks'][neurons_indices_in_area][:, right_stim_trials].mean(axis=(1, 2))
    mean_left_rate = 1/dt * dat['spks'][neurons_indices_in_area][:, left_stim_trials].mean(axis=(1, 2))
    preference_rate = mean_right_rate - mean_left_rate
    if np.all(~np.isnan(preference_rate)):
        all_preference_rates.extend(preference_rate)

    all_preference_components_rates.extend([(x, y) for x, y in zip(mean_right_rate, mean_left_rate)])

# plot
time_array = dt * np.arange(N_timebins)
neurons_indices_in_area = np.where(np.isin(alldat[11]['brain_area'], brain_groups[regions.index("vis ctx")]))[0]
correct_right_trace = 1/dt * alldat[11]['spks'][neurons_indices_in_area][:,
                                                                         np.logical_and((alldat[11]['contrast_right'] == 1)*(alldat[11]['contrast_left'] == 0), alldat[11]['response'] < 0)].mean(axis=(0, 1))
wrong_right_trace = 1/dt * alldat[11]['spks'][neurons_indices_in_area][:,
                                                                       np.logical_and((alldat[11]['contrast_right'] == 1)*(alldat[11]['contrast_left'] == 0), alldat[11]['response'] >= 0)].mean(axis=(0, 1))

fig = plt.figure(figsize=(10, 14))
nrows, ncols = (5, 2)
ax0 = plt.subplot2grid((nrows, ncols), (0, 0), colspan=1)
ax1 = plt.subplot2grid((nrows, ncols), (0, 1), colspan=1)
ax2 = plt.subplot2grid((nrows, ncols), (1, 0), rowspan=nrows-1)
ax3 = plt.subplot2grid((nrows, ncols), (1, 1), rowspan=nrows-1)

ax0.plot(time_array, correct_right_trace)
ax0.plot(time_array, wrong_right_trace)
ax0.set_title('response')
ax0.legend(['correct-R', 'wrong-R'], fontsize=12)
ax0.set(xlabel='time (sec)', ylabel='firing rate (Hz)')

ax1.plot(time_array, correct_right_trace-wrong_right_trace, color='r')
ax1.axhline(y=0, c='k', lw=2)
ax1.set_title('$\Delta$ response')
ax1.legend(['difference'], fontsize=12)
ax1.set(xlabel='time (sec)', ylabel='$\Delta$ firing rate (Hz)')

ax2.imshow(np.vstack(all_d_right), vmin=-10, vmax=10, cmap='bwr')
ax2.set_ylabel('Neurons')
ax2.set_title('contra-mistakes')
ax2.set_aspect('auto')

ax3.imshow(np.vstack(all_d_left), vmin=-10, vmax=10, cmap='bwr')
ax3.set_title('ipsi-mistakes')
ax3.set_aspect('auto')

plt.subplots_adjust(hspace=0.9)
plt.show()
