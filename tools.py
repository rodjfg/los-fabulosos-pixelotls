import os
import requests
import numpy as np
from typing import List


def load_raw_data():
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
        fname.append('steinmetz_part%d.npz' % j)
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
        alldat = np.hstack((alldat, np.load('steinmetz_part%d.npz' % j, allow_pickle=True)['dat']))

    return alldat


def select_by_areas(dat, selected_regions: List[str] = ['VISp']):
    '''Find indices of neurons belonging to the specified areas in the dataset provided from a single experiment.

    Args:
        dat (dict): data dictionary from a single experiment. For example dat = alldat[11] in the example notebook.
        selected_regions (list of str): list of region names to include. For example ['VISp']

    Returns:
        indices (1D array): array of indices from neurons belonging to specified regions.'''
    return np.where(np.isin(dat['brain_area'], selected_regions))[0]
