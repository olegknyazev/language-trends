# Language Trends
A simple python web application that analyzes languages usage on GitHub. See it
in action [here](http://oleg-knyazev.com/language-trends/).

Essentially, it's a training project that I was developing while trying to get
familiar with web- and asynchronous programming in Python. The main challenge here
was finding an effective approach to GitHub scanning via an API having a very limited
throughput.

Some difficulties I've encountered and worked around were:

  * It's not possible to list all the repositories on GitHub using its
    [V4 API (GraphQL)](https://developer.github.com/v4). A search result is limited
    to 1000 items. So I've split search to many sub-searches based on repository
    creation time.

  * Depending on actual data (and on something else, probably), API requests may fail. Some
    of the requests are failing all the time—my guess is that they don't fit into internal
    GitHub's timeouts. There is no way to predict which request will succeed and which
    will fail (it actually may depend on, say, the total commit count in the repository
    history). The solution I've used is to retrieve data in small portions and decrease
    a portion size in case of error.

## Project structure

If you want to dig into the code a little bit, here is a short overview of the project's
structure. The root package contains several modules and sub-packages encapsulating
particular areas of responsibility.

* `langauge_trends.github`

  Everything related to working with GitHub API. One of the key points here is a separation
  of query forming methods from actual IO.

* `lanaguge_trends.data`

  Data persistence. The data model is pretty simple, therefore plain SQL queries are used.
  I implemented a simple migrations mechanism because I didn't like the complexity of
  existing solutions (use of a separate config, for example).

* `language_trends.scan`

  The core of the application—the scanning process. Glues `github` and `data` modules
  together.

* `language_trends.ui`

  A very simple Flask application that, in essence, serves an almost static page. Data
  for the chart is embedded into a page in a JavaScript variable. JavaScript and HTML in
  this project are bad, I know :-)

## Playing around

### Prerequisites

* Python 3.6
* PostgreSQL
* GitHub account :-)

### Installation

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

### Running

#### Running a scan process

  ```bash
  ./bin/python -m language_trends.scan [<languages>]
  ```

  `<langugages>` is an optional space-separated list of languages, e.g. `clojure python`.
If it isn't specified, all known languages will be scanned in order. The list of known
languages is stored in variable `ALL_LANGUAGES` in module `language_trends.languages`.

  Be aware that full scan may take many hours or even days. It's mainly caused by GitHub's
[rate limits](https://developer.github.com/v4/guides/resource-limitations/)—most of the time
the scanner is just waiting for a new quota.

#### Running a development web-server

  ```bash
  export FLASK_APP=language_trends.ui
  ./bin/flask run
  ```

  For enchanced debugging and automatic reload you can also perform `export FLASK_DEBUG=1`.

### Additional development tasks

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
