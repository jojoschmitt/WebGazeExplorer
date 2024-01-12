"""
Calculates the percentage of explorations for which the participants already visited
the website before.
"""

import os.path

from analysis.AccumulationMapping import AccumulationMapping
from analysis import Analyzer
from config import EXPERIMENT_DATA_DIR
from experiment.Observation import Observation
from util import from_json_file


def percentage_of_already_visited(accumulation_mapping):

    analyzer = Analyzer.get_default_analyzer()
    analyzer.config.accumulation_mapping = accumulation_mapping
    analyzer.initialize_components()

    relatable_fixations = analyzer.accumulator.get_relatable_fixations()
    relatable_fixations_map = analyzer.accumulator.map_relatable_fixations(relatable_fixations)

    total_already_visited = list()

    for task, relatable_fixations_list in relatable_fixations_map.items():
        already_visited = list()
        for rel_fixs in relatable_fixations_list:
            pid = rel_fixs.pid
            img_name = rel_fixs.image.get_name()
            observation_file_path = os.path.join(EXPERIMENT_DATA_DIR, f"{pid}", f"observation.json")
            observation = from_json_file(Observation, observation_file_path)
            for assignment in observation.assignments:
                if img_name in assignment.img_url:
                    already_visited.append(assignment.website_known)
                    break

        print(f"{int(round(already_visited.count('True')/len(already_visited), 2)*100)}% of all images for {task} have already been visited by participants.")
        total_already_visited.extend(already_visited)
    print(f"Overall {int(round(total_already_visited.count('True')/len(total_already_visited), 2)*100)}% of all images have already been visited by participants.")


if __name__ == '__main__':
    percentage_of_already_visited(AccumulationMapping.TASK)
    percentage_of_already_visited(AccumulationMapping.SPECIFICATION)
