import subprocess
import sys
import os
import streamlit as st
from pathlib import Path
from streamlit_extras.add_vertical_space import add_vertical_space
from resources import edit_design


st.set_page_config(page_title="External Hard Drive", page_icon="💾️", layout="centered")


def intro():
    st.title("How to use your external hard drive", anchor=False)
    st.markdown("If you specify the path to your external hard drive, "
                " OpuSearch will automatically replicate the following folders found in data:", unsafe_allow_html=True)
    st.markdown("* source_files", unsafe_allow_html=True)
    st.markdown("* generated", unsafe_allow_html=True)
    st.markdown("* search_results", unsafe_allow_html=True)
    add_vertical_space(1)
    st.markdown("After downloading the source files, they will be automatically saved in source_files."
                "The same goes for the generated files and the search results respectively."
                "If you download the corpus files manually,"
                " make sure to put them under *source_files*.", unsafe_allow_html=True)
    st.markdown("**Attention**: If you refresh the page, "
                "the folders of the local project's directory will be taken as default."
                , unsafe_allow_html=True)
    st.markdown("Press the button below to navigate to the directory, in which you want to save your project's data:"
                , unsafe_allow_html=True)
    st.button("Choose Directory", on_click=assign_paths_harddrive)


def assign_paths_harddrive():
    subdirectory_names = ["source_files", "generated", "search_results"]
    path = os.path.dirname(os.path.abspath(__file__))
    p = subprocess.Popen([sys.executable, "tkinter_file_dialog.py"], cwd=path,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, error = p.communicate()
    p.terminate()

    # Get the directory containing the main script
    main_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to "selected_file_path.txt"
    file_path = os.path.join(main_script_dir, "../data/selected_file_path.txt")

    # Open "selected_file_path.txt" and read the folder path
    with open(file_path, "r", encoding="utf-8") as file_in:
        folder_path = file_in.read().strip()
    subdirectory_paths = []
    for subdir_name in subdirectory_names:
        subdir_path = Path(os.path.join(folder_path, subdir_name)).as_posix()
        os.makedirs(subdir_path, exist_ok=True)
        subdirectory_paths.append(subdir_path)
    # Create an empty file "-" in the "search_results" directory
    empty_file_path = os.path.join(subdirectory_paths[1], "-")
    with open(empty_file_path, "w") as empty_file:
        pass  # Just creating an empty file
    st.session_state["src_path_hard"] = subdirectory_paths[0]
    st.session_state["gen_path_hard"] = subdirectory_paths[1]
    st.session_state["search_path_hard"] = subdirectory_paths[2]
    message_generation(subdirectory_paths)


def message_generation(paths):
    # Check if file exists
    all_paths_exist = all(os.path.exists(path) for path in paths)
    if all_paths_exist:
        styled = f"""
                    <div style="background-color: rgba(50, 205, 50, 0.5); 
                    padding: 10px;
                    border-radius: 5px;
                    color: black;">
                        <b>The location has been set successfully.</b>
                    """
        st.markdown(styled, unsafe_allow_html=True)
    else:
        styled = f"""
                    <div style="background-color: rgba(255, 165, 0, 0.8); 
                padding: 10px;
                    border-radius: 5px;
                    color: black;">
                        <b>Error:</b> Soomething went wrong.
                    </div>
                    """
        st.markdown(styled, unsafe_allow_html=True)


def build():
    edit_design()
    intro()

if __name__ == "__main__":
    build()


