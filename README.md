# Testing Quantum Metal and Ansys on Linux

## Prerequisites

- We use `uv` to manage dependencies for this project. 
  - First install `uv` on your system ([installation instructions here](https://docs.astral.sh/uv/getting-started/installation/)). 
  - `uv` will manage Python and any Python dependencies for this project. Conda is not used.
  - If your system has a global Python installation, `uv` may try to use that by default, potentially creating problems. For such cases, set the environment variable `UV_MANAGED_PYTHON` or specify the `--managed_python` flag in any `uv run` commands (see [here](https://docs.astral.sh/uv/reference/cli/#uv-run--managed-python)).
- Ensure that Ansys Electronics Desktop (AEDT) is installed on your system and available. 
  - The scripts below have been tested on Ansys 2025R2 on Windows 11 and Rocky Linux 8.1.
  - Ensure the appropriate environment variables are set for your Ansys installation. See the pyaedt [documentation about linux support](https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html#linux-support). `pyaedt` uses these variables to locate your Ansys installation.
  - For HPC systems, installed software may be made available in the form of modules (typically using something like [spack](https://spack.readthedocs.io/en/latest/) or [EasyBuild](https://easybuild.io/)). In such cases, you may need to import the installed module to have access to Ansys. Please contact your HPC sysadmin to resolve issues related to Ansys installations on your HPC. 

To run the scripts and test functionality, clone the repo: 

```bash
git clone https://github.com/abhishekchak52/metal_ansys_linux_test.git
```


### Python dependency management

Sync the Python environment before running any scripts. This ensures that all the required dependencies are correctly installed in the virtual environment. Run the following command in the root of this repository: 

```bash
uv sync
```

Note that any extra manually-installed packages may be affected by this command. Read more about *exact syncing* in the uv documentation [here](https://docs.astral.sh/uv/reference/cli/#uv-sync). 

To update various package dependencies to their latest available version (which satisfy the constraints set by the environment specifications set in `pyproject.toml` and the dependencies listed within), run the following command from the root of this repository:

```bash
uv lock -U
```

This will show you a summary of the version updates for various dependencies. 

## Running Scripts

In general, you can run the various test scripts using the following command (from the repository root):

```bash
uv run scripts/<script_name>.py
```

`uv` will run the script in the virtual environment for the project. 

### Setting environment variables

Some script functionality is controlled using environment variables: 
- `QISKIT_METAL_HEADLESS`: Sets non-graphical mode for Quantum Metal. When set, this will bypass any GUI-related imports. 
- `PYEPR_USE_PYAEDT`: Force the `pyaedt` Ansys backend for pyEPR on Windows (the legacy COM backend is used by default). On Linux, `pyaedt` is the only available backend. 
- `PYAEDT_NON_GRAPHICAL`: Sets nongraphical mode for `pyaedt`. Run Ansys using `pyaedt` without loading the AEDT GUI. 

These environment variables must be set before script execution. On Linux, it is fairly easy to set these for a single command. For example, 

```bash
ENVVAR1=value1 ENVVAR2=value2 uv run scripts/<script_name>.py
```
Things are slightly trickier on Windows, so we recommend setting these environment variables at the top of the script using Python instead. Add the following lines at the top of the script before running: 

``` python
# First line of script. Ensure there are no imports above this. 
import os
os.environ["ENVVAR1"] = "value1"
os.environ["ENVVAR2"] = "value2"
# The rest of the original script follows. 
```

For example, to run a script in headless mode on Linux, use the following command:

```bash
QISKIT_METAL_HEADLESS=1 PYAEDT_NON_GRAPHICAL=1 uv run scripts/<script_name>.py
```
### Forward Pass Validation

There are three scripts, one for each ML model/SQuADDS dataset: 

- [TransmonCross_cap_forward_pass.py](scripts/TransmonCross_cap_forward_pass.py): LOM analysis for transmon cross and resonator claw.
- [NCap_cap_forward_pass.py](scripts/NCap_cap_forward_pass.py):  Interdigitated capacitor for resonator coupling. 
- [RouteMeander_eigenmode_forward_pass.py](scripts/RouteMeander_eigenmode_forward_pass.py): EPR analysis for Xmon qubit and resonator.

These scripts will print out a table comparing various design and simulation-related parameters and results upon completion. Note that the last script runs an eigenmode simulation which can be time-memory intensive. In preliminary testing, this script ran for approximately 1 hour and used ~50 GB RAM. The script may fail if it runs out of memory. 

### Other Scripts

Some other test scripts are also provided: 
- [lom_test.py](scripts/lom_test.py): Minimal LOM analysis script based on Quantum Metal tutorial. 
- [epr_test.py](scripts/epr_test.py): Minimal EPR analysis script based on Quantum Metal tutorial. 
- [squadds_xmon_lom_test.py](scripts/squadds_xmon_lom_test.py): Minimal LOM analysis for an Xmon qubit using SQuADDS. 

## Development Setup

This repository uses [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to maintain local copies of Quantum Metal, pyEPR and SQuADDS for easy development and debugging. These dependencies will be installed as editable in the project virtual environment. Use the following command to clone the repository and its submodules:

```bash
git clone --recurse-submodules https://github.com/abhishekchak52/metal_ansys_linux_test.git
```
Then switch to the `dev` branch, which installs locally cloned versions of my forks of Quantum Metal, SQuADDS and pyEPR in the virtual environment. 
```bash
git checkout dev
```
This may enable easier debugging and contribution. Note that this is not required if you only want to run the scripts. 