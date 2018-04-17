# Language Trends
A simple python web application that watches on language dynamics on GitHub. You can see it
in action [here](http://oleg-knyazev.com/language-trends/).

## Prerequisites

* Python 3.6
* PostgreSQL

## Installation

1. Install requirements:

      ```bash
      cd <checkout-directory>
      python -m venv .
      ./bin/python -m pip install -r requirements.txt
      ```

   On Windows you probably should use `./Scripts/python.exe` instead of `./bin/python`.

2. Create a database

3. Edit `CONNECTION_PARAMS` in the file `language_trends/data/access.py` to make it
   point on a newly created database.

4. Put your GitHub API access token in file `auth_token.txt`. See
   [instructions](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/)
   on how to generate a token. No special grants are required (the app uses only publicly
   available information), so, you can leave all the checkboxes on the token generation
   page unchecked.

## Running

### Running a scan process

  ```bash
  ./bin/python -m language_trends.scan [<languages>]
  ```

  `<langugages>` is an optional space-separated list of languages, e.g. `clojure python`.
If it isn't specified, all known languages will be scanned in order. The list of known
languages is stored in variable `ALL_LANGUAGES` in module `language_trends.languages`.

  Be aware that full scan may take many hours or even days. It's mainly caused by GitHub's
[rate limits](https://developer.github.com/v4/guides/resource-limitations/)—most of the time
the scanner is just waiting for a new quota.

### Hosting a WSGI application

  WSGI application variable is called `app` and it resides in module `language_trends.ui`.
To serve it, follow instructions of your server. Anyway, the application *isn't ready for
production use* currently, so, be careful!

### Additional developer tasks

#### Running a development web-server

  ```bash
  export FLASK_APP=language_trends.ui
  ./bin/flask run
  ```

  For enchanced debugging and automatic reload you can also perform `export FLASK_DEBUG=1`.

#### Database migrations

 * Migrate to the latest version:

     ```bash
     ./bin/python -m language_trends.data migrate
     ```

  * Rollback the last migration:

     ```bash
     ./bin/python -m language_trends.data rollback
     ```

  * **(CAUTION!)** Rollback to an *empty* database:

     ```bash
     ./bin/python -m language_trends.data rollback all
     ```

  Migrations are performed automatically when running scanning process or web server, so, you
  don't have to do it manually.

#### Language statistics

  ```bash
  ./bin/python -m language_trends.stat
  ```
