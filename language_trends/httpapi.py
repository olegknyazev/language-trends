from datetime import date
from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from . import data

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, date):
        return obj.isoformat()
    return super().default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

@app.route('/api/commits')
def hello_world():
  commits = data.commits_by_language(request.args['language'])
  return jsonify(commits)
