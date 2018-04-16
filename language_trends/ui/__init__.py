from datetime import date
from collections import defaultdict

from flask import Flask, render_template
from flask.json import JSONEncoder, dumps

from language_trends import data
from language_trends.languages import ALL_LANGUAGES

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

  def remove_indices(lst, indices):
    return [x for i, x in enumerate(lst) if i not in indices]

  num_langs = len(langs)
  result = defaultdict(lambda: [0] * num_langs)
  for i, lang in enumerate(langs):
    for date, commits in integrate(data.commits_by_language(lang)):
      result[date][i] = commits

  empty_languages = {i for i in range(num_langs) if all(c[i] == 0 for c in result.values())}
  langs = remove_indices(langs, empty_languages)
  result = {k: remove_indices(v, empty_languages) for k, v in result.items()}

  commits = [[k, *v] for k, v in result.items()]
  commits.sort(key=lambda x: x[0])
  return {'langs': langs, 'commits': commits}

@app.route('/')
def index():
  return render_template(
    'index.html',
    data=dumps(_collect_data(ALL_LANGUAGES)))
