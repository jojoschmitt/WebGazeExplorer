"""
This script evaluates the observation quality by its successful initial and final validation result.
A validation result consists of the following important attributes:
Average Accuracy Right | Average Accuracy Left | Average Precision Right | Average Precision Left | Average Precision RMS Right | Average Precision RMS Left
It then sorts the observations and prints their validation results in order of quality, high to low.
Along the validation results, the mean and standard deviation of all observed validation results is printed.

The quality of an observation is determined by the sum of its normalized mean deviations
i.e. the sum over the mean of the initial and final normalized deviations.
Hereby, accuracy deviation and precision deviation are taken into account but not the precision RMS deviation
because we would otherwise add more weight to the precision value when comparing validation results.

The mean and standard deviation are calculated over the initial and final validation result of each observation.
"""


import os.path

from experiment.Observation import Observation, ValidationResult

from statistics import mean, pstdev

from util import repo_root, list_files, from_json_file


class Mean:
    def __init__(self, aar_mean, aal_mean, apr_mean, apl_mean, aprr_mean, aprl_mean):
        self.aar = aar_mean
        self.aal = aal_mean
        self.apr = apr_mean
        self.apl = apl_mean
        self.aprr = aprr_mean
        self.aprl = aprl_mean

    @staticmethod
    def from_observations(obs: list[Observation]):
        aar_vals = []
        aal_vals = []
        apr_vals = []
        apl_vals = []
        aprr_vals = []
        aprl_vals = []
        for ob in obs:
            ini_val = sorted(ob.initial_validation_data)[0]
            fin_val = sorted(ob.final_validation_data)[0]
            aar_vals += [ini_val.average_accuracy_right, fin_val.average_accuracy_right]
            aal_vals += [ini_val.average_accuracy_left, fin_val.average_accuracy_left]
            apr_vals += [ini_val.average_precision_right, fin_val.average_precision_right]
            apl_vals += [ini_val.average_precision_left, fin_val.average_precision_left]
            aprr_vals += [ini_val.average_precision_rms_right, fin_val.average_precision_rms_right]
            aprl_vals += [ini_val.average_precision_rms_left, fin_val.average_precision_rms_left]
        return Mean(mean(aar_vals), mean(aal_vals), mean(apr_vals), mean(apl_vals), mean(aprr_vals), mean(aprl_vals))


class ValidationEvaluation:
    """
    dev stands for deviation (from mean)
    norm stands for normalized and is a value of [-1, 1]. It describes the fraction of deviation (from mean)
    """
    def __init__(self,
                 aar_dev, norm_aar_dev,
                 aal_dev, norm_aal_dev,
                 apr_dev, norm_apr_dev,
                 apl_dev, norm_apl_dev,
                 aprr_dev, norm_aprr_dev,
                 aprl_dev, norm_aprl_dev):
        self.aar_dev: float = aar_dev
        self.norm_aar_dev: float = norm_aar_dev
        self.aal_dev: float = aal_dev
        self.norm_aal_dev: float = norm_aal_dev
        self.apr_dev: float = apr_dev
        self.norm_apr_dev: float = norm_apr_dev
        self.apl_dev: float = apl_dev
        self.norm_apl_dev: float = norm_apl_dev
        self.aprr_dev: float = aprr_dev
        self.norm_aprr_dev: float = norm_aprr_dev
        self.aprl_dev: float = aprl_dev
        self.norm_aprl_dev: float = norm_aprl_dev

    @staticmethod
    def from_validation_result(val_res: ValidationResult, global_mean: Mean):
        aar_dev = val_res.average_accuracy_right - global_mean.aar
        norm_aar_dev = aar_dev / global_mean.aar
        aal_dev = val_res.average_accuracy_left - global_mean.aal
        norm_aal_dev = aal_dev / global_mean.aal
        apr_dev = val_res.average_precision_right - global_mean.apr
        norm_apr_dev = apr_dev / global_mean.apr
        apl_dev = val_res.average_precision_left - global_mean.apl
        norm_apl_dev = apl_dev / global_mean.apl
        aprr_dev = val_res.average_precision_rms_right - global_mean.aprr
        norm_aprr_dev = aprr_dev / global_mean.aprr
        aprl_dev = val_res.average_precision_rms_left - global_mean.aprl
        norm_aprl_dev = aprl_dev / global_mean.aprl
        return ValidationEvaluation(aar_dev, norm_aar_dev,
                 aal_dev, norm_aal_dev,
                 apr_dev, norm_apr_dev,
                 apl_dev, norm_apl_dev,
                 aprr_dev, norm_aprr_dev,
                 aprl_dev, norm_aprl_dev)


