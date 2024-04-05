import os
import re
import subprocess
import sys
import streamlit as st
import pandas as pd
from io import StringIO
from pathlib import Path
from streamlit_extras.add_vertical_space import add_vertical_space
from resources import edit_design, rename_files, info_external_hard_drive

# TODO fix error alignment file could not be created or is empty for existing files

st.set_page_config(page_title="Data generation", page_icon="⚙️", layout="centered")


class GenAlign:
    def __init__(self):
        # path variables for subscript
        self.__script_path = None
        self.__src_path = None
        self.__gen_path = None
        # path variable for language pairs
        self.__lang_path = None
        # capture whether parsed file should be generated
        # (adapt choice of languages accordingly)
        self.__parse_gen_file = None
        # initiate list for prompt lines to check for download request
        self.__gen_prompt = []
        # language code for source_files language
        self.__code_src = None
        # language code for target language
        self.__code_trg = None
        # source_files language for generation
        self.__lang_src = st.session_state.src if "src" in st.session_state else None
        # source_files language for generation
        self.__lang_trg = st.session_state.src if "trg" in st.session_state else None
        # path variable for source files on external hard drive
        self.__src_path_hard = st.session_state["src_path_hard"] if "src_path_hard" in st.session_state else None
        # path variable for generated files on external hard drive
        self.__gen_path_hard = st.session_state["gen_path_hard"] if "gen_path_hard" in st.session_state else None
        # limit for number of alignments to be generated
        self.__limit = st.session_state.limit if 'limit' in st.session_state \
            else None
        self.__download_text = "The source files are being downloaded. " \
                               "This may take a while ⏳. " \
                               "The alignments will be generated right after."
        self.__generate_text = "The alignments are being generated. " \
                               "Please wait a moment ☕."
        # capture whether parsed or normal file was selected for search
        self.__parse_search = None

    @staticmethod
    @st.cache_data
    def __load_data(src_path, parsed=True):
        final_file = "languages_parsed.csv" if parsed else "languages.csv"
        file_path = os.path.join(src_path, final_file)
        return pd.read_csv(file_path)

    def __handle_paths(self):
        # Determine the current directory
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Cut off the last directory of the current directoryif
        parent_directory = os.path.dirname(current_directory)
        # Construct the paths relative to the parent directory
        self.__script_path = Path(os.path.join(parent_directory, "model", "get_alignments.py")).as_posix()
        if self.__src_path_hard is None:
            self.__src_path = Path(os.path.join(parent_directory, "data", "source_files")).as_posix()
        if self.__gen_path_hard is None:
            self.__gen_path = Path(os.path.join(parent_directory, "data", "generated")).as_posix()
        self.__lang_path = Path(os.path.join(parent_directory, "data", "language_pairs")).as_posix()

    def __handle_languages(self):
        # csv for languages with parse option
        self.__languages = self.__load_data(self.__lang_path, parsed=True)
        # csv for languages without parse option
        self.__languages_no_parse = self.__load_data(self.__lang_path, parsed=False)
        # list of languages that can also be generated in parsed format
        self.__lang = sorted(list(self.__languages["language"]))
        # list of languages that can be generated in normal format
        self.__lang_no_parse = sorted(list(self.__languages_no_parse["language"]))

    def __handle_generation(self):
        self.__parse_option = st.selectbox(label="Format of the Source Data", options=("parsed", "normal"), key="parse")
        self.__parse_gen = False if self.__parse_option == "normal" else True
        with st.form(key="generation"):
            if not self.__parse_gen:
                self.__final_format = self.__lang_no_parse
            else:
                self.__final_format = self.__lang
            col1, col2, col3 = st.columns(3)
            with col1:
                st.selectbox(label="source language",
                             options=self.__final_format, key="src")
            with col2:
                st.selectbox(label="target language",
                             options=self.__final_format, key="trg")
            with col3:
                st.number_input(
                    label="maximum number of alignments", value=10, key="limit")
            add_vertical_space(2)
            st.form_submit_button("Generate Data", on_click=self.__generate)

    def __lang_to_val(self, src, trg, lang_to_code=True):
        if lang_to_code:
            if self.__parse_search == "parsed" or self.__parse_gen:
                self.__code_src = self.__languages.loc[self.__languages['language'] == src, "code"].item()
                self.__code_trg = self.__languages.loc[self.__languages['language'] == trg, "code"].item()
            else:
                self.__code_src = self.__languages_no_parse.loc[self.__languages_no_parse['language']
                                                                == src, "code"].item()
                self.__code_trg = self.__languages_no_parse.loc[self.__languages_no_parse['language']
                                                                == trg, "code"].item()
        else:
            if self.__parse_search == "parsed" or self.__parse_gen:
                self.__search_src = self.__languages.loc[self.__languages['code'] == src, "language"].item()
                self.__search_trg = self.__languages.loc[self.__languages['code'] == trg, "language"].item()
            else:
                self.__search_src = self.__languages_no_parse.loc[self.__languages_no_parse['code']
                                                                  == src, "language"].item()
                self.__search_trg = self.__languages_no_parse.loc[self.__languages_no_parse['code']
                                                                  == trg, "language"].item()

    def __generate(self):
        self.__lang_src = st.session_state.src
        self.__lang_trg = st.session_state.trg
        self.__limit = st.session_state.limit
        try:
            self.__gen_path_hard = st.session_state["gen_path_hard"]
            self.__src_path_hard = st.session_state["src_path_hard"]
        except KeyError:
            pass
        self.__lang_to_val(self.__lang_src, self.__lang_trg, lang_to_code=True)
        # check if path to external hard drive has been given
        if self.__gen_path_hard is not None:
            self.__gen_path = self.__gen_path_hard
        if self.__parse_gen:
            self.__gen_path_file = Path(os.path.join(self.__gen_path, f"alignments_{self.__code_src}" +
                                                     f"_{self.__code_trg}_{self.__limit}_parsed.txt")).as_posix()
        else:
            self.__gen_path_file = Path(os.path.join(self.__gen_path, f"alignments_{self.__code_src}" +
                                                     f"_{self.__code_trg}_" +
                                                     f"{self.__limit}_normal.txt")).as_posix()
        if self.__src_path_hard is not None:
            self.__src_path = self.__src_path_hard
        # Call __run_command_check_download with the determined paths
        self.__run_command_check_download(sys.executable,
                                          self.__script_path,
                                          self.__src_path,
                                          self.__gen_path,
                                          self.__code_src,
                                          self.__code_trg,
                                          str(self.__limit),
                                          self.__parse_option)

    def __handle_no_download(self, parsed):
        # get filenames necessary to be downloaded
        files = [data['url'] for data in parsed]
        # Display filenames with a line break as links
        files_links = "<br>".join([f"<a href='{file}'>{file}</a>" for file in files])
        st.markdown(
            f"""
               <div style="background-color: rgba(255, 255, 0, 0.8);
                padding: 10px;
                border-radius: 5px;
                 color: black;">
                   <b>Note:</b>
                   <br>
                   You have terminated the generation process. 
                   To generate the alignments,
                   you need to have the following files:
                   <br>
                   <br>
                   {files_links}
                   <br><br> Click on the links to download them or go to <a 
                   href='https://opus.nlpl.eu/OpenSubtitles/ar&eu/v2018/OpenSubtitles
                   '>OPUS OpenSubtitles</a> for the download. Make sure to select the parsed version if it is offered!
                   <br> <br>
                   After downloading the necessary files, you put them into the following directory:<br><br>
                    <i>{self.__src_path}</i></div>""",
            unsafe_allow_html=True
        )

    def __message_generation(self):
        # Check if file exists
        if os.path.exists(self.__gen_path_file):
            # Check if file is empty
            if os.path.getsize(self.__gen_path_file) > 0:
                styled = f"""
                            <div style="background-color: rgba(50, 205, 50, 0.5); 
                            padding: 10px;
                            border-radius: 5px;
                            color: black;">
                                <b>The alignment file has been created successfully.</b>
                                <br>
                                <br>
                                The pairs were generated for {self.__lang_src} and {self.__lang_trg} under 
                                the following path:
                                <br>
                                <br>
                                {os.path.abspath(self.__gen_path_file)}.
                            </div>
                            """
                st.markdown(styled, unsafe_allow_html=True)
            else:
                # Delete empty file
                os.remove(self.__gen_path_file)
                styled = f"""
                            <div style="background-color: rgba(255, 165, 0, 0.8); 
                            padding: 10px;
                            border-radius: 5px;
                            color: black;">
                                <b>Error:</b> The alignment file could not be created or is empty.
                            </div>
                            """
                st.markdown(styled, unsafe_allow_html=True)
        else:
            styled = f"""
                        <div style="background-color: rgba(255, 165, 0, 0.8); 
                        padding: 10px;
                        border-radius: 5px;
                        color: black;">
                            <b>Error:</b> The alignment file could not be found. {self.__gen_path_file}
                        </div>
                        """
            st.markdown(styled, unsafe_allow_html=True)

    def __message_download_generation(self):
        styled = f"""
                    <div style="background-color: rgba(50, 205, 50, 0.5); 
                    padding: 10px;
                    border-radius: 5px;
                    color: black;">
                        <b>The files have been downloaded successfully.</b>
                        <br>
                        <br>
                        The pairs were generated for {self.__lang_src} and {self.__lang_trg} under 
                        the following path:
                        <br>
                        <br>
                        {os.path.abspath(self.__gen_path_file)}.
                    </div>
                    """
        st.markdown(styled, unsafe_allow_html=True)

    def __run_command_check_download(self, *cmd_with_args):
        with st.spinner(self.__generate_text):
            try:
                # Start the subprocess
                with subprocess.Popen(cmd_with_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      text=True) as checker:
                    # Read stdout in a non-blocking manner until the subprocess completes
                    while checker.poll() is None:
                        output_chunk = checker.stdout.readline()
                        # Check for timeout (10 seconds)
                        if output_chunk:
                            # Append output to self.__gen_prompt
                            self.__gen_prompt.append(output_chunk.strip())
                        if "size" in output_chunk:
                            # If no output is produced within the timeout, terminate subprocess
                            checker.terminate()
                            break  # Exit loop
                    # Check if "downloading" is found in any line of output
                    if any("downloading" in line for line in self.__gen_prompt):
                        self.__display_download_info()  # This part should display the download info
                    else:
                        # If "downloading" is not found, proceed with message, file creation stats, and reload
                        self.__message_generation()
            except Exception as e:
                # Handle any exceptions that occur during subprocess execution
                st.error(f"Error occurred during subprocess execution: {e}")

    def __run_command_download(self):
        # handle input
        input_stream = StringIO()
        input_stream.write("y")
        input_stream.seek(0)
        # handle generation with download command
        if input_stream is not None:
            # handle input
            input_stream.write("y")
            input_stream.seek(0)
            with st.spinner(self.__download_text):
                subprocess.run([sys.executable,
                                self.__script_path,
                                self.__src_path,
                                self.__gen_path,
                                self.__code_src,
                                self.__code_trg,
                                str(self.__limit),
                                self.__parse_option],
                               stdout=subprocess.PIPE, cwd=os.getcwd(),
                               input=input_stream.read().encode())
            # add info for generated file here:
            self.__message_download_generation()

    def __display_download_info(self):
        parsed_data = self.__parse_output(self.__gen_prompt)
        if not len(parsed_data) > 0:
            styled = f"""
                        <div style="background-color: rgba(255, 165, 0, 0.8); 
                        padding: 10px;
                        border-radius: 5px;
                        color: black;">
                            <b>Error:</b>  <br> There are no source files for this language combination:
                            {self.__lang_src} - {self.__lang_trg}. <br>
                             Please try a different combination.
                        </div>
                        """
            st.markdown(styled, unsafe_allow_html=True)
        else:
            try:
                st.markdown(
                    f"""
                       <div style="background-color: rgba(255, 255, 255, 0.8);
                        padding: 10px;
                        border-radius: 5px;
                         color: black;">
                        You need to download the following source files to generate alignments.
                        How do you want to proceed?</div> """,
                    unsafe_allow_html=True)
                add_vertical_space(1)
                # Parsing logic using other method
                for data in parsed_data:
                    st.markdown(
                        f"""<div style="background-color: rgba(255, 255, 255, 0.8);
                                    padding: 10px;
                                    border-radius: 5px;
                                     color: black;">
                                    <strong>File</strong>: {data['url']} &nbsp;&nbsp;&nbsp; 
                                    <strong>Size</strong>: {data['size']}
                                </div>""",
                        unsafe_allow_html=True)

                add_vertical_space(1)
                col1, col2 = st.columns(2)
                with col1:
                    st.button("Download Data",
                              on_click=lambda: self.__run_command_download(),
                              key="download")
                with col2:
                    st.button("Do not Download Data",
                              on_click=lambda: self.__handle_no_download(
                                  parsed_data),
                              key="no download")
            except Exception as e:
                st.write(e)

    @staticmethod
    def __parse_output(output):
        file_info = []
        # Join all lines into a single string
        joined_lines = '\n'.join(output)
        # Adjusted pattern to capture file size, URL, and documents
        pattern = re.compile(
            r'(\d+\s*(?:MB|GB|KB))\s+(https://[^\s]+)\s+\|\s+(\d+)\s+documents',
            re.IGNORECASE)
        # Find all matches using the adjusted pattern
        matches = pattern.finditer(joined_lines)
        for match in matches:
            size = match.group(1)
            url = match.group(2)
            documents = match.group(3)
            file_info.append({'size': size, 'url': url,
                              'documents': documents})
        return file_info

    def build(self):
        rename_files()
        edit_design()
        st.title("Generate Alignments", anchor=False)
        add_vertical_space(2)
        info_external_hard_drive(st, page="generation")
        add_vertical_space(2)
        self.__handle_paths()
        self.__handle_languages()
        self.__handle_generation()


if __name__ == "__main__":
    test = GenAlign()
    test.build()
