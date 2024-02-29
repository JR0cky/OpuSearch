# OpuSearch
This is a Streamlit Application for the software project *OpuSearch*.

## Setup Overview
0. Download [Python 3.11](https://www.python.org/downloads/release/python-3116/) and make sure to add Python to your **Path Variable** (See [here](https://realpython.com/add-python-to-path/) for more information or take the instruction linked under 3.3). Better use the Python Website for installing instead of Microsoft Store (Windows). 
1. Download [Git](https://git-scm.com/download/win). 
2. Clone the repository.
3. Create a virtual environment.
4. Install the necessary packages into the virtual environment.
5. Run the app.

## Detailed Setup Instruction

### 2. Cloning the repository

Open a command line tool of your choice and go to the root directory (OPUS-OpenSubTitles-Processing) of 
the project. For Windows you can go to the root directory via the Explorer and open a Git Bash or cmd 
there using the context menu with right-click. There should be a similar option for MacOS. Otherwise, you can use **cd** to change the directory over the commandline. 
To make things easier you can copy the path to ypur preferred directory from your file explorer or finder and put it after **cd**.

```
git clone https://github.com/JR0cky/OPUS-OpenSubTitles-Processing.git
```

Remark: You may need to [generate a token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) to be able to clone.
### 3. Creating a virtual environment
To create a virtual environment for this project you can use different frameworks.
This example shows how to do it with python and **venv**:

1. Open a command line tool of your choice and go to the root directory (OPUS-OpenSubTitles-Processing) of the project.
For Windows you can go to the root directory via the Explorer and open a Git Bash or cmd there using the context menu with right-click.

2. In the command line (bash or cmd) type the following:
```
python -m venv venv
```
Make sure to use "venv" for the environment name, as the scripts for running the app (OpuSearch.bat and OpuSearch.sh)
will not work with a different name.

Remark: If Python is not recognized as a module you need to add it to your system's path
(see this [instruction](https://realpython.com/add-python-to-path/)).

3. Now activate the environment with the following command (from the project's root directory):

**For Windows (cmd):**
```
venv\Scripts\activate.bat
```
If you see the name of your environment in parentheses at the beginning of the line then you were successful.

**For Windows (Powershell --> Terminal in VSCode and PyCharm):**

```
venv\Scripts\Activate.ps1
```

Remark: If you do not have permission to run this command, 
you may follow these [instructions](https://support.enthought.com/hc/en-us/articles/360058403072-Windows-error-activate-ps1-cannot-be-loaded-because-running-scripts-is-disabled-UnauthorizedAccess-).

**For Linux and MacOS (including Git Bash for Windows):**
```
source venv/Scripts/activate
```
### 4. Installing the packages


Once you have activated your virtual environment, you can install the required packages 
with the following command:

```
pip install -r requirements.txt
```
The installation is finished if you see your user name and the environment name displayed as before.

### 5. Running the Streamlit App

After installing the necessary packages, you can double click on **OpuSearch.bat** (Windows) or **OpuSearch.sh** (Linux).

Alternatively, you can run this code from the root directory to display the content on your local host. 
Use the following command:

```
streamlit run home.py
```

This will open a terminal (command line) automatically.
You will be asked to enter your email in the terminal if you start the app for the first time.
You can skip this step by pressing ENTER. 

Afterwards, the app will be opened in a new tab in your default browser.