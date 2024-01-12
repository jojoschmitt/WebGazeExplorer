from queue import Queue

from tobii_research_addons import CalibrationValidationResult

from experiment import values
from experiment.Image import Image, SPECIFICATIONS
from experiment.Observation import Observation, ValidationResult
from experiment.Phase import Phase
from experiment.State import State
from experiment.Task import Task
from experiment.ValidationWidget import ValType
from util import save_object_to_json_file


class Experiment:
    def __init__(self, id):
        self.id = id
        self.workflow: Queue = Queue()
        self.__init_workflow()
        self.state: State = self.workflow.get()
        self.observation: Observation = Observation.create_observation(self.id)

    def __init_workflow(self):
        assert self.workflow.empty()
        self.workflow.put(State.get_initial_state())
        self.workflow.put(State.get_initial_validation_instruction_state())
        self.workflow.put(State.get_initial_validation_state())
        # for all 3 tasks (classification, functionality identification, navigation)
        for task_id in range(1, 4):
            # Insert introduction state
            self.workflow.put(self.__create_introduction_state(task_id))
            # Insert example state
            #self.workflow.put(self.__create_example_state__(task_id))
            # for all 4 images
            for round in range(1, 5):
                # for all 3 phases (instruction (1), exploration (2), statement (3))
                for phase_id in range(1, 4):
                    self.workflow.put(State(task=Task(task_id, self.id), round=round, phase=Phase(phase_id)))
        self.workflow.put(State.get_final_validation_instruction_state())
        self.workflow.put(State.get_final_validation_state())
        self.workflow.put(State.get_final_state())
        self.__validate_workflow()

    def save_observation_to_file(self, file_path):
        save_object_to_json_file(self.observation, file_path)

    def get_introduction(self):
        return self.state.task.introduction

    def get_initial_validation_instruction(self):
        return values.initial_validation_instruction

    def get_final_validation_instruction(self):
        return values.final_validation_instruction

    def get_latest_validation_result(self):
        if len(self.observation.initial_validation_data) > 0:
            if len(self.observation.final_validation_data) > 0:
                return self.observation.final_validation_data[-1]
            else:
                return self.observation.initial_validation_data[-1]
        else:
            return None

    def get_instruction(self):
        match self.state.task.id:
            case 0:
                return values.instruction_final_state
            case 1:
                return values.instruction_1
            case 2:
                return values.instruction_2
            case 3:
                return values.instruction_3

    def get_navigation_task(self):
        assert self.state.task.id == 3
        desired_functionality = self.get_img().specification
        desired_functionality_id = SPECIFICATIONS[self.state.task.id].index(desired_functionality)
        match desired_functionality_id:
            # Karriereseite
            case 0:
                return values.navigationtask_1
            # Gegenstand in den Einkaufswagen
            case 1:
                return values.navigationtask_2
            # Startseite
            case 2:
                return values.navigationtask_3
            # Login
            case 3:
                return values.navigationtask_4
            # Logout
            case 4:
                return values.navigationtask_5
            # Zahlungsabwicklung
            case 5:
                return values.navigationtask_6
            # Posten von Inhalten
            case 6:
                return values.navigationtask_7
            # Registrierung
            case 7:
                return values.navigationtask_8
            case _:
                raise ValueError(f"The provided ID {desired_functionality_id} did not match any of the available ones [0-7].")

    def get_img(self):
        return Image(self.__current_img_id(), self.state.task.id, reference=False)

    def get_reference_img(self):
        return Image(self.__current_img_id(), self.state.task.id, reference=True)

    def get_statement(self):
        match self.state.task.id:
            case 1:
                return values.statement_1
            case 2:
                return values.statement_2
            case 3:
                return ""

    def __current_img_id(self):
        return self.get_img_id(self.id, self.state.task, self.state.round)

    @staticmethod
    def get_img_id(pid, task, round):
        # There are 32 images total in a task but each image should be presented two times
        # However, no participant should see the same image twice
        # Hence we will start repeating images with the 9. participant (after all images were already presented)
        if pid < 9:
            slot = pid
        else:
            slot = pid-8
        return task.randomized_img_order[(slot - 1)*4 + round - 1]

    def __create_introduction_state(self, task_id):
        return State.introduction_state_from_task(Task(task_id, self.id))

    def evaluate_validation_success(self):
        initial_success_data = self.observation.initial_validation_data[-1]
        final_success_data = self.observation.final_validation_data[-1]
        self.observation.overall_validation_success = initial_success_data.compares_valid(final_success_data)

    def set_validation_data(self, data: CalibrationValidationResult, type: ValType):
        if type == ValType.INITIAL:
            return self.__set_initial_validation_data(data)
        else:
            return self.__set_final_validation_data(data)

    def __set_initial_validation_data(self, data: CalibrationValidationResult):
        validation_result = ValidationResult.from_CalibrationValidationResult(
            len(self.observation.initial_validation_data), data)
        self.observation.initial_validation_data.append(validation_result)
        return validation_result.validation_success

    def __set_final_validation_data(self, data: CalibrationValidationResult):
        validation_result = ValidationResult.from_CalibrationValidationResult(
            len(self.observation.final_validation_data), data)
        self.observation.final_validation_data.append(validation_result)
        return validation_result.validation_success

    def trial_nr(self):
        return (self.state.task.id - 1) * 4 + self.state.round

    def __validate_workflow(self):
        workflow = Queue()
        state = self.workflow.get()
        workflow.put(state)
        while not self.workflow.empty():
            next_state = self.workflow.get()
            # Make sure that state order complies
            assert state < next_state
            state = next_state
            workflow.put(state)
        self.workflow = workflow

    def next_state(self):
        self.state = self.workflow.get()