import json

from tobii_research_addons import CalibrationValidationResult


class Observation:
    def __init__(self, id, completed, overall_validation_success, initial_validation_data, final_validation_data,  assignments):
        self.id: int = id
        self.completed: bool = completed
        self.overall_validation_success: bool = overall_validation_success
        self.initial_validation_data: list[ValidationResult] = initial_validation_data
        self.final_validation_data: list[ValidationResult] = final_validation_data
        self.assignments: list[Assignment] = assignments

    def add_assignment(self, assignment):
        self.assignments.append(assignment)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        initial_validation_data = []
        final_validation_data = []
        assignments = []
        for ivd in data['initial_validation_data']:
            initial_validation_data.append(ValidationResult.from_json(json.dumps(ivd)))
        for fvd in data['final_validation_data']:
            final_validation_data.append(ValidationResult.from_json(json.dumps(fvd)))
        for ass in data['assignments']:
            assignments.append(Assignment.from_json(json.dumps(ass)))
        return cls(data['id'], data['completed'], data['overall_validation_success'], initial_validation_data, final_validation_data, assignments)

    @staticmethod
    def create_observation(id):
        return Observation(id, False, False, [], [], [])


class ValidationResult:
    def __init__(self, id, average_precision_right, average_precision_left, average_accuracy_right, average_accuracy_left, average_precision_rms_right, average_precision_rms_left, validation_success):
        self.id = id
        self.average_precision_right = average_precision_right
        self.average_precision_left = average_precision_left
        self.average_accuracy_right = average_accuracy_right
        self.average_accuracy_left = average_accuracy_left
        self.average_precision_rms_right = average_precision_rms_right
        self.average_precision_rms_left = average_precision_rms_left
        self.validation_success = validation_success

    def __lt__(self, other):
        # We are not including the RMS values because then we would end up with two precision values
        # and only one accuracy value which would automatically apply more weight to precision
        total_self = (self.average_precision_right
                      + self.average_precision_left
                      + self.average_accuracy_right
                      + self.average_accuracy_left
                      #+ self.average_precision_rms_right
                      #+ self.average_precision_rms_left
                      )
        total_other = (other.average_precision_right
                       + other.average_precision_left
                       + other.average_accuracy_right
                       + other.average_accuracy_left
                       #+ other.average_precision_rms_right
                       #+ other.average_precision_rms_left
                       )
        return total_self < total_other

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(**data)

    @staticmethod
    def from_CalibrationValidationResult(id, data: CalibrationValidationResult):
        return ValidationResult(id,
                                data.average_precision_right,
                                data.average_precision_left,
                                data.average_accuracy_right,
                                data.average_accuracy_left,
                                data.average_precision_rms_right,
                                data.average_precision_rms_left,
                                ValidationResult.__is_valid(data))

    @staticmethod
    def __is_valid(data: CalibrationValidationResult):
        """
        From the Tobii Pro Fusion specification the following optimal values are provided:
        Accuracy: 0.4°
        Precision RMS: 0.3°

        We define a validation as unsuccessful, if the deviation from the specification is
        above 0.2° or there is no data at all (NaN)
        """
        deviation = 0.2
        accuracy_thresh = 0.4 + deviation
        precision_rms_thresh = 0.3 + deviation
        if (data.average_accuracy_right > accuracy_thresh
                or data.average_accuracy_left > accuracy_thresh
                or data.average_precision_rms_right > precision_rms_thresh
                or data.average_precision_rms_left > precision_rms_thresh
                or str(data.average_accuracy_right) == "nan"
                or str(data.average_accuracy_left) == "nan"
                or str(data.average_precision_right) == "nan"
                or str(data.average_precision_left) == "nan"
                or str(data.average_precision_rms_right) == "nan"
                or str(data.average_precision_rms_left) == "nan"):
            return False
        return True

    def compares_valid(self, other):
        """
        Compares two ValidationResults. This is useful in case both validations are made in two different
        points in time. This helps to identify inaccurate gaze recordings by validating the calibration over
        a time period based on the difference of both ValidationResults.
        We define the limit for a positive validation as an accuracy difference of 2mm at the physical stimuli plane.
        At 60cm distance from the eyes to the stimuli plane, the angle needs to increase by 0.19° for a 2mm distance:
        arctan(0,2cm / 60 cm) = 0.19°
        """
        if not isinstance(other, ValidationResult):
            raise AttributeError(f"Can only compare validity to {ValidationResult.__class__} and not {other.__class__}")
        accuracy_thresh = 0.19
        aar_diff = abs(self.average_accuracy_right - other.average_accuracy_right)
        aal_diff = abs(self.average_accuracy_left - other.average_accuracy_left)
        if aar_diff > accuracy_thresh or aal_diff > accuracy_thresh \
                or self.validation_success is False \
                or other.validation_success is False:
            return False
        return True


class Assignment:
    def __init__(self, task_id, round, img_url, img_specification, user_selection, answer_correct, website_known):
        self.task_id = task_id
        self.round = round
        self.img_url = img_url
        self.img_specification = img_specification
        self.user_selection = user_selection
        self.answer_correct = answer_correct
        self.website_known = website_known

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(**data)


class Answer:
    def __init__(self, user_selection, website_known):
        self.user_selection = user_selection
        self.website_known = website_known