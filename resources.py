import os
import re
import time
import keyboard
import psutil
import toml
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
    custom = """
    <style>
    header {visibility: hidden;}
    div[data-testid="stNotification"] {
        border: 2px solid rgba(255, 255, 255, 0.7); /* Opaque white border */
        padding: 10px; /* Adjust padding as needed */
        background-color: transparent; /* Transparent background */
    }
    div[data-testid="stAppViewContainer"] {
            background: linear-gradient(86deg, rgba(20,45,160,1) 54%, rgba(35,117,174,1) 98%);
    </style>
    """
    st.markdown(custom, unsafe_allow_html=True)
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
    primaryColor = toml.load(".streamlit/config.toml")['theme']['primaryColor']
    footer_html = f"""
        <style>
            .footer {{
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                color: white;
                text-align: right;
                padding: 10px 50px 10px 0;
            }}
            div.stButton > button:first-child {{
                border: 3px solid {primaryColor};
                border-radius: 20px;
            }}
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
        st.markdown("This tool was developed by Johanna Rockstroh and Jan Fliessbach and is licensed "
                    "under the MIT License. Its use is based on "
                    "[OPUS](https://opus.nlpl.eu/) "
                    "([Jörg Tiedemann](https://scholar.google.com/citations?user=j6V-rOUAAAAJ))  "
                    "and [opustools](https://pypi.org/project/opustools/) "
                    "([Aulamo et al. 2020](https://aclanthology.org/2020.lrec-1.467/)).")
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span style="color:orange;"><b>Warning:</b><br>Do not delete any folders or files from '
                    'the existing structure,'
                    ' as this may cause the application to crash.</span>', unsafe_allow_html=True)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        st.sidebar.button("Close Application", on_click=shut_down)
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.sidebar.columns([1, 3])
        with col1:
            st.image("data/github.png", use_column_width="always")
        with col2:
            # Add some CSS styling to align the link with the center of the image
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="display: flex; align-items: center;"><a href="https://github.com/JR0cky/OpuSearch">'
                'Link to Github Repository</a></div>',
                unsafe_allow_html=True
            )


def shut_down():
    # Give a bit of delay for user experience
    time.sleep(2.5)
    # Close streamlit browser tab
    keyboard.press_and_release('ctrl+w')
    # Terminate streamlit python process
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()


def edit_design():
    hide_streamlit_content()
    app_appear()


def info_external_hard_drive(st, page=None):
    if page == "search":
        st.page_link("pages/external_drive.py", icon="💾", label="Store the search results on an external hard drive")
    elif page == "generation":
        st.page_link("pages/external_drive.py", icon="💾", label="Store the aligments and source files"
                                                                " on an external hard drive")
    elif page is None:
        st.page_link("pages/external_drive.py", icon="💾", label="Use an external harddrive for your data.")


def info_cwd(st):
    st.info(f"Your Current Working directory: {st.session_state['cwd']}")
