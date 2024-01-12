import os.path
import pickle


class ValidationResult:
    def __init__(self):
        self.validation_scores = list()

    def load(self, path):
        if not os.path.exists(path):
            self.save(path)
        with open(path, "rb") as file:
            self.validation_scores = pickle.load(file).validation_scores

    def save(self, path):
        with open(path, "wb") as file:
            pickle.dump(self, file)

    def set_scores(self, validation_scores):
        self.validation_scores = validation_scores


class ValidationScore:
    def __init__(self, mapping, pid, eid, hm_score, dm_score):
        self.mapping: str = mapping
        self.pid: int = pid
        self.eid: int = eid
        self.hm_score: HeatMapScore = hm_score
        self.dm_score: DirectedMaskScore = dm_score

    def __eq__(self, other):
        return self.mapping == other.mapping and self.pid == other.pid and self.eid == other.eid and self.hm_score == other.hm_score and self.dm_score == other.hm_score


class Score:
    def __init__(self, corr, p):
        self.corr = corr
        self.p = p

    def __eq__(self, other):
        return self.corr == other.corr and self.p == other.p


class DirectedMaskScore(Score):
    def __init__(self, corr, p):
        super().__init__(corr, p)


class HeatMapScore(Score):
    def __init__(self, corr, p):
        super().__init__(corr, p)
