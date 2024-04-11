import os
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from resources import edit_design, rename_files
st.set_page_config(page_title="Introduction", page_icon="📖", layout="centered")
# set current working directory to be displayed
if "cwd" not in st.session_state:
    st.session_state["cwd"] = os.path.dirname(os.path.abspath(__file__))


def show_intro():
    st.title("Welcome to OpuSearch", anchor=False)
    st.markdown("<span style='font-size:20px;'>With OpuSearch, explore the vast collection of Opus OpenSubtitles"
                " with ease as you generate alignments and employ regular expressions"
                " for efficient searches.</span>", unsafe_allow_html=True)
    add_vertical_space(2)
    with st.expander("**What can I do with OpuSearch?**"):
        st.markdown("With OpuSearch you can generate alignments and search them after using regular expressions. "
                    "The source files used for the generation are provided by Opus OpenSubtitles **add citation** "
                    "and ",
                    unsafe_allow_html=True)
    add_vertical_space(1)
    with st.expander("**What is an alignment?**"):
        st.markdown("An alignment in parallel corpora is the matching of equivalent "
                    "texts or segments in different languages. "
                    "It enables the association of corresponding elements for tasks like translation "
                    "and cross-lingual analysis. In case of Opus OpenSubtitles we always have a mapping between a "
                    "**source** and a **target**.",
                    unsafe_allow_html=True)
    add_vertical_space(1)
    with st.expander("**How can I generate alignments?**"):
        st.markdown("You can generate alignments out of source files on the page **Generate Alignments**. "
                    "For this you first need to decide for the mode of the source files: "
                    "**normal** or **parsed**. Afterwards you set the languages for the source "
                    "and target. Finally, you set the number of alignments. "
                    "If the needed source files for the languages and the"
                    " mappings are not found, you can download them with this software, by either clicking on "
                    "**Download Data** or the links provided by the programme in case you want to download "
                    "the data manually. If you use this software for the first time, "
                    "you need to take some time to download the necessary data.",
                    unsafe_allow_html=True)
    add_vertical_space(1)
    with st.expander("**What is the difference between 'parsed' and 'normal' for generating alignments?**"):
        st.markdown("The parsed version contains metadata, such as the lemma "
                    "and Part of Speech (POS) tag for every token, whereas the normal version "
                    "only contains the text itself. "
                    "Opus OpenSubtitles does not offer the parsed version for every language and hence every language "
                    "combination. If the parsed version is available, we advise you to choose this one to include more "
                    "information, which might be useful later on.",
                    unsafe_allow_html=True)
    add_vertical_space(1)
    with st.expander("**How can I search alignments?**"):
        st.markdown("After generating the alignments, you can search them using regular expressions. In the first step,"
                    " you select the file you want to search through (the output of the generation). "
                    "For this, you can either select the normal or parsed format."
                    " Afterwards you are presented several options: <br><br>",
                    unsafe_allow_html=True)
        content = ""
        content += "| <span style='font-size: 13px'>Setting</span> | <span style='font-size: 13px'>Values</span> | " \
                   "<span style='font-size: 13px'>Description</span> | <span style='font-size: 13px'>Used for</span> " \
                   "|\n"
        content += "|---------|------|-------------|----------|\n"
        content += "| <span style='font-size: 13px'>Regular Expression</span> | <span style='font-size: 13px'>set by " \
                   "user</span> | <span style='font-size: 13px'>Specifies the Regular Expression for the search. " \
                   "This value is obligatory.</span> | <span style='font-size: 13px'>All Option Types</span> |\n"
        content += "| <span style='font-size: 13px'>Ignore Case</span> | " \
                   "<span style='font-size: 13px'>set by " \
                   "user</span> | <span style='font-size: 13px'>If selected, the Regular Expression will be applied " \
                   "in upper and lower case without further specification. " \
                   "</span> | <span style='font-size: 13px'>All Option Types</span> |\n"
        content += "| <span style='font-size: 13px'>Language Mode</span> | <span style='font-size: 13px'>bilingual / " \
                   "monolingual</span> | <span style='font-size: 13px'>Specifies the language mode. If " \
                   "monolingual is selected the language has to be specified. " \
                   "Only the <b> source language</b> can be searched in the " \
                   "bilingual mode.</span> | <span style='font-size: " \
                   "13px'>All Option Types</span> |\n"
        content += "| <span style='font-size: 13px'>Option Type</span> | <span style='font-size: 13px'>" \
                   "Get Statistics / Get Context</span> | <span style='font-size: 13px'>Specifies whether to get " \
                   "statistics or context. At least one value has to be selected.</span> | " \
                   "<span style='font-size: 13px'>All Language Modes</span> |\n"
        content += "| <span style='font-size: 13px'>Get Statistics</span> | <span style='font-size: " \
                   "13px'>yes/no</span> | <span style='font-size: 13px'>One output (.csv-file) including counts for " \
                   "matches, POS, lemma, token (if parsed) and translation of matches (if bilingual).</span> | <span " \
                   "style='font-size: 13px'>All Language Modes</span> |\n"
        content += "| <span style='font-size: 13px'>Summarise Lines for 'src'</span> | <span style='font-size: " \
                   "13px'>yes/no</span> | <span style='font-size: 13px'>Just use the line (src) in which the match " \
                   "was found or get all lines belonging to the alignment. Lines for target are summarised " \
                   "automatically.</span> | <span style='font-size: 13px'>Get Statistics + bilingual</span> |\n"
        content += "| <span style='font-size: 13px'>Get Context</span> | <span style='font-size: 13px'>yes/no</span> " \
                   "| <span style='font-size: 13px'>Two different outputs: Results in a qualitative (.txt-file) " \
                   "and quantitative (.csv-file) format.</span> " \
                   "| <span style='font-size: 13px'>All Language Modes</span> |\n"
        content += "| <span style='font-size: 13px'>Number of Lines for Pre-Context</span> | <span style='font-size: " \
                   "13px'>1 (default) - n</span> | <span style='font-size: 13px'>Number of lines appearing before " \
                   "the match.</span> | <span style='font-size: 13px'>Get Context</span> |\n"
        content += "| <span style='font-size: 13px'>Number of Lines for Post-Context</span> | <span style='font-size:" \
                   " 13px'>1 (default) - n</span> | <span style='font-size: 13px'>Number of lines appearing after " \
                   "the match.</span> | <span style='font-size: 13px'>Get Context</span> |\n"
        content += "| <span style='font-size: 13px'>Keep Annotations for Context</span> | <span style='font-size: " \
                   "13px'>yes/no</span> | <span style='font-size: 13px'>Keep or remove annotations provided by Opus " \
                   "OpenSubtitles.</span> | <span style='font-size: 13px'>Get Context</span> |\n"
        content += "| <span style='font-size: 13px'>Show Paths for Created Files</span> | <span style='font-size: " \
                   "13px'>yes/no</span> | <span style='font-size: 13px'>Show the path under which the resulting " \
                   "files have been created. A maximum of three paths can be shown.</span> | <span style='font-size: " \
                   "13px'>All Option Types and Language Modes</span> |\n"
        st.markdown(content, unsafe_allow_html=True)
    add_vertical_space(1)
    with st.expander("**What can I do with the search results?**"):
        st.markdown(
            "You can get two kinds of output for the search:",
            unsafe_allow_html=True)
        st.markdown("* statistics", unsafe_allow_html=True)
        st.markdown("* context", unsafe_allow_html=True)
        st.markdown("The content of both files is linked via the file IDs that are displayed "
                    "in the respective output. So if you are looking for a specific phrase "
                    "displayed in the statistics you can locate the phrase in the context files by"
                    " searching for the ID.", unsafe_allow_html=True)
    add_vertical_space(1)
    with st.expander("**Can I use an external hard drive for storing the data?**"):
        st.markdown("Yes, it is possible to store the corpus files, the generated alignments and your search results "
                    "on an external hard drive of your choice. "
                    "For more information go to the page *Use External Hard Drive*.",
                    unsafe_allow_html=True)


def main():
    rename_files()
    edit_design()
    show_intro()


if __name__ == "__main__":
    main()
