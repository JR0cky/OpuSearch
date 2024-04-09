# OpuSearch
This is a Streamlit Application for the software project *OpuSearch*.

## Setup Overview
0. Check if you have Python already installed: [How to Python](https://www.howtogeek.com/796841/check-python-version/). If the command is not found, or a different version than 3.11.X, download [Python 3.11](https://www.python.org/downloads/release/python-3116/) and make sure to add Python to your **Path Variable** (See [here](https://realpython.com/add-python-to-path/) for more information or take the instruction linked under 3.3). For **Windows**, better use the Python Website for installing instead of Microsoft Store. 
1. Check if you have Git installed: [How to Git](https://www.linode.com/docs/guides/how-to-install-git-on-linux-mac-and-windows/) If Git is not on your computer, install it for [Windows](https://git-scm.com/download/win) or for [macOS/Linux](https://git-scm.com/download/mac). If necessary, install the package manager [homebrew](https://brew.sh/) beforehand (**macOS/Linux**).
2. Clone the repository.
3. Create a virtual environment.
4. Install the necessary packages into the virtual environment.
5. Run the app.

## Detailed Setup Instruction

### 2. Cloning the repository
#### 2.1 
Open a command line tool of your choice. <br>
#### 2.2. 
Navigate to your preferred local directory, ideally something like "Documents". Make sure that this is not a cloud folder, as the software will store large amounts of data to work.
For navigating in **Windows** you can go to the preferred directory via the Explorer and open a Git Bash or cmd 
there using the context menu with right-click. Otherwise, you can use **cd** to change the directory over the commandline (on all operating systems). To make things easier you can copy the path to your preferred directory from your file explorer or finder and put it after **cd**. <br>
#### 2.3. 
Once you have arrived at the desired locarion, copy and paste the following command:


```
git clone https://github.com/JR0cky/OpuSearch.git
```

Remark: You may need to [generate a token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) to be able to clone.

### 3. Creating a virtual environment
To create a virtual environment for this project you can use different frameworks.
This example shows how to do it with python and **venv**:

#### 3.1. 
Open a command line tool of your choice. <br>
#### 3.2 
Go to the root directory (OpuSearch) of the project.
For **Windows** you can go to the root directory via the Explorer and open a Git Bash or Terminal there using the context menu with right-click. Otherwise, you can navigate there (on all operating systems) using:
```
cd OpuSearch
```


#### 3.3 
In the command line (bash or cmd) type the following:
```
python -m venv venv
```
**or**, depending on your operating system, use

```
python3 -m venv venv
```


Make sure to use "venv" for the environment name, as the script *OpuSearch.bat* for running the app
will not work with a different name.

If Python is not recognized as a module you need to add it to your system's path
(see this [instruction](https://realpython.com/add-python-to-path/)).

You can check whether the folder *venv* has been created by using the command *dir* (Windows) or *ls* (Linux/macOS) 
to list the content of the directory you are currently in. Otherwise, you can take a look via the file explorer.

#### 3.4 

Now activate the environment with the following command from the project's root directory (OpuSearch):

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
source venv/bin/activate
```

If you see *(venv)* at the beginning of your command prompt, the virtual environment has been activated.

### 4. Installing the packages


Once you have activated your virtual environment and still being in the project's root directory, you can install the required packages 
with the following command:

```
pip install -r requirements.txt
```
The installation is finished if you see your user name and the environment name displayed as before.

### 5. Running the Streamlit App

After installing the necessary packages, you  can start the application. For **Windows** you can do this double clicking on **OpuSearch.bat**, which is in the project's root directory. 
You may need to allow its execution before the application starts running.

Alternatively (including **macOs** and **Linux**), you can run this code from the project's root directory (OpuSearch) to display the content on your local host. 
Use the following command:

```
streamlit run home.py
```

This will open a terminal (command line) automatically.
You will be asked to enter your email in the terminal if you start the app for the first time.
You can skip this step by pressing ENTER. 

Afterwards, the app will be opened in a new tab in your default browser.