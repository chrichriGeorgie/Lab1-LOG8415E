
from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def hello():
    app.config.from_prefixed_env()
    machine_id = app.config['MACHINEID']
    return f'<h1>Hello, World! FROM: {machine_id}</h1>'
