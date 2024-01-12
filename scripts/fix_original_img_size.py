"""
There was an issue where the PicPick tool took screenshots with a resolution of 1920x1079.
This script finds all images that are not properly 1080p i.e. 1920x1080.
Then duplicates last row/column and appends it at the bottom / to the left.
New images are saved along the old images as new-<original_img_name>.
"""

import os

import cv2
import numpy as np

from util import repo_root, list_files


def fix_original_images():
    original_imgs_dir = os.path.join(repo_root, 'experiment', 'images', 'original')
    task1_img_dir = os.path.join(original_imgs_dir, 'task1')
    task2_img_dir = os.path.join(original_imgs_dir, 'task2')
    task3_img_dir = os.path.join(original_imgs_dir, 'task3')
    task_dirs = [task1_img_dir, task2_img_dir, task3_img_dir]

    for task_dir in task_dirs:
        file_names = list_files(task_dir)
        for file_name in file_names:
            img = cv2.imread(os.path.join(task_dir, file_name))
            height, width, _ = img.shape
            if width != 1920 or height != 1080:
                fixed = False
                if width == 1920 and height == 1079:
                    new_img = duplicate_last_row(img)
                    fixed = True

                if fixed:
                    new_file_name = f"new-{file_name}"
                    new_img_path = os.path.join(task_dir, new_file_name)
                    cv2.imwrite(new_img_path, new_img)
                    print(f"Created new image: {new_img_path}")
                else:
                    print(f"Unconsidered image: ({width},{height}) for {file_name}")


def duplicate_last_row(img):
    return np.vstack((img, img[-1:, :, :]))


def duplicate_last_column(img):
    return np.hstack((img, img[:, -1:, :]))


if __name__ == '__main__':
    fix_original_images()
