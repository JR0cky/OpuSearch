import os
import re
import streamlit as st
import pandas as pd
from resources import edit_design, scroll_top, rename_files
from model.monolingual_context import MonolingualContext
from model.bilingual_context import BilingualContext
from model.monolingual_statistics import MonolingualStats
from model.bilingual_statistics import BilingualStats
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(page_title="Search Data", page_icon="🔎", layout="centered")

# TODO catch 'error: global flags not at the start of the expression at position 17' (Regex, wait for reproduction)
# TODO handle mystery languages (normal mode)
# TODO disclaimer for search results in source_files for wrong language resulting from alignments (for all search modes), e.g. "Que"


class SearchAlign:
    def __init__(self):
        # get path to root
        self.__root_path = None
        # create needed paths
        self.__handle_paths()
        # list of generated files to choose from
        self.__generated = self.__get_generated(self.__gen_path)
        # csv for languages with parse option
        self.__languages = self.__load_data(self.__src_path)
        # list of languages that can also be generated in parsed format
        self.__lang = sorted(list(self.__languages["language"]))
        # language code for source_files language
        self.__code_src = st.session_state.code_src \
            if 'code_src' in st.session_state else None
        # language code for target language
        self.__code_trg = st.session_state.code_trg \
            if 'code_trg' in st.session_state else None
        # capture whether parsed or normal file was selected for search
        self.__parse_search = None
        # regular expression entered (user)
        self.__regex = st.session_state.regex \
            if 'regex' in st.session_state else None
        # selected file to search through (user)
        self.__search_file = st.session_state.search_file \
            if 'search_file' in st.session_state else None
        # path to search through (user)
        self.__search_path = st.session_state.search_path \
            if 'search_path' in st.session_state else None
        # path get statistics
        self.__stats = st.session_state.search_stats \
            if 'search_stats' in st.session_state else True
        # get context
        self.__context = st.session_state.search_context \
            if 'search_context' in st.session_state else True
        # handle annotation
        self.__anno = st.session_state.anno \
            if 'anno' in st.session_state else None
        # source_files language based on search file
        self.__search_src = st.session_state.search_src \
            if 'search_src' in st.session_state else None
        # target language based on search file
        self.__search_trg = st.session_state.search_trg \
            if 'search_trg' in st.session_state else None
        # number of alignments in search file
        self.__num_align = st.session_state.num_align \
            if 'num_align' in st.session_state else None
        # monolingual or bilingual search (user)
        self.__lang_mode = st.session_state.lang_mode \
            if 'lang_mode' in st.session_state else None
        # language to search through if monolingual search mode (user)
        self.__mono_lang = st.session_state.mono_lang \
            if 'mono_lang' in st.session_state else None
        # context or statistics as search mode (user)
        self.__search_mode = st.session_state.search_mode \
            if 'search_mode' in st.session_state else None
        # pre context for context search (user)
        self.__pre_context = st.session_state.pre_context \
            if 'pre_context' in st.session_state else 1
        # pre context for context search (user)
        self.__post_context = st.session_state.post_context \
            if 'post_context' in st.session_state else 1
        # summarise src lines
        self.__aggr_src = st.session_state.aggr_src \
            if 'aggr_src' in st.session_state else None
        # show info
        self.__show_messages = st.session_state.show_messages \
            if 'show_messages' in st.session_state else None
        # handle paths for info
        self.__path_stats = ""
        self.__path_qual = ""
        self.__path_quant = ""
        self.__search_text = "The alignments are being searched. " \
                             "Please wait a moment ☕."

    def __handle_paths(self):
        # Get the absolute path of the directory containing the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up one directory to access the 'data' directory
        data_dir = os.path.abspath(os.path.join(script_dir, os.pardir, "data"))
        # Path for the download directory
        self.__root_path = os.path.join(data_dir, "search_results")
        self.__gen_path = os.path.join(data_dir, "generated")
        self.__src_path = os.path.join(data_dir, "language_pairs")

    @staticmethod
    def __no_matches():
        styled = f"""
                <div style="background-color: rgba(255, 165, 0, 0.8);
                 padding: 10px; 
                 border-radius: 5px;
                 color: black;">
                    <b>Error:</b>
                    <br>
                    There are no search results. Please check if: <br>
                    1. you chose the correct language
                    <br>
                    2. the regular expression works correctly
                </div>
                """
        st.markdown(styled, unsafe_allow_html=True)

    @staticmethod
    def __no_selection():
        styled = f"""
                <div style="background-color: rgba(255, 165, 0, 0.8);
                 padding: 10px; 
                 border-radius: 5px;
                 color: black;">
                    Please select at least one of the follwing options:<br>
                    <br>
                    * Get Context
                    <br>
                    * Get Statistics
                </div>
                """
        st.markdown(styled, unsafe_allow_html=True)

    @staticmethod
    def __no_regex():
        placeholder = st.empty()
        styled = f"""
            <div style="background-color: rgba(255, 165, 0, 0.8);
             padding: 10px; 
             border-radius: 5px;
             color: black;">
                Please enter a regular expression and press <b>ENTER</b> to apply it.
                <br>
            </div>
            """
        placeholder.markdown(styled, unsafe_allow_html=True)

    @staticmethod
    @st.cache_data
    def __load_data(file_path):
        final_path = os.path.join(file_path, "languages.csv")
        return pd.read_csv(final_path)

    @staticmethod
    def __get_generated(directory):
        # Get the list of files in the directory
        file_list = os.listdir(directory)
        # Iterate through the files
        for filename in file_list:
            if filename == "-":
                continue  # Skip deleting files named "-"
            filepath = os.path.join(directory, filename)
            # Check if file is empty
            if os.path.getsize(filepath) == 0:
                # Remove the empty file
                os.remove(filepath)
                # Remove the empty file from the file_list
                file_list.remove(filename)
        return file_list

    @staticmethod
    def __parse_output(output):
        file_info = []
        # Join all lines into a single string
        joined_lines = '\n'.join(output)
        # Adjusted pattern to capture file size, URL, and documents
        pattern = re.compile(
            r'(\d+\s*(?:MB|GB))\s+(https://[^\s]+)\s+\|\s+(\d+)\s+documents',
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

    def __parse_file_name(self):
        pattern = re.compile(
            r'_(\w{2})_(\w{2})_(\d+)(_parsed)?(_normal)?\.txt')
        match = pattern.search(self.__search_file)
        if match:
            self.__search_src = match.group(1)
            self.__search_trg = match.group(2)
            self.__num_align = match.group(3)
            if match.group(4):
                self.__parse_search = "parsed"
            elif match.group(5):
                self.__parse_search = "normal"
            else:
                self.__parse_search = None

    @staticmethod
    def __message_file_creation_stats(path=None):
        if path is not None:
            styled = f"""
                    <div style="background-color: rgba(50, 205, 50, 0.5); 
                    padding: 10px;
                    border-radius: 5px;
                    color: black;">
                        <b>The search was successful</b>.
                        <br>
                        <br>
                        The <b>statistics file</b> has been generated 
                        under the following path:
                        <br>
                        {os.path.abspath(path)}.
                    </div>
                    """
            st.markdown(styled, unsafe_allow_html=True)

    @staticmethod
    def __message_file_creation_context(path_qual=None, path_quant=None):
        if path_qual is not None and path_quant is not None:
            styled = f"""
                <div style="background-color: rgba(50, 205, 50, 0.5);
                padding: 10px; 
                border-radius: 5px;
                color: black;">
                    <b>The search was successful</b>.
                    <br>
                    <br>
                    The <b>quantitative</b> context file has been generated 
                    under the following path:
                    <br>
                    {os.path.abspath(path_quant)}.
                    <br>
                    <br>
                    The <b>qualitative context</b> file has been generated 
                    under the following path:
                    <br>
                    {os.path.abspath(path_qual)}.
                </div>
                """
            st.markdown(styled, unsafe_allow_html=True)

    @staticmethod
    def __message_file_creation_all(path_stats, path_qual, path_quant):
        styled = f"""
              <div style="background-color: rgba(50, 205, 50, 0.5);
              padding: 10px; 
              border-radius: 5px;
              color: black;">
                  <b>The search was successful</b>.
                  <br>
                  <br>
                  The <b>statistics file</b> has been generated under the following path:
                    <br>
                    {os.path.abspath(path_stats)}.
                    <br>
                    <br>
                  The <b>quantitative</b> context file has been generated 
                  under the following path:
                  <br>
                  {os.path.abspath(path_quant)}.
                  <br>
                  <br>
                  The <b>qualitative context</b> file has been generated 
                  under the following path:
                  <br>
                  {os.path.abspath(path_qual)}.
              </div>
              """
        st.markdown(styled, unsafe_allow_html=True)

    def __lang_to_val(self, src, trg, lang_to_code=True):
        if lang_to_code:
            self.__code_src = self.__languages.loc[
                self.__languages['language'] == src, "code"].item()
            self.__code_trg = self.__languages.loc[
                self.__languages['language'] == trg, "code"].item()

        else:
            self.__search_src = self.__languages.loc[
                self.__languages['code'] == src, "language"].item()
            self.__search_trg = self.__languages.loc[
                self.__languages['code'] == trg, "language"].item()

    def __handle_search(self):
        # make user select search file
        self.__search_file = st.selectbox("Choose a File to Search through",
                                          self.__generated, key="search_file")
        # extract path from file
        self.__search_path = os.path.join(self.__gen_path, self.__search_file)
        if self.__search_file != "-":
            self.__parse_file_name()
            self.__lang_to_val(self.__search_src, self.__search_trg,
                               lang_to_code=False)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                add_vertical_space(2)
                st.markdown(f"**Source Language:**", unsafe_allow_html=True)
                st.markdown(f"{self.__search_src}", unsafe_allow_html=True)
            with col2:
                add_vertical_space(2)
                st.markdown(f"**Target Language:**", unsafe_allow_html=True)
                st.markdown(f"{self.__search_trg}", unsafe_allow_html=True)
            with col3:
                add_vertical_space(2)
                st.markdown(f"**Number of Alignments:**",
                            unsafe_allow_html=True)
                st.markdown(f"{self.__num_align}", unsafe_allow_html=True)
            with col4:
                add_vertical_space(2)
                st.markdown(f"**File Format:**", unsafe_allow_html=True)
                st.markdown(f"{self.__parse_search}", unsafe_allow_html=True)
            st.text_input("Regular Expression for Searching the Data", key="regex")
            if self.__regex is None:
                self.__no_regex()
            else:
                st.selectbox("Language Mode", ("bilingual", "monolingual"), key="lang_mode")
                if self.__lang_mode == "monolingual":
                    # make user choose source_files or target language
                    st.selectbox("Language to Search", (self.__search_src, self.__search_trg), key="mono_lang")
                add_vertical_space(1)
                st.toggle("Get Statistics", key="search_stats", value=True)
                add_vertical_space(1)
                st.toggle("Get Context", key="search_context", value=True)
                add_vertical_space(1)
                if self.__context:
                    st.number_input(label="Number of Lines for Pre-Context", value=1, key="pre_context")
                    st.number_input(label="Number of Lines for Post-Context", value=1, key="post_context")
                    st.checkbox("Keep Annotations for Context", value=True, key="anno")
                if self.__stats and self.__lang_mode == "bilingual":
                    st.checkbox("Summarise Lines for 'src' ", value=True, key="aggr_src")
                st.checkbox("Show Paths for Created Files", value=True, key="show_messages")
                add_vertical_space(3)
                st.button("Do the Search!", key="search_results",
                          on_click=self.__call_search_func)

    def __call_search_func(self):
        scroll_top()
        with st.spinner(self.__search_text):
            parse_param = False if self.__parse_search == "normal" else True
            if not self.__stats and not self.__context:
                self.__no_selection()
            if self.__lang_mode == "monolingual":
                mono_param = True if self.__mono_lang == self.__search_src \
                    else False
                if self.__context:
                    mono_context = MonolingualContext(
                        path=self.__search_path,
                        regex=self.__regex,
                        pre_context=self.__pre_context,
                        post_context=self.__post_context,
                        anno=True if self.__anno else False,
                        src=mono_param,
                    )
                    matches = mono_context.get_matches_context()
                    if len(matches) > 0:
                        self.__path_qual = mono_context.write_context_qual_mono(
                            lang=str(self.__mono_lang).strip(),
                            root_path=self.__root_path)
                        self.__path_quant = mono_context.write_context_quant_mono(
                            lang=str(self.__mono_lang).strip(),
                            root_path=self.__root_path)

                    else:
                        scroll_top()
                        self.__no_matches()
                        return
                if self.__stats:
                    mono_matches = MonolingualStats(path=self.__search_path,
                                                    regex=self.__regex,
                                                    src=mono_param,
                                                    parsed=parse_param
                                                    )
                    counts = mono_matches.get_counts()
                    if counts:
                        self.__path_stats = mono_matches.write_monolingual_stats(
                            lang=str(self.__mono_lang).strip(),
                            root_path=self.__root_path)
                    else:
                        scroll_top()
                        self.__no_matches()
                        return
            elif self.__lang_mode == "bilingual":
                if self.__context:
                    bil_context = BilingualContext(
                        path=self.__search_path,
                        regex=self.__regex,
                        pre_context=self.__pre_context,
                        post_context=self.__post_context,
                        anno=self.__anno
                    )
                    matches = bil_context.get_matches_context()
                    if len(matches) > 0:
                        self.__path_qual = bil_context.write_context_qual_bil(
                            l1=str(self.__search_src).strip(), l2=str(self.__search_trg).strip(),
                            root_path=self.__root_path)
                        self.__path_quant = bil_context.write_context_quant_bil(
                            l1=str(self.__search_src).strip(), l2=str(self.__search_trg).strip(),
                            root_path=self.__root_path)
                    else:
                        scroll_top()
                        self.__no_matches()
                        return
                if self.__stats:
                    src_aggr_param = True if self.__aggr_src else False
                    bil_matches = BilingualStats(path=self.__search_path,
                                                 regex=self.__regex, src_aggregate=src_aggr_param,
                                                 parsed=parse_param)
                    counts = bil_matches.get_counts()
                    if counts:
                        self.__path_stats = bil_matches.write_bilingual_stats(
                            l1=str(self.__search_src).strip(),
                            l2=str(self.__search_trg).strip(),
                            root_path=self.__root_path)
                    else:
                        scroll_top()
                        self.__no_matches()
                        return
        self.__messages()

    def __messages(self):
        # only show messages and paths if selected
        if self.__show_messages:
            if self.__context and self.__stats:
                self.__message_file_creation_all(path_stats=self.__path_stats,
                                                 path_quant=self.__path_quant,
                                                 path_qual=self.__path_qual)
            elif self.__stats:
                self.__message_file_creation_stats(path=self.__path_stats)
            elif self.__context:
                self.__message_file_creation_context(path_qual=self.__path_qual, path_quant=self.__path_quant)

    def build(self):
        rename_files()
        edit_design()
        st.title("Search Alignments", anchor=False)
        add_vertical_space(2)
        self.__handle_search()


if __name__ == "__main__":
    test = SearchAlign()
    test.build()
