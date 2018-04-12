from datetime import date
from collections import defaultdict

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

def _collect_data(langs):
  def integrate(commits):
    total = 0
    for date, commits in commits:
      total += commits
      yield date, total

  def data_for_lang(lang):
    return list()

  num_langs = len(langs)
  result = defaultdict(lambda: [0] * num_langs)
  for i, lang in enumerate(langs):
    for date, commits in integrate(data.commits_by_language(lang)):
      result[date][i] = commits

  commits = [[k, *v] for k, v in result.items()]
  commits.sort(key=lambda x: x[0])
  return {'langs': langs, 'commits': commits}

@app.route('/')
def index():
  langs = ['scala', 'python']
  return render_template(
    'index.html',
    data=dumps(_collect_data(langs)))
