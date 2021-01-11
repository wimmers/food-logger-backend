## Installation

Create a new virtual environment and load it:
```
python3 -m venv ~/.virtualenvs/fl
source ~/.virtualenvs/fl/bin/activate
```

Install Django and required libraries with `pip`:
```
pip install -r requirements.txt
```

Run migrations:
```
python manage.py migrate
```

Run the server:
```
python manage.py runserver
```