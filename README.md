# Testing Quantum Metal and Ansys on Linux

This repository uses [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to maintain local copies of Quantum Metal and pyEPR for easy development and troubleshooting. Both these dependencies will be installed as editable in the project virtual environment. Use the following command to clone the repository and its submodules:

```
git clone --recurse-submodules https://www.github.com/abhishekchak52/quantum-metal-ansys-testing.git
```

We use uv to manage dependencies for this project. First install `uv` on your system ([installation instructions here](https://docs.astral.sh/uv/getting-started/installation/)). 
Run the following command in the root of the repository. This will open the tutorial notebooks from the qiskit-metal repo: 

```
uv run jupyter lab packages/qiskit-metal/tutorials
```

To update various package dependencies, run the following command from the root of this repository:

```
uv lock -U
```

Note that Ansys Electronics Desktop (AEDT) must be installed on your system and the appropriate environment variables should be set so that pyaedt can automatically find the installation. Please refer to the [pyaedt documention for linux support](https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html#linux-support). 



