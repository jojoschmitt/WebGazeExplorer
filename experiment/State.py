from experiment.Phase import Phase
from experiment.Task import Task


class State:
    def __init__(self, task, round, phase):
        # Neutral task 0 must only occur with the initial and final state
        if task.id == 0:
            assert (phase == Phase.N_INITIAL
                    or phase == Phase.N_FINAL
                    or phase == Phase.N_INITIAL_VALIDATION
                    or phase == Phase.N_FINAL_VALIDATION
                    or phase == Phase.N_INITIAL_VALIDATION_INSTRUCTION
                    or phase == Phase.N_FINAL_VALIDATION_INSTRUCTION)
        assert round in [1, 2, 3, 4]
        self.task: Task = task
        self.round: int = round
        self.phase: Phase = phase

    def __eq__(self, other):
        return self.task == other.task and self.round == other.round and self.phase == other.phase

    def __lt__(self, other):
        if not isinstance(other, State):
            raise AttributeError(f"Cannot compare {self.__class__} with {other.__class__}")

        if self.task.id == other.task.id:
            if self.round == other.round:
                return self.phase.value < other.phase.value
            else:
                return self.round < other.round
        else:
            # The final validation state is a special case because the task id goes back to 0
            # Still, as long as the current state (self) is not equal to
            # the final validation instruction state,
            # the final validation state or
            # the final state
            # (which are all caught by equal task IDs above), self is always smaller
            if other.phase == Phase.N_FINAL_VALIDATION_INSTRUCTION:
                return True
            else:
                return self.task.id < other.task.id

    def __str__(self):
        return f"Task: {self.task} Round: {str(self.round)} Phase: {self.phase.name}"

    @staticmethod
    def get_initial_state():
        return State(task=Task(0, 0), round=1, phase=Phase.N_INITIAL)

    @staticmethod
    def get_final_state():
        return State(task=Task(0, 0), round=1, phase=Phase.N_FINAL)

    @staticmethod
    def get_initial_validation_instruction_state():
        return State(task=Task(0, 0), round=1, phase=Phase.N_INITIAL_VALIDATION_INSTRUCTION)

    @staticmethod
    def get_initial_validation_state():
        return State(task=Task(0, 0), round=1, phase=Phase.N_INITIAL_VALIDATION)

    @staticmethod
    def get_final_validation_instruction_state():
        return State(task=Task(0, 0), round=1, phase=Phase.N_FINAL_VALIDATION_INSTRUCTION)

    @staticmethod
    def get_final_validation_state():
        return State(task=Task(0, 0), round=1, phase=Phase.N_FINAL_VALIDATION)

    @staticmethod
    def introduction_state_from_task(task: Task):
        return State(task=task, round=1, phase=Phase.T_INTRODUCTION)
