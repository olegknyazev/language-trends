from datetime import date
from flask import Flask, jsonify, request, render_template
from flask.json import JSONEncoder
from .. import data

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, date):
        return obj.isoformat()
    return super().default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api/commits')
def commits():
  commits = data.commits_by_language(request.args['language'])
  return jsonify(commits)
