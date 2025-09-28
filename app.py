# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from flask_cors import CORS
from datetime import datetime, timezone

import requests
import dao
import utils
import pymongo
# import re
import pprint
from bson import ObjectId
import time


app = Flask(__name__)
CORS(app)

# rasa_server = f""

# __DPDC_URL_ = "https://api.dpdc.org.bd/dpdcapp/api/bot/"
__RASA_BASE_URL = "http://localhost:5005/webhooks/rest/webhook"
__RASA_BASE_CONV_URL = "http://localhost:5005/conversations/{ctx}/predict"

client = pymongo.MongoClient("mongodb://192.168.14.136:27017")
db = client["chatbot"]
bn_to_en_num_map = {'০': '0','১': '1','২': '2','৩': '3','৪': '4','৫': '5','৬': '6','৭': '7','৮': '8','৯': '9'}
last_intent = None

def init():
    ctxId = dao.initiate_content(True, None, None, None)
    intro = utils.introduction()
    intro["status"] = 200
    intro["ctx"] = str(ctxId)
    # ctx = str(ctxId)
    return intro

def convert_en_to_bn_chars(user_input):
    # print(user_input.split())
    new_user_input = ""
    for token in user_input.split():
        for char in token:
            en_char = char
            if char in bn_to_en_num_map:
                en_char = bn_to_en_num_map[char]
            new_user_input += en_char
        new_user_input += " " 
    return new_user_input.strip()

def get_response(intent, doc, special_number):
    
    return {
        "intent": intent,
        "pendingIntent": None,
        "responseBangla": doc['bn'].format(no=special_number) if special_number else doc['bn'],
        "responseEnglish": doc['en'].format(no=special_number) if special_number else doc['en'],
        "suggestions": doc['suggestions'] if 'suggestions' in doc and len(doc['suggestions']) > 0 else []                        
    }


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
    history = dao.load_history(request.json.get('ctx'))
    # print("Loading history", request.json)
    # pprint.pp(history)
    if history is None:
        abort(400)
    else:
        history.insert(0, utils.introduction())
        if len(history) > 1:
            history.append(utils.welcome_back())
    return history

@app.route("/init", methods=['POST'])
def initialize_chatbot():
    ctxId = dao.initiate_content(True, None, None, None)
    intro = utils.introduction()
    intro["status"] = 200
    intro["ctx"] = str(ctxId)
    return intro

@app.route("/chat", methods=['POST'])
def chat():
    start_time = time.time()
    intent = None
    responses = []
    
    # print("Got this request:")
    # pprint.pp(request.json)

    ctx = request.json.get("ctx")
    raw_user_input = request.json.get("input")
    user_input = convert_en_to_bn_chars(raw_user_input)
    # print(f"Raw user input: {raw_user_input}, input after preprocessing: {user_input}")

    payload = {
        "sender": ctx,
        "message": user_input
    }
    
    bot_response = requests.post(__RASA_BASE_URL, json=payload).json()
    conv_response = requests.post(__RASA_BASE_CONV_URL.format(ctx=ctx), json=payload).json()

    print("-----------BOT RESPONSE-----------")
    pprint.pp(bot_response)
    print("-----------BOT RESPONSE-----------")
    print()
    # print("__________________CONVERSATION RESPONSE_________________")
    # pprint.pp(conv_response['tracker']['events'])
    # print("__________________CONVERSATION RESPONSE_________________\n")
    
    if len(bot_response) == 0:
        # print("Sending empty response")
        responses.append(   
            {
                "intent": "nlu_fallback",
                "pendingIntent": None,
                "responseBangla": "I am sorry, I dont understand.",
                "responseEnglish": "দুঃখিত, আমি আপনার তথ্য বুঝতে পারিনি.",
                "suggestions": []
            }
        )
    else: 
        for data in conv_response['tracker']['events']:
            if data['event'] == 'user':
                intent = data['parse_data']['intent']['name']
        
        # If the intent is None, then it means the conversation was restarted
        # check the database for the last user intent
        if intent == None:
            intent = last_intent
            # chat_history = db.chat_logs.find_one({"_id": ObjectId(ctx)}).get('messages')
            # intent = None
            # for data in chat_history:
            #     if 'intent' in data:
            #         intent = data['intent']
        
        # pprint.pp(conv_response)
        print("Got this intent:", intent)

        # Prepare the bot message
        for response in bot_response:
            if 'custom' in response:
                custom_msg = response['custom']
                doc = db.bot_responses.find_one({"en": custom_msg['text'].strip()})
                if 'complaint_number' in custom_msg:
                    responses.append(get_response(intent, doc, custom_msg['complaint_number']))
                    # save the complaint issue into the db
                elif 'tracking_number' in custom_msg:
                    responses.append(get_response(intent, doc, custom_msg['tracking_number']))
                elif 'customer_number' in custom_msg:
                    # only 1 message should be returned
                    responses.append(get_response(intent, doc, custom_msg['customer_number']))
                    break
                elif 'phone_number' in custom_msg:
                    # only 1 message should be returned
                    responses.append(get_response(intent, doc, custom_msg['phone_number']))
                    break
                elif 'init' in custom_msg:
                    doc = db.bot_responses.find_one({'en': "Select from the options below or type"})
                    responses.append(get_response(intent, doc, None))
                else:
                    # only 1 message should be returned
                    responses.append(get_response(intent, doc, None))
                    break
            else:
                doc = db.bot_responses.find_one({"en": response["text"].strip()})
                responses.append(get_response(intent, doc, None))

    # print("Sending this response")
    # print(responses)
    end_time = time.time()

    # store the conversation history into the DB
    db_ctx = db.chat_logs.find_one({"_id": ObjectId(ctx)})
    # print(db_ctx)
    # pprint.pp(responses)
    if db_ctx:
        user_message = {
            "source": "user",
            "type": "text",
            "message": raw_user_input,
            "lang": "en",
            "intent": responses[0]["intent"]
        }
        bot_message = {
            "source": "bot",
            "type": "text",
            "responseBangla": responses[0]["responseBangla"],
            "responseEnglish": responses[0]["responseEnglish"],
            "lang": "en",
            "intent": responses[0]["intent"],
            "pendingIntent": "",
            "executionTime": end_time - start_time
        }

        db.chat_logs.update_one(
            {'_id': ObjectId(ctx)},
            {'$push': {'messages': {'$each': [user_message, bot_message]}}}
        )
    
    # save nlu or oos messages from user
    # print("Last intent:", responses[0]["intent"])
    if responses[0]["intent"] == "nlu_fallback":
        db.pending_training_data.insert_one({
            "prompt": raw_user_input,
            "intent": responses[0]["intent"]
        })

    return responses

if __name__ == '__main__':
    # Code to run when the app starts
    app.run(host="0.0.0.0", port=5000, debug=True)