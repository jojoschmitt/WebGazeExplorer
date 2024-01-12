from enum import Enum


MOVEMENT_HEADER = "Timestamp,MovementType,Duration,AverageGazePoint2DX,AverageGazePoint2DY,AverageGazePoint3DX,AverageGazePoint3DY,AverageGazePoint3DZ,AverageEyePosition3DX,AverageEyePosition3DY,AverageEyePosition3DZ,AveragePupilDiameter"


class MovementType(Enum):
    FIXATION = "Fixation"
    SACCADE = "Saccade"
    # Eye movement is unknown because the eye were not seen by the tracker (e.g. blinks),
    # or the real movement could have not been determined from the samples.
    UNKNOWN = "Unknown"


class Movement:
    def __init__(self, timestamp, movement_type, duration, average_gaze_point2d_x, average_gaze_point2d_y,
                 average_gaze_point3d_x, average_gaze_point3d_y, average_gaze_point3d_z, average_eye_position3d_x,
                 average_eye_position3d_y, average_eye_position3d_z, average_pupil_diameter):
        self.timestamp_us = timestamp
        self.movement_type = movement_type
        self.duration = duration
        self.average_gaze_point2d_x = average_gaze_point2d_x
        self.average_gaze_point2d_y = average_gaze_point2d_y
        self.average_gaze_point3d_x = average_gaze_point3d_x
        self.average_gaze_point3d_y = average_gaze_point3d_y
        self.average_gaze_point3d_z = average_gaze_point3d_z
        self.average_eye_position3d_x = average_eye_position3d_x
        self.average_eye_position3d_y = average_eye_position3d_y
        self.average_eye_position3d_z = average_eye_position3d_z
        self.average_pupil_diameter = average_pupil_diameter

    def is_fixation(self):
        if self.movement_type == MovementType.FIXATION:
            return True
        return False

    @staticmethod
    def from_csv(line):
        movement_attributes = line.split(",")
        timestamp = int(movement_attributes[0])
        movement_type = MovementType(movement_attributes[1])
        duration = float(movement_attributes[2])
        if movement_type == MovementType.FIXATION:
            average_gaze_point2d_x = float(movement_attributes[3])
            average_gaze_point2d_y = float(movement_attributes[4])
            average_gaze_point3d_x = float(movement_attributes[5])
            average_gaze_point3d_y = float(movement_attributes[6])
            average_gaze_point3d_z = float(movement_attributes[7])
            average_eye_position3d_x = float(movement_attributes[8])
            average_eye_position3d_y = float(movement_attributes[9])
            average_eye_position3d_z = float(movement_attributes[10])
            average_pupil_diameter = float(movement_attributes[11])
        else:
            average_gaze_point2d_x = None
            average_gaze_point2d_y = None
            average_gaze_point3d_x = None
            average_gaze_point3d_y = None
            average_gaze_point3d_z = None
            average_eye_position3d_x = None
            average_eye_position3d_y = None
            average_eye_position3d_z = None
            average_pupil_diameter = None
        return Movement(timestamp, movement_type, duration, average_gaze_point2d_x, average_gaze_point2d_y,
                        average_gaze_point3d_x, average_gaze_point3d_y, average_gaze_point3d_z, average_eye_position3d_x,
                        average_eye_position3d_y, average_eye_position3d_z, average_pupil_diameter)


def write_movements_to_file(movements: list[Movement], file_path: str):
    with open(file_path, 'w') as file:
        file.write(f"{MOVEMENT_HEADER}\n")
        for movement in movements:
            movement_attributes = [movement.timestamp_us, movement.movement_type,
                             movement.duration, movement.average_gaze_point2d_x,
                             movement.average_gaze_point2d_y, movement.average_gaze_point3d_x,
                             movement.average_gaze_point3d_y, movement.average_gaze_point3d_z,
                             movement.average_eye_position3d_x, movement.average_eye_position3d_y,
                             movement.average_eye_position3d_z, movement.average_pupil_diameter]
            writable_movement_attributes = [_movement_attribute_to_str(attr) for attr in movement_attributes]
            line = ",".join(writable_movement_attributes)
            file.write(f"{line}\n")


def _movement_attribute_to_str(attr):
    if isinstance(attr, MovementType):
        return attr.value
    else:
        return str(attr)
