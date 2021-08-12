python -m venv venv
venv\Scripts\activate.bat && python -m pip install -r requirements.txt && python manage.py migrate && python manage.py seed --mode=refresh