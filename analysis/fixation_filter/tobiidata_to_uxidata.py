import os

from util import repo_root

DATA_DIR = os.path.join(repo_root, "analysis", "../data")


def _uxi_csv_header():
    return ("Timestamp,LeftValidity,LeftGazePoint2DX,LeftGazePoint2DY,LeftGazePoint3DX,LeftGazePoint3DY,"
            "LeftGazePoint3DZ,LeftEyePosition3DX,LeftEyePosition3DY,LeftEyePosition3DZ,LeftPupilDiameter,"
            "RightValidity,RightGazePoint2DX,RightGazePoint2DY,RightGazePoint3DX,RightGazePoint3DY,"
            "RightGazePoint3DZ,RightEyePosition3DX,RightEyePosition3DY,RightEyePosition3DZ,RightPupilDiameter")


def _tobii_tsv_header():
    return ('device_time_stamp\t'
            'system_time_stamp\t'
            'left_gaze_point_on_display_area\t'
            'left_gaze_point_in_user_coordinate_system\t'
            'left_gaze_point_validity\t'
            'left_pupil_diameter\t'
            'left_pupil_validity\t'
            'left_gaze_origin_in_user_coordinate_system\t'
            'left_gaze_origin_in_trackbox_coordinate_system\t'
            'left_gaze_origin_validity\t'
            'right_gaze_point_on_display_area\t'
            'right_gaze_point_in_user_coordinate_system\t'
            'right_gaze_point_validity\t'
            'right_pupil_diameter\t'
            'right_pupil_validity\t'
            'right_gaze_origin_in_user_coordinate_system\t'
            'right_gaze_origin_in_trackbox_coordinate_system\t'
            'right_gaze_origin_validity')


def _validity(gaze_point_validity, pupil_validity):
    if int(gaze_point_validity) and int(pupil_validity):
        return "Valid"
    return "Invalid"


def _get_value(gaze_data, variable):
    src_header = {name: index for index, name in enumerate(_tobii_tsv_header().split("\t"))}
    return gaze_data[src_header[variable]]


def _str_to_tup(s):
    return tuple(s.replace("(", "")
                 .replace(")", "")
                 .replace(" ", "")
                 .split(","))


def _replace_nan(lst):
    rep = "0"
    clean_list = []
    for item in lst:
        if isinstance(item, tuple):
            clean_item = _handle_nan_tuple(item, rep)
        else:
            if item == "nan":
                clean_item = rep
            else:
                clean_item = item
        clean_list.append(clean_item)
    return clean_list


def _handle_nan_tuple(tup, rep):
    clean_elements = []
    for element in tup:
        if element == "nan":
            clean_elements.append(rep)
        else:
            clean_elements.append(element)
    return f"({str(tuple(clean_elements)).replace(' ', '')})"


def convert_tobiidata_to_uxidata(participant_data_dir):
    source_file_path = os.path.join(participant_data_dir, "tobii_data.tsv")
    if not os.path.exists(source_file_path):
        print(f"Tobii data file for participant not found ({source_file_path})")
        return False
    destination_file_path = os.path.join(participant_data_dir, "uxi_data.csv")
    with open(source_file_path, 'r') as src_file:
        with open(destination_file_path, 'w') as res_file:
            res_file.write(_uxi_csv_header()+"\n")
            src_header_line = src_file.readline()  # Read off the header line
            for line in src_file:
                gaze_data = line.split("\t")
                # Timestamp from Tobii SDK given in microseconds (ticks:us)
                # us_to_hh_mm_ss_ms(1034954093) -> 00:17:14:954.093
                timestamp = _get_value(gaze_data, "system_time_stamp")
                # Left eye measures
                left_validity = _validity(_get_value(gaze_data, "left_gaze_point_validity"),
                                         _get_value(gaze_data, "left_pupil_validity"))
                left_gaze_point_on_display_area = _str_to_tup(_get_value(
                    gaze_data, "left_gaze_point_on_display_area"))
                left_gaze_point_2d_x = left_gaze_point_on_display_area[0]
                left_gaze_point_2d_y = left_gaze_point_on_display_area[1]
                left_gaze_point_in_user_coordinate_system = _str_to_tup(
                    _get_value(gaze_data, "left_gaze_point_in_user_coordinate_system"))
                left_gaze_point_3d_x = left_gaze_point_in_user_coordinate_system[0]
                left_gaze_point_3d_y = left_gaze_point_in_user_coordinate_system[1]
                left_gaze_point_3d_z = left_gaze_point_in_user_coordinate_system[2]
                left_gaze_origin_in_user_coordinate_system = _str_to_tup(
                    _get_value(gaze_data, "left_gaze_origin_in_user_coordinate_system"))
                left_eye_position_3d_x = left_gaze_origin_in_user_coordinate_system[0]
                left_eye_position_3d_y = left_gaze_origin_in_user_coordinate_system[1]
                left_eye_position_3d_z = left_gaze_origin_in_user_coordinate_system[2]
                left_pupil_diameter = _get_value(gaze_data, "left_pupil_diameter")
                # Right eye measures
                right_validity = _validity(_get_value(gaze_data, "right_gaze_point_validity"),
                                          _get_value(gaze_data, "left_pupil_validity"))
                right_gaze_point_on_display_area = _str_to_tup(
                    _get_value(gaze_data, "right_gaze_point_on_display_area"))
                right_gaze_point_2d_x = right_gaze_point_on_display_area[0]
                right_gaze_point_2d_y = right_gaze_point_on_display_area[1]
                right_gaze_point_in_user_coordinate_system = _str_to_tup(
                    _get_value(gaze_data, "right_gaze_point_in_user_coordinate_system"))
                right_gaze_point_3d_x = right_gaze_point_in_user_coordinate_system[0]
                right_gaze_point_3d_y = right_gaze_point_in_user_coordinate_system[1]
                right_gaze_point_3d_z = right_gaze_point_in_user_coordinate_system[2]
                right_gaze_origin_in_user_coordinate_system = _str_to_tup(
                    _get_value(gaze_data, "right_gaze_origin_in_user_coordinate_system"))
                right_eye_position_3d_x = right_gaze_origin_in_user_coordinate_system[0]
                right_eye_position_3d_y = right_gaze_origin_in_user_coordinate_system[1]
                right_eye_position_3d_z = right_gaze_origin_in_user_coordinate_system[2]
                right_pupil_diameter = _get_value(gaze_data, "right_pupil_diameter")

                uxi_variables = [
                    timestamp,
                    left_validity,
                    left_gaze_point_2d_x,
                    left_gaze_point_2d_y,
                    left_gaze_point_3d_x,
                    left_gaze_point_3d_y,
                    left_gaze_point_3d_z,
                    left_eye_position_3d_x,
                    left_eye_position_3d_y,
                    left_eye_position_3d_z,
                    left_pupil_diameter,
                    right_validity,
                    right_gaze_point_2d_x,
                    right_gaze_point_2d_y,
                    right_gaze_point_3d_x,
                    right_gaze_point_3d_y,
                    right_gaze_point_3d_z,
                    right_eye_position_3d_x,
                    right_eye_position_3d_y,
                    right_eye_position_3d_z,
                    right_pupil_diameter
                ]

                uxi_variables = _replace_nan(uxi_variables)
                uxi_data = ",".join(uxi_variables)
                res_file.write(uxi_data+"\n")

    return True
