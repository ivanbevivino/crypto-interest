from flask import Blueprint, jsonify,request
from ..models.interest import Interest
app = Blueprint("interests", __name__)



@app.route('/interests',methods=['GET'])
def get_user():
    query_params = request.args.to_dict()
    interests = Interest.list_by(query_params)
    return jsonify([r.serialize() for r in interests])


@app.route("/interests", methods=["POST"])
def create():
    interest = Interest.create(**request.json)
    return jsonify(interest.serialize())
