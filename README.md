# WebGaze Explorer
This project is part of a master's thesis called **Human Scan Patterns in Task-Driven Web Exploration** and publicly available under an MIT license (see LICENSE file).

The project splits into two parts:

**Experiment:** The project contains an eye tracking experiment that collects raw gaze data with a Tobii Pro Fusion eyetracking device during a task-driven web exploration process. 

**Analysis:** The project also contains tools to analyse the raw gaze data once the experiment is finished. The analysis contains the generation of fixation points and saccades from the raw gaze data using an I-VT fixation filter. The fixation points are then used to generate heatmaps, scanpaths and fixation plots and directed heatmaps from the observed web images. Additionally, analysis contains tools to subtract saliency from observations and accumulate data from multiple participants into one observation to find exploration patterns.

# Dataset
We provide our dataset including 96 web images, their corresponding saliency maps and 192 explorations from 16 participants [here on Google Drive](https://drive.google.com/file/d/1WVXw3HVWfmwxyIPCRhQ2wok6KzX42alS/view). Additionally, the dataset contains the reference images that include the marked AOIs for web images of task 3 and their respective heatmaps.

# Requirements
* [Python 3.10](https://www.python.org/downloads/release/python-3100/) (64-bit)
* [Tobii Pro Eye Tracker Manager](https://connect.tobii.com/s/etm-downloads?language=en_US) (for eye tracker calibration)

# Installation
1. Clone the repository.
2. Navigate to the `<repo-root>`.
3. Install requirements `pip install -r requirements.txt`. 
4. Install Tobii addons `python -m pip install .\prosdk-addons-python\`.
   1. For more information on the package see the [prosdk-addons-python GitHub repository](https://github.com/tobiipro/prosdk-addons-python).

## Experiment
Place the webpage images in the following directories:
* Task 1 images in `<repo-root>/experiment/images/original/task1`
* Task 2 images in `<repo-root>/experiment/images/original/task2`
* Task 3 images in `<repo-root>/experiment/images/original/task3`

Place the reference images for task 3 including the AOIs in the following directory: `<repo-root>/experiment/images/reference/task3`.

### Saliency Map Generation
If you wish to run your own experiment and use own webpage images as stimuli, the saliency maps can be generated using this [Contextual Encoder-Decoder Network
for Visual Saliency Prediction](https://github.com/alexanderkroner/saliency).

## Analysis
Place the saliency maps in the following directory: `<repo-root>/analysis/saliency_maps`.

For the analysis of collected gaze data, it is necessary to  apply a fixation filter.
We are using the I-VT fixation filter from the [GazeToolkit](https://github.com/uxifiit/GazeToolkit).
This toolkit is shipped as source code and needs to be built manually. Follow the instructions of the tool's README.

1. We used Visual Studio Enterprise 2017 15.9 x86 on Windows 10 to build the source as described in the tool's documentation.
2. Copy/Move the binaries folder `<gaze-toolkit-root>/Build/Release` to the following directory `<repo-root>/analysis/fixation_filter/Release`.

## Scrips
Maybe take a look into the scripts, they might save you some time and provide some additional analysis.

To use the `saliency_task_relation.py` script, you need to add the AOI heatmaps to `<repo-root>/scripts/script_resources/aoi_heatmaps`


## Known Issues
For **Linux** systems, there a few things to note here:
* When installing PsychoPy, sometimes wheels for wxPython are not available from pip, so you have to manually install a wheel that suits your system. Basically follow the instructions from [PsychoPy](https://www.psychopy.org/download.html#linux-install) i.e. download the correct wheel file for your system, install it and run the PsychoPy installaiton again.

`pip install <wxPython-file>.whl`

`pip install psychopy`

## Tobii Pro Fusion Specification
Please consult the [official device specifications](https://go.tobii.com/tobii-pro-fusion-user-manual) for an optimal eye tracking experience.

## Tobii Pro Eye Tracker Manager Calibration
There are two options when calibrating the Tobii Pro Fusion Eye Tracker:
1. Attach the eye tracker to the bottom center of the screen and run the normal setup.
2. When the eye tracker is not directly attached to the screen, you need to run the advanced setup. Follow the [official Tobii guide](https://connect.tobii.com/s/article/how-to-configure-an-advanced-display-setup?language=en_US) to calibrate the eye tracker correctly. Pay attention on how to measure the angle between the vertical plane and the screen or otherwise the calibration results won't be meaningful.

# Execution
## Experiment
`python experiment/main.py`

### Known Issues
For **Linux** systems, there can be an issue with the display communication protocol. Try running the project with the `wayland` protocol specifically set.

`python main.py -platform wayland`

### Duration
Current completion times range from 10-15 minutes.

## Analysis
Configure the analyzer in `<repo-root>/analysis/Analyzer.py` to decide which analysis steps you want to perform. Once finished execute the analyzer.

`python analysis/Analyzer.py`