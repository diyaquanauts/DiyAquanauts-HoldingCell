import tkinter as tk
from tkinter import filedialog
import os

class fileSelection:
    @staticmethod
    def selectFile(extension, initial_directory="."):
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(
            initialdir=initial_directory,
            title="Select File",
            filetypes=[(f"All Files", "*.*"), (f"{extension.upper()} Files", f"*.{extension}")],
        )

        return file_path
