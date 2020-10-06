from flask import Blueprint, jsonify,request,current_app
import requests, time
from ..models.interest import Interest
from ..helpers.email_helper import EmailHelper
app = Blueprint("interests", __name__)



@app.route('/interests',methods=['GET'])
def interests():
    response= requests.get("https://criptoya.com/api/aave/dai").json()
    for _ in range(288):
        response = requests.get("https://criptoya.com/api/aave/dai").json()
        current_app.logger.info( "https://criptoya.com/api/aave/dai , {} , {} ".format(response["value"],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response["time"]))))
        Interest.create(plataform="aave",interest =response["value"], date="{}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response["time"]))))
        if response["value"] > 15:
            current_app.logger.info("alert")
            EmailHelper.send(""" Interest aave is in alerts current value: {}""".format(response["value"]))
        time.sleep(600)
    return jsonify(response)


@app.route("/interests", methods=["POST"])
def create():
    interest = Interest.create(**request.json)
    return jsonify(interest.serialize())
