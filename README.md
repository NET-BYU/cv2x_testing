# cv2x_testing
NET Lab methods for RSU performance testing.

## Repository Setup
---
### Python Libraries
(If you are familiar with things like virtual environments, go ahead and just install from requirements.txt (make sure your environemtn name ends in `-env`). If you aren't, go ahead and unfold the following section for instructions on how to do that.)
<details>
    <summary>Click Here</summary>
In order to run the files in this repo, you will need certain python libraries installed. This section walks you through doing this in a virtual environment. For those who are are already confident in creating their venv or who just want to add the lkibraries to their machine, you can just jump to step 3.

**0. Make sure you have Python's virtual environment library**
```bash
pip install virtualenv
```
This is a super useful library, and you can read more about it [here](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

**1. Create your virtual environment**
```bash
python3 -m venv <name>env
```
_Please make sure that your virtual envornment name ends with `-env` if you intend to develop on Git, or else add it to the `.gitignore` file!_

**2. Activate your virtual environment**
```bash
source <name>env/bin/activate
```
When you are done developing on the virtual environment, you can just exit it using the terminal command 
```bash
deactivate
```

**3. Install the required python libraries**
```bash
pip install -r requirements.txt
```
This should install all the libraries needed. If you are not using a virtual enviroment, they will be installed to your whole python environment.
</details>

---
### Build the code

Run the following command to setup your folder:
```bash
python3 build.py
```
This will perform several functions, primarily giving you some blank folders to store data and results as well as creating an untracked `.yaml` file that will be crucial for the testing.