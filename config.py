import os.path

from util import repo_root


RESOLUTION = (1920, 1080)

MIDDLE_FIXATION_INTENSITY = 125

EXPERIMENT_DIR = os.path.join(repo_root, "experiment")
EXPERIMENT_DATA_DIR = os.path.join(EXPERIMENT_DIR, "results")
ANALYSIS_DIR = os.path.join(repo_root, "analysis")
ANALYSIS_DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
ANALYSIS_PLOT_DIR = os.path.join(ANALYSIS_DIR, "plots")
ACCUMULATED_PLOT_DIR = os.path.join(ANALYSIS_PLOT_DIR, "accumulated")
ACCUMULATED_SALIENCE_PLOT_DIR = os.path.join(ACCUMULATED_PLOT_DIR, 'salience_considered')

VALIDATION_RESULT_FILE_PATH = os.path.join(ANALYSIS_DATA_DIR, 'validation_result.pickle')

ACCUMULATED_DIRECTED_MASK_DIR = os.path.join(ANALYSIS_DATA_DIR, "accumulated_directed_masks")

ORIGINAL_IMG_DIR = os.path.join(EXPERIMENT_DIR, "images", "original")
SALIENCE_IMG_DIR = os.path.join(ANALYSIS_DIR, "saliency_maps")

VALIDATION_RAW_LOG_PATH = os.path.join(EXPERIMENT_DATA_DIR, "validation_data.tsv")
VALIDATION_MARKER_LOG_PATH = os.path.join(EXPERIMENT_DATA_DIR, "validation_markers.tsv")

TEST_DIR = os.path.join(repo_root, 'tests')
TEST_RESOURCES_DIR = os.path.join(TEST_DIR, 'test_resources')
SCRIPT_DIR = os.path.join(repo_root, 'scripts')
SCRIPT_RESOURCES_DIR = os.path.join(SCRIPT_DIR, 'script_resources')
