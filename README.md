# Image Deduplication Storage

System to storage images with hash-based deduplication. 
It is helpful for 3d rendering testing or for another cases to store images with a log of duplicated images.

## How to run development environment

1. Install `python 3.10`
2. Install `poetry`

```shell
# Windows
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -

# *NIX
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

More info at https://python-poetry.org/docs/

If you got error with python version try to add to `PYTHONPATH` python root dir (for
example `C:\Program Files\Python39`)

3. Check installation `poetry --version`
4. Run in project root dir `poetry shell`
5. In opened shell install dependencies with `poetry install`
6. Create file `.env` in project root and copy data from file `.env.example`
7. In that file configure postgres credentials and database names
8. Run alembic migrations with command `poetry run alembic upgrade head`
10. Run `uvicorn app.main:app --reload`. As default it starts at `http://localhost:8000`
11. To access docs go to `http://localhost:8000/docs`

### Start command

```shell
uvicorn app.main:app --reload
```

### Add dependency

```shell
poetry add <dep>
```

### Requirements export

```shell
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

### Create init migrations

```shell
poetry run alembic init migrations
```

### Create migrations revision

```shell
poetry run alembic revision --autogenerate -m "<message>"
```

### Upgrade to the latest migration revision

```shell
poetry run alembic upgrade head
```

### Sort imports

```shell
poetry run isort app
```

### Run flake8 linter

```shell
poetry run flake8 app
```

### Recommendations before pull request

Run that commands and inspect errors shown from linter

```shell
poetry run isort app
poetry run flake8 app
```
