marisco windows and anaconda
================

The Marisco package is developed within Jupyter Notebooks using  [nbdev](https://nbdev.fast.ai/). The Jupyter Notebooks used for development are located at marisco/nbs/. The Marisco package, which is created using the notebooks, is located at marisco/marisco/.

## Prerequisites ( Windows )
Marisco with Anaconda Navigator 

1. Recommended, create a new python environment for your Marisco development.
    - In Anaconda Navigator, select 'Environments'. 
    - In Environments, Select 'Create'. 
    - Name your environment (e.g.mariscoDev ). Take note of the location. 
    - Select a Python version (recommended 3.9.18 as Marisco uses the package H3 which does not have wheels for Python 3.10 and above).  

2.  In Anaconda Navigator, go to 'Home'. Select your environment (e.g.mariscoDev ). Select install CMD.exe Prompt. 
 

3. In Anaconda Navigator, launch CMD.exe Prompt. A command prompt will open. Make sure your environment name appears in brackets (e.g. '(mariscoDev)').

4. To install marisco 
```
pip install marisco
```

OR

If you would like install marisco as an editable version then download the Marisco package from github. [Link Marisco package downlaod](https://github.com/franckalbinet/marisco/archive/refs/heads/main.zip). Unzip the package. In CMD.exe Prompt change to the package location.
```
cd  path_to_downloaded_package
```
The install the package.
```
pip install -e .
```

5. Init marisco
The maris_init command will create a `.marisco/` directory containing various configuration/configurable files in your python home directory 
 ```
maris_init
```

In Anconda, install Jupyter Notebook and launch. 

