from analysis.Movement import Movement
from analysis.SimpleFixation import SimpleFixation
from experiment.Image import Image


class RelatableFixations:
    def __init__(self, pid, image, exploration_id, movements: list[Movement]):
        self.pid: int = pid
        self.image: Image = image
        self.exploration_id = exploration_id
        self.fixations: list[SimpleFixation] = self._movements_to_simple_fixations(movements)

    @staticmethod
    def _movements_to_simple_fixations(movements: list[Movement]) -> list[SimpleFixation]:
        simple_fixations = []
        for movement in movements:
            simple_fixations.append(SimpleFixation(movement.timestamp_us, movement.duration, movement.average_gaze_point2d_x, movement.average_gaze_point2d_y))
        return simple_fixations
