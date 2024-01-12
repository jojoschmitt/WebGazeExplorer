"""
Copies all image files from the source directory to any matching directory or subdirectory
in the destination directory.

The matching destination directory is the directory that contains the same image file name as those encountered
in the source directory.

Once the destination directory is identified, the file from the source directory is renamed to
<file_name>-saliency.<file_extension>
and saved into the matching directory inside the destination directory.
"""

import os
import shutil
import tkinter as tk
from tkinter import filedialog


def copy_images_with_saliency(source_dir, dest_dir):
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src_path = os.path.join(root, file)
                dest_path = find_matching_destination(file, dest_dir)

                if dest_path:
                    shutil.copy2(src_path, dest_path)
                    print(f"Copied '{file}' to '{dest_path}'")

def find_matching_destination(src_file, dest_dir):
    src_file_name, src_file_ext = os.path.splitext(src_file)
    for root, _, files in os.walk(dest_dir):
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            if src_file_name == file_name:
                return os.path.join(root, f'{src_file_name}-saliency{src_file_ext}')


def select_source_directory():
    initial_dir = os.path.dirname(__file__)
    source_dir = filedialog.askdirectory(title="Select Source Directory", initialdir=initial_dir)
    source_entry.delete(0, tk.END)
    source_entry.insert(0, source_dir)


def select_destination_directory():
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