class ObservationEvaluation:
    def __init__(self, pid, ini_val, fin_val, ini_val_eval, fin_val_eval, global_mean):
        self.pid: int = pid
        self.ini_val: ValidationResult = ini_val
        self.ini_val_eval: ValidationEvaluation = ini_val_eval
        self.fin_val: ValidationResult = fin_val
        self.fin_val_eval: ValidationEvaluation = fin_val_eval
        self.global_mean: Mean = global_mean

    def __lt__(self, other):
        if not isinstance(other, ObservationEvaluation):
            raise AttributeError(f"Cannot compare {self.__class__} to {other.__class__}")
        self_total_norm_dev = 0
        other_total_norm_dev = 0
        # We are not including the RMS values because then we would end up with two precision values
        # and only one accuracy value which would automatically apply more weight to precision
        self_total_norm_dev += (self.ini_val_eval.norm_aar_dev +
                                self.ini_val_eval.norm_aal_dev +
                                self.ini_val_eval.norm_apr_dev +
                                self.ini_val_eval.norm_apl_dev +
                                #self.ini_val_eval.norm_aprr_dev +
                                #self.ini_val_eval.norm_aprl_dev +
                                self.fin_val_eval.norm_aar_dev +
                                self.fin_val_eval.norm_aal_dev +
                                self.fin_val_eval.norm_apr_dev +
                                self.fin_val_eval.norm_apl_dev
                                #self.fin_val_eval.norm_aprr_dev +
                                #self.fin_val_eval.norm_aprl_dev
                                )
        other_total_norm_dev += (other.ini_val_eval.norm_aar_dev +
                                 other.ini_val_eval.norm_aal_dev +
                                 other.ini_val_eval.norm_apr_dev +
                                 other.ini_val_eval.norm_apl_dev +
                                 #other.ini_val_eval.norm_aprr_dev +
                                 #other.ini_val_eval.norm_aprl_dev +
                                 other.fin_val_eval.norm_aar_dev +
                                 other.fin_val_eval.norm_aal_dev +
                                 other.fin_val_eval.norm_apr_dev +
                                 other.fin_val_eval.norm_apl_dev
                                 #other.fin_val_eval.norm_aprr_dev +
                                 #other.fin_val_eval.norm_aprl_dev
                                 )
        return self_total_norm_dev < other_total_norm_dev

    @staticmethod
    def from_observation(obs: Observation, global_mean: Mean):
        ini_val = sorted(obs.initial_validation_data)[0]
        ini_val_eval = ValidationEvaluation.from_validation_result(ini_val, global_mean)
        fin_val = sorted(obs.final_validation_data)[0]
        fin_val_eval = ValidationEvaluation.from_validation_result(fin_val, global_mean)
        return ObservationEvaluation(
            obs.id,
            ini_val,
            fin_val,
            ini_val_eval,
            fin_val_eval,
            global_mean
        )


def get_observations() -> list[Observation]:
    obs_main_dir = os.path.join(repo_root, "experiment", "results")
    obs = []
    for part_nr in os.listdir(obs_main_dir):
        obs_dir = os.path.join(obs_main_dir, part_nr)
        if not os.path.isdir(obs_dir):
            continue
        obs_files = list_files(obs_dir)
        for file in obs_files:
            if file.endswith(".json"):
                absolute_file_path = os.path.join(obs_dir, file)
                obs.append(from_json_file(Observation, absolute_file_path))
    return obs


