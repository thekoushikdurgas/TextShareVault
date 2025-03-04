# netlify/functions/handler.py
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
netlify_app = DispatcherMiddleware(app)