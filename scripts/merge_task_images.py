"""
@Description
This script was used to bring together all screenshots from one task to a single folder.
Instead of having screenshots in the folder of their corresponding category or functionality, they are all in a more
general task folder. The images will be renamed based on their task and category or functionality.
This allows to make a random selection from all 32 images of one task.

@Example
Before: C:/Users/John/Images/Task1/Community/google.com.png
After: C:/Users/John/Images/Task1/google.com-t1.4.png (t1.4 Task 1 Category 4)
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog

from experiment.values import categories, functionalities, desired_functionalities


def copy_images_with_saliency(source_dir, dest_dir):
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src_path = os.path.join(root, file)
                parent_path, curr_dir = os.path.split(root)
                cat_or_func = get_cat_or_func(curr_dir)
                _, parent_dir = os.path.split(parent_path)
                task = get_task(parent_dir)
                src_file_name, src_file_ext = os.path.splitext(file)

                dest_path = f"{dest_dir}/{src_file_name}-t{task}.{cat_or_func}{src_file_ext}"

                if dest_path:
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied '{file}' to '{dest_path}'")


def get_task(txt):
    if "1" in txt:
        return "1"
    elif "2" in txt:
        return "2"
    elif "3" in txt:
        return "3"
    else:
        raise ValueError(f"Task could not be identified from {txt}")


def get_cat_or_func(txt):
    if txt in categories.values():
        for item in categories.items():
            if item[1] == txt:
                return str(item[0])
    if txt in functionalities.values():
        for item in functionalities.items():
            if item[1] == txt:
                return str(item[0])
    if txt in desired_functionalities.values():
        for item in desired_functionalities.items():
            if item[1] == txt:
                return str(item[0])
    raise ValueError(f"Could not find the following category or functionality: {txt}")


def select_source_directory():
    entry = source_entry.get()
    if os.path.exists(entry):
        initial_dir = entry
    else:
        initial_dir = os.path.dirname(__file__)
    source_dir = filedialog.askdirectory(title="Select Source Directory", initialdir=initial_dir)
    source_entry.delete(0, tk.END)
    source_entry.insert(0, source_dir)


def select_destination_directory():
    entry = dest_entry.get()
    if os.path.exists(entry):
        initial_dir = entry
    else:
        initial_dir = os.path.dirname(__file__)
    dest_dir = filedialog.askdirectory(title="Select Destination Directory", initialdir=initial_dir)
    dest_entry.delete(0, tk.END)
    dest_entry.insert(0, dest_dir)


def start_copying():
    source_dir = source_entry.get()
    dest_dir = dest_entry.get()

    if not source_dir or not dest_dir:
        status_label.config(text="Please select source and destination directories.")
        return

    copy_images_with_saliency(source_dir, dest_dir)
    status_label.config(text="Image copying completed.")


if __name__ == '__main__':
    # Create the main GUI window
    root = tk.Tk()

    # Set the width of the dialog
    root.geometry("600x200")

    # Disable resizing of the dialog
    root.resizable(False, False)

    root.title("Image Copy with Saliency")

    # Source directory input
    source_label = tk.Label(root, text="Source Directory:")
    source_label.pack(fill=tk.X, padx=10, pady=5)
    source_entry = tk.Entry(root)
    source_entry.pack(fill=tk.X, padx=10)
    source_button = tk.Button(root, text="Select Source Directory", command=select_source_directory)
    source_button.pack()

    # Destination directory input
    dest_label = tk.Label(root, text="Destination Directory:")
    dest_label.pack(fill=tk.X, padx=10, pady=5)
    dest_entry = tk.Entry(root)
    dest_entry.pack(fill=tk.X, padx=10)
    dest_button = tk.Button(root, text="Select Destination Directory", command=select_destination_directory)
    dest_button.pack()

    # Start copying button
    copy_button = tk.Button(root, text="Start Copying", command=start_copying)
    copy_button.pack()

    # Status label
    status_label = tk.Label(root, text="")
    status_label.pack()

    root.mainloop()