<br />
<p align="center">
    <img src="media/logo.png" alt="Logo" width="80" height="80">
  </p>
  <h1 align="center">Football players management application</h1>
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#Requirements">Requirements</a>
    </li>
    <li>
        <a href = "#Getting-start">Getting-start</a>
    </li>
    <li>
        <a href="#contact">Contact</a>
    </li>
  </ol>
</details>

# Requirements

1) [Python 3.8](https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe "Python 3.8 download page")

2) [Doxygen 1.9](https://www.doxygen.nl/index.html "Doxygen home")

3) [Pycharm( recomended )](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows "Pycharm download page")

# Getting-start

**_This is the instruction you need to build and use the project._**

1. ### Clone the repo

```sh
  git clone https://gitlab.scase.local/ali.ibrahim.2/football_club.git
  cd football_club
```

2. ### Run install_dependencies.bat in order to create and install all the requried environment application needed in the projct or use cmd in the project directory and write these instructions

```shell
   python -m venv venv
  venv\Scripts\activate.bat && python -m pip install -r requirements.txt && python manage.py migrate && python manage.py seed --mode=refresh
```

    these instructions are decrpiped as follow:
        1) venv\Scripts\activate.bat: used to activate environment
        2) python -m pip install -r requirements.txt: used to install all the required apps from requirement.txt file
        3) python manage.py migrate to migrate all models to the databse.
        4) manage.py seed --mode=refresh it is a command that we use to refresh the database and clear all the previous data.

3. ### Run runserver.bat to Run the application or use cmd in the project directory and write this line

```shell
   venv\Scripts\activate.bat && python manage.py runserver
```

4. ### Run make_docs.bat to generate html documentation file or open cmd in the project directory and write

```shell
    mkdir docs
    cd docs
    mkdir player
    mkdir app
    cd ..
    doxygen config_player_doxy
    doxygen config_app_doxy
```

# Contact

Ali ibrahim - ali.ibrahim.2@lit-co.net Project
Link: [https://gitlab.scase.local/ali.ibrahim.2/football_club.git](https://gitlab.scase.local/ali.ibrahim.2/football_club.git)

&copy;