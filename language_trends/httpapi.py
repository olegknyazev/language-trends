from datetime import date
from flask import Flask, jsonify, request, send_file
from flask.json import JSONEncoder
from . import data

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, date):
        return obj.isoformat()
    return super().default(self, obj)

app = Flask(__name__, static_folder='resources', static_url_path='')
app.json_encoder = CustomJSONEncoder

@app.route('/')
def index():
  return send_file('resources/index.html')

@app.route('/api/commits')
def commits():
  commits = data.commits_by_language(request.args['language'])
  return jsonify(commits)
