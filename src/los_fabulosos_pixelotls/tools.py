import os
import requests
import numpy as np
from typing import List
from scipy.ndimage import gaussian_filter1d
from scipy.ndimage import gaussian_filter #are they different?

def load_raw_data(dat_path='.'):
    '''get dataset in its raw form, just like in the notebook.

    Returns:
    (dict)   : data dictionary with the following keys.

    `alldat` contains 39 sessions from 10 mice, data from Steinmetz et al, 2019. Time bins for all measurements are 10ms, starting 500ms before stimulus onset. The mouse had to determine which side has the highest contrast. For each `dat = alldat[k]`, you have the fields below. For extra variables, check out the extra notebook and extra data files (lfp, waveforms and exact spike times, non-binned). 

    * `dat['mouse_name']`: mouse name
    * `dat['date_exp']`: when a session was performed
    * `dat['spks']`: neurons by trials by time bins.    
    * `dat['brain_area']`: brain area for each neuron recorded. 
    * `dat['ccf']`: Allen Institute brain atlas coordinates for each neuron. 
    * `dat['ccf_axes']`: axes names for the Allen CCF. 
    * `dat['contrast_right']`: contrast level for the right stimulus, which is always contralateral to the recorded brain areas.
    * `dat['contrast_left']`: contrast level for left stimulus. 
    * `dat['gocue']`: when the go cue sound was played. 
    * `dat['response_times']`: when the response was registered, which has to be after the go cue. The mouse can turn the wheel before the go cue (and nearly always does!), but the stimulus on the screen won't move before the go cue.  
    * `dat['response']`: which side the response was (`-1`, `0`, `1`). When the right-side stimulus had higher contrast, the correct choice was `-1`. `0` is a no go response. 
    * `dat['feedback_time']`: when feedback was provided. 
    * `dat['feedback_type']`: if the feedback was positive (`+1`, reward) or negative (`-1`, white noise burst).  
    * `dat['wheel']`: turning speed of the wheel that the mice uses to make a response, sampled at `10ms`. 
    * `dat['pupil']`: pupil area  (noisy, because pupil is very small) + pupil horizontal and vertical position.
    * `dat['face']`: average face motion energy from a video camera. 
    * `dat['licks']`: lick detections, 0 or 1.   
    * `dat['trough_to_peak']`: measures the width of the action potential waveform for each neuron. Widths `<=10` samples are "putative fast spiking neurons". 
    * `dat['%X%_passive']`: same as above for `X` = {`spks`, `pupil`, `wheel`, `contrast_left`, `contrast_right`} but for  passive trials at the end of the recording when the mouse was no longer engaged and stopped making responses. 
    * `dat['prev_reward']`: time of the feedback (reward/white noise) on the previous trial in relation to the current stimulus time. 
    * `dat['reaction_time']`: ntrials by 2. First column: reaction time computed from the wheel movement as the first sample above `5` ticks/10ms bin. Second column: direction of the wheel movement (`0` = no move detected).  

    '''

    fname = []
    for j in range(3):
        fname.append(f'{dat_path}/steinmetz_part{j}.npz')
    url = ["https://osf.io/agvxh/download"]
    url.append("https://osf.io/uv3mw/download")
    url.append("https://osf.io/ehmw2/download")

    for j in range(len(url)):
        if not os.path.isfile(fname[j]):
            try:
                r = requests.get(url[j])
            except requests.ConnectionError:
                print("!!! Failed to download data !!!")
            else:
                if r.status_code != requests.codes.ok:
                    print("!!! Failed to download data !!!")
                else:
                    with open(fname[j], "wb") as fid:
                        fid.write(r.content)

    alldat = np.array([])
    for j in range(len(fname)):
        alldat = np.hstack((alldat, np.load(f'{dat_path}/steinmetz_part{j}.npz', allow_pickle=True)['dat']))

    return alldat


def select_by_areas(dat, selected_regions: List[str] = ['VISp']):
    '''Find indices of neurons belonging to the specified areas in the dataset provided from a single experiment.

    Args:
        dat (dict): data dictionary from a single experiment. For example dat = alldat[11] in the example notebook.
        selected_regions (list of str): list of region names to include. For example ['VISp']

    Returns:
        indices (1D array): array of indices from neurons belonging to specified regions.'''
    return np.where(np.isin(dat['brain_area'], selected_regions))[0]


