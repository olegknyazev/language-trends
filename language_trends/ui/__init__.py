from datetime import date

from flask import Flask, render_template
from flask.json import JSONEncoder, dumps

from language_trends import data

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, date):
        return obj.isoformat()
    return super().default(obj)

app = Flask(__name__, static_url_path='')
app.json_encoder = CustomJSONEncoder

def integrate(commits):
  total = 0
  for date, commits in commits:
    total += commits
    yield date, total

@app.route('/')
def index():
  return render_template(
    'index.html',
    data=dumps(list(integrate(data.commits_by_language('clojure')))))