def std_devs(obs: list[Observation]):
    aar_vals = []
    aal_vals = []
    apr_vals = []
    apl_vals = []
    aprr_vals = []
    aprl_vals = []
    for ob in obs:
        ini_val = sorted(ob.initial_validation_data)[0]
        fin_val = sorted(ob.final_validation_data)[0]
        aar_vals += [ini_val.average_accuracy_right, fin_val.average_accuracy_right]
        aal_vals += [ini_val.average_accuracy_left, fin_val.average_accuracy_left]
        apr_vals += [ini_val.average_precision_right, fin_val.average_precision_right]
        apl_vals += [ini_val.average_precision_left, fin_val.average_precision_left]
        aprr_vals += [ini_val.average_precision_rms_right, fin_val.average_precision_rms_right]
        aprl_vals += [ini_val.average_precision_rms_left, fin_val.average_precision_rms_left]
    return pstdev(aar_vals), pstdev(aal_vals), pstdev(apr_vals), pstdev(apl_vals), pstdev(aprr_vals), pstdev(aprl_vals)


if __name__ == '__main__':
    obs = get_observations()
    if obs:
        print(
            "Average Accuracy Right | Average Accuracy Left | Average Precision Right | Average Precision Left | Average Precision RMS Right | Average Precision RMS Left")
        global_mean = Mean.from_observations(obs)
        print("Mean Values")
        print(global_mean.aar, global_mean.aal, global_mean.apr, global_mean.apl, global_mean.aprr, global_mean.aprl)
        st_devs = std_devs(obs)
        print("Standard Deviations")
        print(*st_devs)
        print("Normalized Standard Deviations")
        print(st_devs[0] / global_mean.aar, st_devs[1] / global_mean.aal, st_devs[2] / global_mean.apr,
              st_devs[3] / global_mean.apl, st_devs[4] / global_mean.aprr, st_devs[5] / global_mean.aprl)
        print("")
        ob_evals = []
        for ob in obs:
            eval = ObservationEvaluation.from_observation(ob, global_mean)
            ob_evals.append(eval)
        ob_evals = sorted(ob_evals)
        print("The following observations are ordered by calibration validation quality. Highest quality first.")
        pid_list = []
        total_quality_score = 0
        for eval in ob_evals:
            print(f"Observation PID {eval.pid}")
            pid_list.append(eval.pid)
            val = eval.ini_val
            norm = eval.ini_val_eval
            print("Initial validation result followed by normalized deviation")
            print(val.average_accuracy_right, val.average_accuracy_left, val.average_precision_right,
                  val.average_precision_left, val.average_precision_rms_right, val.average_precision_rms_left)
            print(norm.norm_aar_dev, norm.norm_aal_dev, norm.norm_apr_dev,
                  norm.norm_apl_dev, norm.norm_aprr_dev, norm.norm_aprl_dev)
            initial_norm = [norm.norm_aar_dev, norm.norm_aal_dev, norm.norm_apr_dev,
                  norm.norm_apl_dev, norm.norm_aprr_dev, norm.norm_aprl_dev]
            val = eval.fin_val
            norm = eval.fin_val_eval
            print("Final validation result followed by normalized deviation")
            print(val.average_accuracy_right, val.average_accuracy_left, val.average_precision_right,
                  val.average_precision_left, val.average_precision_rms_right, val.average_precision_rms_left)
            print(norm.norm_aar_dev, norm.norm_aal_dev, norm.norm_apr_dev,
                  norm.norm_apl_dev, norm.norm_aprr_dev, norm.norm_aprl_dev)
            print("Normalized mean deviation")
            print(mean([initial_norm[0], norm.norm_aar_dev]), mean([initial_norm[1], norm.norm_aal_dev]),
                  mean([initial_norm[2], norm.norm_apr_dev]), mean([initial_norm[3], norm.norm_apl_dev]),
                  mean([initial_norm[4], norm.norm_aprr_dev]), mean([initial_norm[5], norm.norm_aprl_dev]))
            # The higher the score the better, therefore flipped the algebraic sign from normalized deviation
            quality_score = -(mean([initial_norm[0], norm.norm_aar_dev]) + mean([initial_norm[1], norm.norm_aal_dev]) +
                              mean([initial_norm[2], norm.norm_apr_dev]) + mean([initial_norm[3], norm.norm_apl_dev]))
            print(f"Quality score: {quality_score}")
            print("")
        print(pid_list)
            