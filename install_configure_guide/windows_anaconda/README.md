The Marisco package is developed within Jupyter Notebooks using  [nbdev](https://nbdev.fast.ai/). The Jupyter Notebooks used for development are located at `marisco/nbs`. The `Marisco` package, which is created using the notebooks, is located at `marisco/marisco`.

#### Windows

##### Prerequisites
`Marisco` with Anaconda Navigator 

1. Create a new python environment for your `Marisco` development (*Recommended*):
    - In Anaconda Navigator, select `Environments`; 
    - In Environments, Select `Create`;
    - Name your environment, e.g. `mariscoDev` (*Take note of the location*);
    - Select a Python version (3.10 and above) ~(recommended 3.9.18 as `Marisco` uses the package H3 which does not have wheels for Python 3.10 and above)~.

2.  In Anaconda Navigator, go to `Home`. Select your environment (e.g. `mariscoDev`). Select install `CMD.exe` Prompt; 
 
3. In Anaconda Navigator, launch `CMD.exe` Prompt. A command prompt will open. Make sure your environment name appears in brackets (e.g. `mariscoDev`);

4. To install `marisco`:

```
pip install marisco
```

**OR**

If you would like install `Marisco` as an editable version then download the `Marisco` package from [GitHub](https://github.com/franckalbinet/marisco). [Link Marisco package download](https://github.com/franckalbinet/marisco/archive/refs/heads/main.zip):

1. Unzip the package;
2. In `CMD.exe` Prompt change to the package location;
3. `cd` (*change directory*) in the donwloaded package:

```
cd  path_to_downloaded_package
```

4. Then install the package:
```
pip install -e .
```

5. And initialize `marisco`:

The `maris_init` command will create a `.marisco/` directory containing various configuration/configurable files in your python home directory:

 ```
maris_init
```

6. In Anaconda, install Jupyter Notebook and launch. 