import os
import re
import pandas as pd
import streamlit as st
from st_pages import show_pages_from_config


def rename_files():
    # Determine the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    directory_src = os.path.join(current_directory, "data", "source_files")
    directory_lang = os.path.join(current_directory, "data", "language_pairs")
    # read in parsed languages to check for file info
    parsed_df = pd.read_csv(os.path.join(directory_lang, "languages_parsed.csv"))
    # capture patterns for files
    xml_pattern = r'([a-z]{2})-([a-z]{2})\.xml\.gz'
    zip_pattern = r'([a-z]{2})\.zip'
    # go through all files to capture files that need to be renamed
    try:
        for filename in os.listdir(directory_src):
            # match files
            xml_match = re.match(xml_pattern, filename)
            zip_match = re.match(zip_pattern, filename)
            if xml_match:
                # capture languages for alignment file
                lang_code1 = xml_match.group(1)
                lang_code2 = xml_match.group(2)
                # rename alignment file
                new_filename = f'OpenSubtitles_latest_xml_{lang_code1}-{lang_code2}.xml.gz'
                os.rename(os.path.join(directory_src, filename), os.path.join(directory_src, new_filename))
            elif zip_match:
                # capture language for each language
                lang_code = zip_match.group(1)
                # check whether it occurs in a parsed
                parsed = lang_code in parsed_df['code'].values
                new_filename = f'OpenSubtitles_latest_{lang_code}.zip'
                if parsed:
                    new_filename = new_filename.replace(f'_{lang_code}.zip', f'_parsed_{lang_code}.zip')
                else:
                    new_filename = new_filename.replace('.zip', '_normal.zip')
                os.rename(os.path.join(directory_src, filename), os.path.join(directory_src, new_filename))
    except FileExistsError:
        pass


def hide_streamlit_content():
    st.markdown(
        """ <style>
        #MainMenu {
        visibility: hidden;
        }

            div[data-testid="InputInstructions"]{
                display: none;
            }
            div[data-testid="stToolbar"]{
                display: none;
            }
            svg[xmlns="http://www.w3.org/2000/svg"][width="18"][height="18"][viewBox="0 0 24 24"][fill="none"]
            [stroke="currentColor"][stroke-width="2"][stroke-linecap="round"][stroke-linejoin="round"] {
        display: none !important;
    }

        </style> 
        """,
        unsafe_allow_html=True)


def scroll_top():
    js_top = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        console.log(body);
        body.scrollTop = 0;
    </script>
    '''
    st.components.v1.html(js_top, height=0)


def app_appear():
    # custom = """
    # <style>
    # header {visibility: hidden;}
    # div[data-testid="stAppViewContainer"] {
    #         background: linear-gradient(148deg, rgba(72,165,189,1) 22%, rgba(15,66,173,1) 53%);
    # </style>
    # """
    # st.markdown(custom, unsafe_allow_html=True)
    # # linear-gradient(-32deg, rgba(243, 239, 228, 1) 15%, rgba(138, 212, 209, 1) 68%)
    # st.markdown(
    #     """ <style>
    #    [data-testid="stSidebar"] {
    #     background: linear-gradient(to right, floralwhite, cornsilk);
    #     font-family: Helvetica, sans-serif;
    #     font-size: 3px;
    #     }
    #     [data-testid="stSidebarContent"] {
    #     font-size: 3px;
    #     }
    #     [data-testid="stForm"] {
    #     border: none !important;
    #     border-radius: 0 !important;
    #     padding: 0 !important;
    #     }
    #     [data-testid="stExpander"] {
    #     background: linear-gradient(to right, white, azure);
    #     border: 1px solid #ccc; /* Example border */
    #     border-radius: 10px; /* Adjust the value as needed */
    #     box-sizing: border-box; /* Include padding and border in the element's total width and height */
    #     }
    #     .st-emotion-cache-5xcs9u > summary > span > div > p {
    #     font-size: 18px; /* Adjust the font size for the paragraph */
    #     font-weight: bold;
    #     }
    #
    #     </style>
    #     """,
    #     unsafe_allow_html=True)
    footer_html = """
        <style>
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                color: white;
                text-align: right;
                padding: 10px 50px 10px 0;
            }
        </style>
        <div class="footer">
            <p>Made with Streamlit</p>
        </div>
    """

    # Render the footer using st.markdown
    st.markdown(footer_html, unsafe_allow_html=True)
    show_pages_from_config()
    with st.sidebar:
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        st.markdown("This tool was developed by Johanna Rockstroh and Jan Fliessbach and is licensed "
                    "under the MIT License. Its use is based on "
                    "[OPUS](https://opus.nlpl.eu/) "
                    "([Jörg Tiedemann](https://scholar.google.com/citations?user=j6V-rOUAAAAJ))  "
                    "and [opustools](https://pypi.org/project/opustools/) "
                    "([Aulamo et al. 2020](https://aclanthology.org/2020.lrec-1.467/)).")


def edit_design():
    hide_streamlit_content()
    app_appear()