def select_by_contrast(dat, contrast_pair: tuple = (1, 0)):
    '''Find indices of trials with the specified contrasts in the dataset provided from a single experiment.

    Args:
        dat (dict): data dictionary from a single experiment. For example dat = alldat[11] in the example notebook.
        contrast_pair (tuple): tuple with the contrast level of Left and Right stimulus. For example (1,0) represents stimulus on left with contrast 1 (max), and stimulus on right with contrast 0 (not shown).

    Returns:
        indices (1D array): array of indices from trials.'''
    return np.where((dat['contrast_left'] == contrast_pair[0])*(dat['contrast_right'] == contrast_pair[1]))[0]


def select_by_response(dat, response_type: str = 'to_left'):
    '''Find indices of trials with the specified response in the dataset provided from a single experiment.

    Args:
        dat (dict): data dictionary from a single experiment. For example dat = alldat[11] in the example notebook.
        response_type (str): str specifying direction of movement. "to_left", "to_right", or "nogo". For example, responses "to_left" are correct when stimulus with higher contrast is on the right side. "nogo" is when mouse did not move the wheel enough.

    Returns:
        indices (1D array): array of indices from trials.'''

    if response_type == 'to_left':
        indices = np.where(dat['response'] < 0)[0]
    elif response_type == 'to_right':
        indices = np.where(dat['response'] > 0)[0]
    elif response_type == 'nogo':
        indices = np.where(dat['response'] == 0)[0]
    else:
        raise Warning('wrong response_type input, choose: to_left, to_right or nogo')

    return indices


def select_trials(dat,  contrast_pair: tuple = (0, 1), response_type: str = 'to_left'):
    '''Find indices of trials with the specified response and contrast levels in the dataset provided from a single experiment.

    Args:
        dat (dict): data dictionary from a single experiment. For example dat = alldat[11] in the example notebook.
        contrast_pair (tuple): tuple with the contrast level of Left and Right stimulus. For example (1,0) represents stimulus on left with contrast 1 (max), and stimulus on right with contrast 0 (not shown).
        response_type (str): str specifying direction of movement. "to_left", "to_right", or "nogo". For example, responses "to_left" are correct when stimulus with higher contrast is on the right side. "nogo" is when mouse did not move the wheel enough.

    Returns:
        indices (1D array): array of indices from trials.'''

    contrast_indices = select_by_contrast(dat, contrast_pair)

    if response_type == 'to_left':
        response_indices = np.where(dat['response'] < 0)[0]
    elif response_type == 'to_right':
        response_indices = np.where(dat['response'] > 0)[0]
    elif response_type == 'nogo':
        response_indices = np.where(dat['response'] == 0)[0]
    else:
        raise Warning('wrong response_type input, choose: to_left, to_right or nogo')

    # find intersection of both lists using sets and transforming back to a list
    indices = list(set.intersection(set(contrast_indices), set(response_indices)))

    return indices


def calculate_mean_firing_rate(spks, dt, mean_across: List[str] = ['population'], gaussfilter: bool = False, gauss_sigma: int = 1):
    '''Find mean firing rate from the spikes (dat["spks"]), across the chosen dimensions. Note: spks should contain spikes only of desired neurons, so find indices with the select_* functions, and apply the indices before giving the array of spikes to this function.

    Args:
        spks (3D array): array of spikes, from the "spks" field in the datasets. Dimensions should be (Neurons x Trials x Time)
        mean_across (List[str]): list of str specifying type of mean to apply. It can be: A) "population", to only average across neurons, keeping trials and time, B) "trials" to average across trials, keeping neurons and time, C) "time" to average across time, keeping neurons and trials, or D) any combination of 2 from the previous.

    Returns:
        mean_firing_rates (ND array): array of N dimensions, where N=3-len(mean_across), containing mean firing rates according to parameters.'''

    dimension_order = ['population', 'trials', 'time']
    axis_to_mean = tuple([dimension_order.index(x) for x in mean_across])
    mean_firing_rate = 1/dt * spks.mean(axis=axis_to_mean)
    if gaussfilter:
        mean_firing_rate = gaussian_filter1d(mean_firing_rate, gauss_sigma)

    return mean_firing_rate



def choose_time_window(x):
  #input: x: vector time series
  #output: idxLimits: timestamps for window of size "size" after the first peak is skipped
  x = gaussian_filter(x, sigma=1) #if not preprocessed

  #find index of the first peak, where our function will start looking for the end of the peak(which will be the left end of our window) 
  peak = np.argmax(x)  
  i=peak
  while x[i+1]<x[i]:
    i+=1
  idx0 = i  
  while x[i]>x[idx0]:
    if i>len(x):
      break
    i+=1
  idxf = i

  idxLimits = [idx0,idxf]

  return idxLimits
