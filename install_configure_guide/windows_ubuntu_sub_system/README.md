Marisco VS code with Ubuntu sub system
================
The Marisco package is developed within Jupyter Notebooks using  [nbdev](https://nbdev.fast.ai/). The Jupyter Notebooks used for development are located at marisco/nbs/. The Marisco package, which is created using these notebooks, is located at marisco/marisco/.

## Prerequisites ( Windows )
Marisco with Visual Studio Code using Windows Subsystem for Linux (WSL).

Visual Studio Code

1. Download and install [Visual Studio Code for Windows](https://code.visualstudio.com/download).

2. Download and install [Windows Terminal](https://www.microsoft.com/store/productId/9N0DX20HK701?ocid=pdpshare). In Windows Terminal, open a Windows Powershell terminal (the default terminal) and install wsl.

    ```
    wsl --install
    ```
    To view specific Ubuntu versions, in Powershell terminal run
    ```
    wsl --list --online
    ```
    To install a specific Ubuntu version, in Powershell terminal run
    ```
    wsl --install {Name}
    ```
    e.g. 
    ```
    wsl --install -d Ubuntu
    ```
    Complete the installation steps by creating a user (e.g, marisco) and a password for this user. 

    To list installed Linux distributions 
    ```
    wsl --list --verbose
    ```

3. Restart and open Visual Studio Code, and then install the extension 'Remote Development'. The shortcut to extensions in Visual Studio Code is Ctrl+Shift+X. Restart Visual Studio Code, then go to Remote explorer and ensure that 'WSL Targets' are available.
<p align="center">
  <img src="https://github.com/niallmurphy93/marisco/assets/43383736/22c343ed-cd03-4980-8cd0-cba59b29c39b">
</p>
Select 'Connect in current window' for the environment (e.g. Ubuntu) of your choice. 
<p align="center">
  <img src="https://github.com/niallmurphy93/marisco/assets/43383736/c650e418-c358-44cf-8daf-aa5f2ced4daf">
</p>
The current environment is shown in the bottom left of Visual Studio Code.
<p align="center">
  <img src="https://github.com/niallmurphy93/marisco/assets/43383736/9e84ae7f-027c-48d4-9b52-049ea46d7515">
</p>
5. In Visual Studio, go to the menu bar and navigate to 'terminal' and then select 'new terminal'. 
    <p align="center">
      <img src="https://github.com/niallmurphy93/marisco/assets/43383736/28edbfa3-4550-499d-abd4-488b4af5d229">
    </p>
    
6. In your new VS Code terminal, navigate to your home environment.
     ```
        cd /home/{username}
     ```
    e.g. 
     ```
        cd /home/marisco
    ```
7. In the Terminal of Visual Studio, install Python  (Recommended [Mambaforge](https://github.com/conda-forge/miniforge))
   <p align="center">
        <img height=450 width= 450 src="https://github.com/niallmurphy93/marisco/assets/43383736/fe1edd71-293f-486e-930e-3b9bc6b27db9">
    </p>
    Copy the download link based on your architecture.
    
    |OS	|Architecture|	Download|
    | ----------- | ----------- | ----------- |
    |Linux |	x86_64 (amd64) | https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh |
    |Linux|	aarch64 (arm64)	| https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-aarch64.sh |
    |Linux|	ppc64le (POWER8/9)	| https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-ppc64le.sh |
    
    Create a downloads directory 
    ```
    mkdir /downloads 
    ```
    Navigate to this foler
    ```
    cd /downloads 
    ```
    Download Mambaforge package using wget
    ```
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
    ```
    Install  Mambaforge
    ```
    bash {Mambaforge_package_name}
    ```
    e.g.
    ```
    bash Mambaforge-Linux-x86_64.sh
    ```
    Restart Terminal in VS code. 


8. Recommended, create a new python environment for your Marisco development. In the Terminal of VS code.
    
    ```
    mamba create -n mariscoDev
    ```
    Now activate your environment 
    ```
    mamba activate mariscoDev
    ```


9. Install a specific Python version in the Terminal of VS code for your environment.
    Check your python version 
    ```
    python --version
    ```
    Install a specific python version. Recommended 3.9.18 as Marisco uses the package H3 which does not have wheels for Python 3.10 and above.
    ```
    mamba install python=3.9.18
    ```
    Check your python path
    ```
    which python
    ```
    The path returned from which python should return Mambaforge Pyhton (e.g. /home/marisco/mambaforge/bin/python)
    

10. Install Marisco
    
    Navigate to downloads 
    ```
    cd /home/marisco/downloads
    ```
    Download Marisco using git
    ```
    git  https://github.com/franckalbinet/marisco.git
    
    ```
    Install Pip
    ```
    mamba install pip
    ```
   
    Navigate to the Marisco package 
    ```
    cd /home/marisco/downloads/marisco
    ```
    Install Marisco with pip.
    ```
    pip install -e '.[dev]'
    ```

11. Initialize marisco.
    The maris_init command will create a `.marisco/` directory containing various configuration/configurable files in your      python home directory.
     ```
    maris_init
    ```
    Navigate to your home directory and use ls --all to view all files. 
    ```
    ls --all
    ```
12. Install ipykernel for Jupyter compatibility.
    ```
    mamba install ipykernel
    ```
15. Test Jupyter.
    
    In VS code go to extensions (Shortcut Ctrl+Shift+X), search Jupyter and install.
    
    
    Once installed select explorer.
    <p align="center">
      <img src="https://github.com/niallmurphy93/marisco/assets/43383736/b4a5c00f-63a1-44df-9dfe-a85bf8c731c3">
    </p>
    Navigate to a notebook (e.g. /home/marisco/downloads/marisco/nbs/handlers/helcom.ipynb). Open the notebooks. Ensure the      correct kernel is used for Jupyter. 
    <p align="center">
        <img src="https://github.com/niallmurphy93/marisco/assets/43383736/a9cf3c48-a864-4a94-80c9-8871f69b01c4">
    </p>
Other Apps
1. Install netcdf via VS code Terminal
    ```
    sudo apt install netcdf-bin
    ```
2. In VS code install the extension 'vscode-pydata-viewer' to view *.pkl data in VS code. 
