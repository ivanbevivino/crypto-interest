from flask import Blueprint, current_app


app = Blueprint("ping", __name__)


@app.route("/ping")
def ping():
    return "pong"

@app.route('/name',methods=['GET'])
def NewUser():
    return "200"
