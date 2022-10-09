# LOG8415E - Assignment 1
# app.py
# Python file of the Flask app routing of both clusters

from flask import Flask
import os

app = Flask(__name__)

# Default route
@app.route('/')
def base():
    return f'<h1>Hi! Please go to cluster 1 or cluster 2.</h1>'

# Cluster 1 route
@app.route('/cluster1')
def cluster_one():
    app.config.from_prefixed_env()
    machine_id = app.config['MACHINEID']
    return f'<h1>Welcome to cluster 1! From {machine_id}</h1>'

# Cluster 2 route
@app.route('/cluster2')
def cluster_two():
    app.config.from_prefixed_env()
    machine_id = app.config['MACHINEID']
    return f"<h1>Here is cluster 2! You're talking to {machine_id}</h1>"
