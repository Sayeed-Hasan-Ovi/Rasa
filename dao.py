import pymongo
from datetime import datetime
from bson import ObjectId

client = pymongo.MongoClient("mongodb://192.168.14.136:27017")
db = client["chatbot"]


def initiate_content(is_registered, account_number, otp, context):
    if context == None:
        # ctx = db.chat_logs.insert_one({
        #     "accountNumber": account_number,
        #     "otp": otp,
        #     "language": 'bn',
        #     "registered": is_registered,
        #     "messages": []
        # })
        
        # # Insert a new conversation data with the ctx
        # db.conversation.insert_one({
        #     "ctx": ctx.inserted_id,
        #     "flow_data": {},
        #     "messages":[],
        #     "start_time": datetime.now().strftime("%B %d, %Y, %I:%M %p"),
        #     "end_time": None,
        #     "is_active": True
        # })

        ctx = db.chat_logs.insert_one({
            "messages": []
        })

        return ctx.inserted_id
    else:
        db.chat_logs.update_one({"_id": ObjectId(context)}, {"$set":
            {
                "accountNumber": account_number,
                "otp": otp,
                "language": 'bn',
                "registered": is_registered,
                "messages": []
            }})
    return context

def record_training_data(user_input, intent):
    db.pending_training_data.insert_one({
        "prompt": user_input,
        "intent": intent
    })

def is_verified(context):
    document = db.chat_logs.find_one({
        "_id": ObjectId(context),
        "verfied": True
    })
    return document

def save_training_data(prompt, intent, lang):
    db.prompts.insert_one({
        "prompt": prompt,
        "intent": intent,
        "language": lang
    })

def save_temp_phone_number(context, temp_phone):
    db.chat_logs.update_one({"_id": ObjectId(context)}, {"$set": {"temp_phone": temp_phone}})

def save_temp_address(context, input):
    db.chat_logs.update_one({"_id": ObjectId(context)}, {"$set": {"temp_address": input}})

def find_temp_data(context):
    temp_data = db.chat_logs.find_one({"_id": ObjectId(context)}, {"temp_phone": 1, "temp_address": 1})
    temp_phone = temp_data.get("temp_phone", None)
    temp_address = temp_data.get("temp_address", None)
    return temp_phone, temp_address

def verify_otp(context, otp, lang):
    document = db.chat_logs.find_one({
        "_id": ObjectId(context),
        "otp": otp
    })
    if document != None:
        db.chat_logs.update_one({"_id": ObjectId(context)}, {"$set": {"language": lang, "verfied": True}})
        return True
    return False


def record_history(id, user_input, bangla_response, english_response, lang, intent, pending_intent, execution_time):
    db.logs.insert_one({"userInput": user_input, "intent": intent,  "executionTime": execution_time })
    new_messages = [
        {"source": "user", "type": "text", "message": user_input, "lang": lang, "intent": intent},
        {
            "source": "bot",
            "type": "text",
            "responseBangla": bangla_response,
            "responseEnglish": english_response,
            "lang": lang,
            "intent": intent,
            "pendingIntent": pending_intent,
            "executionTime": execution_time
        }
    ]
    db.chat_logs.update_one({"_id": ObjectId(id)}, {"$push": {"messages": {"$each": new_messages}}})


def load_history(id):
    document = db.chat_logs.find_one({"_id": ObjectId(id)})
    return None if document == None else document["messages"]


def find_customer_number(context_id):
    document = db.chat_logs.find_one({"_id": ObjectId(context_id)})
    return document["customerNumber"] if "customerNumber" in document else None


def save_customer_number(context_id, customer_number):
    db.chat_logs.update_one({"_id": ObjectId(context_id)}, {"$set": {"customerNumber": customer_number}})


def find_phone_number(context_id):
    document = db.chat_logs.find_one({"_id": ObjectId(context_id)})
    return document["phoneNumber"] if "phoneNumber" in document else None


def save_phone_number(context_id, phone_number):
    db.chat_logs.update_one({"_id": ObjectId(context_id)}, {"$set": {"phoneNumber": phone_number}})


def find_customer_number_and_phone_number(context_id):
    document = db.chat_logs.find_one({"_id": ObjectId(context_id)})
    return (document["customerNumber"] if "customerNumber" in document else None,
            document["phoneNumber"] if "phoneNumber" in document else None)


def get_repeat_counter(context_id):
    document = db.chat_logs.find_one({"_id": ObjectId(context_id)})
    return 0 if (document is None or "repeatCounter" not in document
                 or document["repeatCounter"] is None) else document["repeatCounter"]


def set_repeat_counter(context_id, counter):
    db.chat_logs.update_one({"_id": ObjectId(context_id)}, {"$set": {"repeatCounter": counter}})


def record_complaint(context, customer_number, phone_number, complaint_type, tracking_number):
    current_time = datetime.now()
    db.complaints.insert_one({
        "sourceId": context,
        "customerNumber": customer_number,
        "phoneNumber": phone_number,
        "complaintType": complaint_type,
        "trackingNumber": tracking_number,
        "createdAt": current_time
    })

def find_last_complaint_today(context, complaint_type):
    # Define the start and end of today
    today_start = datetime.combine(datetime.now(), datetime.min.time())
    today_end = datetime.combine(datetime.now(), datetime.max.time())

    # Query to fetch the last inserted complaint for today
    query = {
        "sourceId": context,
        "complaintType": complaint_type,
        "createdAt": {"$gte": today_start, "$lt": today_end}
    }

    # Sort the complaints by createdAt field in descending order and limit the result to one document
    sort_order = [("createdAt", -1)]
    last_complaint = db.complaints.find_one(query, sort=sort_order)

    # Process the fetched complaint as needed
    if last_complaint:
        return last_complaint["trackingNumber"]
    else:
        return None