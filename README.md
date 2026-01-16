# Testing Quantum Metal and Ansys on Linux

This repository uses [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to maintain local copies of Quantum Metal and pyEPR for easy development and troubleshooting. Both these dependencies will be installed as editable in the project virtual environment. Use the following command to clone the repository and its submodules:

```
git clone --recurse-submodules https://www.github.com/abhishekchak52/metal_ansys_linux_test.git
```

We use uv to manage dependencies for this project. First install `uv` on your system ([installation instructions here](https://docs.astral.sh/uv/getting-started/installation/)). 

## Test Scripts

There are some test scripts to check functionality (more to be added later): 

- [lom_test.py](scripts/lom_test.py)

Run them using the following command: 

```sh
uv run ./scripts/lom_test.py
```

Currently, running the script will bring up the Ansys EDT GUI. You can see the design being drawn inside of Ansys. After that, the Q3D simulation will run for a number of iterations. Finally the capacitance matrix should be printed out as a pandas DataFrame and the Ansys GUI will exit.  

```
                          bus1_connector_pad_Q1  bus2_connector_pad_Q1  ground_main_plane  pad_bot_Q1  pad_top_Q1  readout_connector_pad_Q1        
bus1_connector_pad_Q1                 51.108579              -0.420905         -34.350276   -1.560883  -13.640273                 -0.204364        
bus2_connector_pad_Q1                 -0.420905              55.440790         -36.740701  -14.419409   -1.849197                 -1.031396        
ground_main_plane                    -34.350276             -36.740701         239.516767  -31.539787  -38.285971                -37.526670        
pad_bot_Q1                            -1.560883             -14.419409         -31.539787  100.177557  -30.988633                -19.467099        
pad_top_Q1                           -13.640273              -1.849197         -38.285971  -30.988633   89.664766                 -2.245261        
readout_connector_pad_Q1              -0.204364              -1.031396         -37.526670  -19.467099   -2.245261                 61.534274 
```
Your result may differ from the one shown above, but the general structure and row/column names should be the same. 


## Test notebooks

Run the following command in the root of the repository. This will open the tutorial notebooks from the qiskit-metal repo: 

```
uv run jupyter lab packages/qiskit-metal/tutorials
```

For now, I've tested the following tutorial notebooks: 

- 3.3 Render your design to Ansys
- 4.01 Capacitance and LOM
- 4.02 Eigenmode and EPR

Note that not all cells should be run in the notebooks listed above. Please follow the text instructions in the notebooks. 

To update various package dependencies, run the following command from the root of this repository:

```
uv lock -U
```

Note that Ansys Electronics Desktop (AEDT) must be installed on your system and the appropriate environment variables should be set so that pyaedt can automatically find the installation. Please refer to the [pyaedt documention for linux support](https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html#linux-support). 



