import tkinter as tk
from tkinter import filedialog


def handle_tkinter():
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    folder_path = filedialog.askdirectory(master=root)
    # Write the selected path to a file
    if folder_path:
        with open("../data/selected_file_path.txt", "w", encoding="utf-8") as file_out:
            file_out.write(folder_path)
        root.destroy()
    else:
        print("no folder selected")
        root.destroy()
    root.mainloop()  # Close the tkinter root window


if __name__ == "__main__":
    handle_tkinter()
