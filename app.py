from flask import Flask, request, abort
from flask_cors import CORS
import pymongo
# import dao
# import utils
import time
import pprint
from bson import ObjectId
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient("mongodb://192.168.14.136:27017")
db = client["chatbot"]

@app.route('/store_info', methods=['POST'])
def store_info():
    print("This is the last intent:", request.json)
    global last_intent
    last_intent = request.json['last_intent']
    return {"status": "success", "last_intent_stored": last_intent}, 200

@app.route('/store_complaint', methods=['POST'])
def store_complaint():
    complaint_data = request.json
    db.complaints.insert_one({
        "sourceId": complaint_data['_id'],
        "customerNumber": complaint_data['customerNumber'],
        "phoneNumber": complaint_data['phoneNumber'],
        "complaintType": complaint_data['complaintType'],
        "trackingNumber": complaint_data['trackingNumber'],
        "createdAt": datetime.now(timezone.utc)
    })

    return {"status": "success", "complaint": complaint_data}, 200

@app.route('/history', methods=['POST'])
def load_history():
    history = 'active'
    ctx = request.json['ctx']
    if ctx is None:
        ctx = request.json['ctxId']
    else:
        ctx = request.json['ctx']
    print("ctxId:", ctx)
    return history

@app.route("/init", methods=['POST'])
def initialize_chatbot():
    # ctxId = dao.initiate_content(True, None, None, None)
    # intro = utils.introduction()
    # intro["status"] = 200
    # intro["ctx"] = str(ctxId)
    intro = {
        "status": 200,
        "ctx": None,
        "message": "Welcome to the chatbot! How can I assist you today?"
    }
    return intro

@app.route("/chat", methods=['POST'])
def chat():
    start_time = time.time()
    intent = None
    responses = []
    
    # print("Got this request:")
    # pprint.pp(request.json)


    print("-----------BOT RESPONSE-----------")
    pprint.pp(start_time)
    print("-----------BOT RESPONSE-----------")
    print()
    # print("__________________CONVERSATION RESPONSE_________________")
    # pprint.pp(conv_response['tracker']['events'])
    # print("__________________CONVERSATION RESPONSE_________________\n")


        # Prepare the bot message

    # print("Sending this response")
    # print(responses)
    end_time = time.time()

    # store the conversation history into the DB
    db_ctx = db.chat_logs.find_one({"_id": ObjectId()})
    print(db_ctx)
    pprint.pp(responses)

    return responses

@app.route("/test", methods=['GET'])
def test():
    # Test endpoint to check if the server is running
    return {"status": "success", "message": "Server is running!"}, 200
@app.route("/test/<string:arg>", methods=['GET'])
def test_with_arg(arg):
    # Test endpoint to check if the server is running with an argument
    return {"status": "success", "message": f"Server is running with argument: {arg}"}, 200
if __name__ == '__main__':
    # Code to run when the app starts
    app.run(host="0.0.0.0", port=5000, debug=True)