# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
 
from typing import Any, Coroutine, Text, Dict, List
import re
 
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, ActiveLoop, FollowupAction, Restarted, UserUtteranceReverted

# import pymongo
# import pprint
# from bson import ObjectId
import dpdc_api
import requests

# client = pymongo.MongoClient("mongodb://localhost:27017")
# db = client['chatbot']

__FLASK_BASE_URL = "https://animated-winner-x4xw47x9wwqc9qqw-5000.app.github.dev/"

############################################### GLOBAL FUNCTIONS #############################################
def save_last_intent(sender_id, last_intent):
    payload = {
        "_id": sender_id,
        "last_intent": last_intent
    }
    save_info = requests.post(__FLASK_BASE_URL+"/store_info", json=payload)

def save_complaint(sender_id, customer_number, phone_number, tracking_number):
    payload = {
        "_id": sender_id,
        "customerNumber": customer_number,
        "phoneNumber": phone_number,
        "complaintType": "52",
        "trackingNumber": tracking_number,
    }
    complaint_save_info = requests.post(__FLASK_BASE_URL+"/store_complaint", json=payload)

def get_complaint_number(sender_id, customer_number, phone_number, customer_address, electricity_office):
    print("Getting complaint number...")
    
    dpdc_response = None
    if customer_number is None:
        dpdc_response = dpdc_api.register_complaint_new(phone_number, customer_address, electricity_office, "52")
    else:
        dpdc_response = dpdc_api.register_complaint(phone_number, customer_number, 52)
    
    print(dpdc_response)
    dummy_number = 11223344
    if dpdc_response is not None:
        pattern = r'\d+'
        match = re.search(pattern, dpdc_response['Tracking_Number'])

        # # save the complaint information to the db here:
        # # Get the current time in UTC
        # now = datetime.now(timezone.utc)
        # # # Truncate microseconds to milliseconds
        # # iso_format = now.replace(microsecond=(now.microsecond // 1000) * 1000).isoformat()
        # db.complaints.insert_one({
        #     "sourceId": sender_id,
        #     "customerNumber": customer_number,
        #     "phoneNumber": phone_number,
        #     "complaintType": "52",
        #     "trackingNumber": match.group(0),
        #     "createdAt": now
        # })

        save_complaint(sender_id, customer_number, phone_number, match.group(0))

        return match.group(0)
    else:
        return dummy_number

############################################### VALIDATIONS #############################################
# class ValidateNoElectricityForm(FormValidationAction):

#     def name(self) -> Text:
#         return "validate_no_electricity_form"
    
#     def validate_customer_number(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict
#     ) -> Dict[Text, Any]:
        
#         print("\nVALIDATION: no_electricity_form")
#         print("Validating customer number")

#         if tracker.get_slot('requested_slot') == 'phone_number':
#             print("Excpected phone number but got customer number")
#             # Reset the customer number and call the phone number validation function
#             validation_result = self.validate_phone_number(slot_value, dispatcher, tracker, domain)
#             return {
#                 "customer_number": tracker.get_slot('customer_number'),
#                 "phone_number": None,
#                 **validation_result
#             }

#         # Use dpdc API to check whether customer number is valid
#         dpdc_response = dpdc_api.prepaid_information(slot_value, None)
#         print(dpdc_response)
#         if dpdc_response is not None and dpdc_response["HAS_ERROR"] == 'Y':
#             dispatcher.utter_message(json_message={
#                 "text":"The customer number you've given isn't in our records. Would you like to try again?<br><br>If you've forgotten your customer number, please reach out to our helpline at (16116)."
#             })
#             return {"customer_number": None}
        
#         # print("This is the slot value:", slot_value)
#         return {"customer_number": slot_value}

#     def validate_phone_number(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict
#     ) -> Dict[Text, Any]:
        
#         print("\nVALIDATION: no_electricity_form")
#         print("Validating phone number")
#         # print(tracker.get_latest_entity_values("phone_number"))

#         # Trying to validate phone number but got customer number as the slot
#         print("Requested slot:", tracker.get_slot('requested_slot'))
#         if tracker.get_slot('requested_slot') == 'customer_number':
#             phone_number = tracker.get_slot("phone_number")
#             print(f"Expected customer number but got phone number, current phone number: {phone_number}")
#             print("Last intent:", tracker.latest_message['intent']['name'])
#             validation_result = self.validate_customer_number(slot_value, dispatcher, tracker, domain)
#             if tracker.get_slot("phone_number") is not None:
#                 return {"phone_number": tracker.get_slot("phone_number"), **validation_result}
#             else:
#                 return {"phone_number": None, **validation_result}
        
#         if len(slot_value) != 11 or slot_value.isdigit() == False:
#             dispatcher.utter_message(json_message={"text":"The phone number is invalid. Would you like to try again?"})
#             return {"phone_number": None}
#         else:
#             return {"phone_number": slot_value}

# class ValidateFileComplaintForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_file_complaint_form"
    
#     def validate_phone_number(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict
#     ) -> Dict[Text, Any]:

#         print("\nVALIDATION: validate_file_complaint_form")
#         print(f"Checking phone number: {slot_value}")

#         if len(slot_value) != 11 or slot_value.isdigit() == False:
#             dispatcher.utter_message(json_message={
#                 "text":"The phone number is invalid. Would you like to try again?"
#             })
#             return {"phone_number": None}
        
#         return {"phone_number": slot_value}
        
#     def validate_customer_address(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict
#     ) -> Dict[Text, Any]:
        
#         print("\nVALIDATION: validate_file_complaint_form")
#         print(f"Checking customer address: {slot_value}")

#         return {"customer_address": slot_value}

#     def validate_electricity_office(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict
#     ) -> Dict[Text, Any]:
#         print("\nVALIDATION: validate_file_complaint_form")
#         print(f"Checking electricity_office: {slot_value}")

#         if tracker.get_slot('requested_slot') == "customer_address":
#             print("Expected address but got electricity office")
#             validation_result = self.validate_customer_address(slot_value, dispatcher, tracker, domain)
#             return {
#                 "phone_number": tracker.get_slot("phone_number"),
#                 "customer_address": slot_value,
#                 "electricity_office": None,
#                 **validation_result
#             }

#         return {"electricity_office": slot_value}

# class ValidateBillDueForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_bill_due_form"

#     def validate_bill_number(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict) -> Dict[Text, Any]:
        
#         bill_number = tracker.get_slot('bill_number')
#         print("Validating bill number:", bill_number)
        
#         api_response = dpdc_api.billing_information(bill_number)
#         print("This is the api response:", api_response)
#         if api_response is None or api_response['HAS_ERROR'] == "Y" or len(bill_number) != 9:
#             dispatcher.utter_message(json_message={"text": "No bill found with the provided bill number. Do you want to try with a different bill number?"})
#             return {"bill_number": None}
#         else:
#             dispatcher.utter_message("Your bill has been paid. For detailed information contact our helpline number 16116 or your concern NOCS.")
#             return {"bill_number": bill_number}

# class ValidateTokenIssueForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_token_issue_form"
    
#     def validate_customer_number(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict) -> Dict[Text, Any]:

#         print("\nVALIDATION: validate_token_issue_form")
#         customer_number = tracker.get_slot('customer_number')
#         print("customer number for token issue:", customer_number)

#         # if dpdc_response is not None and dpdc_response["HAS_ERROR"] == 'Y' or len(slot_value) != 8:
#         #     dispatcher.utter_message(json_message={
#         #         "text": "The customer number you've given isn't in our records. Would you like to try again?<br><br>If you've forgotten your customer number, please reach out to our helpline at (16116)."
#         #     })
#         #     return {"customer_number": None}

#         if customer_number is None:
#             return {"customer_number": None}

#         # if len(customer_number) != 8:
#         #     dispatcher.utter_message(json_message={
#         #         "text": "The customer number you've given isn't in our records. Would you like to try again?<br><br>If you've forgotten your customer number, please reach out to our helpline at (16116)."
#         #     })
#         #     return {"customer_number": None}
#         else:
#             dpdc_response = dpdc_api.prepaid_information(slot_value, None)
#             print(dpdc_response)
#             if dpdc_response is not None:
#                 if dpdc_response['HAS_ERROR'] == 'Y':
#                     dispatcher.utter_message(json_message={
#                         "text": "The customer number you've given isn't in our records. Would you like to try again?<br><br>If you've forgotten your customer number, please reach out to our helpline at (16116)."
#                     })

#                     return {"customer_number": None}
#                 else:
#                     dispatcher.utter_message(text=dpdc_response['message'])
#             elif dpdc_response is None:
#                 dispatcher.utter_message(json_message={
#                     "text": "The customer number you've given isn't in our records. Would you like to try again?<br><br>If you've forgotten your customer number, please reach out to our helpline at (16116)."
#                 })
#                 return {"customer_number": None}
#             else:
#                 return {"customer_number": customer_number}

#             return {"customer_number": customer_number}

# class ValidateNewMeterForm(FormValidationAction):
    
#     def name(self) -> Text:
#         return "validate_new_meter_form"
    
#     def validate_tracking_number(
#             self,
#             slot_value: Any,
#             dispatcher:CollectingDispatcher,
#             tracker: Tracker,
#             domain: DomainDict) -> Dict[Text, Any]:
        
#         print("\nVALIDATION: validate_new_meter_form")
#         tracking_number = tracker.get_slot('tracking_number')
#         print("tracking number:", tracking_number)

#         api_response = dpdc_api.online_new_connection_information(tracking_number)
#         print(api_response)
        
#         if api_response['HAS_ERROR'] == "Y" or len(tracking_number) != 10:
#             dispatcher.utter_message(json_message={
#                 'text': "The tracking number provided is incorrect. Please provide the correct tracking number."
#             })
#             return {'tracking_number': None}
#         else:
#             dispatcher.utter_message(json_message={
#                 'text': "For more information visit this url <a href='https://dpdc.org.bd/site/home_gov/online_application_tracking?trac_no={no}'>https://dpdc.org.bd/site/home_gov/online_application_tracking?trac_no={no}</a> or contact our helpline number 16116 or your concern NOCS.",
#                 'tracking_number': tracking_number
#             })
#             return {'tracking_number': tracking_number}
        
############################################### ACTIONS #################################################
class ActionHandleIncorrectIntent(Action):

    def name(self) -> Text:
        return "action_handle_incorrect_intent"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("\nACTION: action_handle_incorrect_intent")
        last_intent = tracker.latest_message['intent']['name']
        last_user_input = tracker.latest_message.get('text')
        active_loop = tracker.active_loop_name
        requested_slot = tracker.get_slot('requested_slot')

        print("Last intent:", last_intent)
        print("Active loop:", active_loop)
        print("Requested slot:", requested_slot)
        print("Last user input:", last_user_input)

        dpdc_response = None
        if requested_slot == "customer_number":
            dpdc_response = dpdc_api.prepaid_information(last_user_input, None)
            print(dpdc_response)
            if dpdc_response and dpdc_response["HAS_ERROR"] == "Y":
                dispatcher.utter_message(json_message={
                    "text":"The customer number you've given isn't in our records. Would you like to try again?<br><br>If you've forgotten your customer number, please reach out to our helpline at (16116)."
                })
                return [SlotSet(requested_slot, None)]
            else:
                # check to see if phone number exists. 
                # This could happen if the user restarts the no elec form says 'no' to re using customer number,
                # enters it but there is an existing phone number
                if tracker.get_slot("phone_number") is not None:
                    # a phone number exists to ask the user if they want to continue with the same phone number
                    dispatcher.utter_message(json_message={
                        "text": "Would you like to continue with this phone number {no}?",
                        "phone_number": tracker.get_slot("phone_number")
                    })
                    return [SlotSet(requested_slot, last_user_input), FollowupAction("utter_retry_phone_number")]
                return [SlotSet(requested_slot, last_user_input)]
            
        elif requested_slot == "phone_number":
            if len(last_user_input) != 11 or last_user_input.isdigit() == False:
                dispatcher.utter_message(json_message={"text":"The phone number is invalid. Would you like to try again?"})
                return [SlotSet(requested_slot, None)]
            else:
                return [SlotSet(requested_slot, last_user_input)]
        elif requested_slot == "customer_address":
            return [SlotSet(requested_slot, last_user_input)]
        elif requested_slot == "bill_number":
            dpdc_response = dpdc_api.billing_information(last_user_input)
            print(dpdc_response)
            if dpdc_response is None or dpdc_response['HAS_ERROR'] == "Y":
                dispatcher.utter_message(json_message={"text": "No bill found with the provided bill number. Do you want to try with a different bill number?"})
                return [SlotSet(requested_slot, None)]

            dispatcher.utter_message(text="Your bill has been paid. For detailed information contact our helpline number 16116 or your concern NOCS.")
            return [SlotSet(requested_slot, last_user_input)]
        elif requested_slot == "tracking_number":
            retry_count = tracker.get_slot("tracking_number_retry") or 0
            dpdc_response = dpdc_api.online_new_connection_information(last_user_input)
            if dpdc_response is None or dpdc_response['HAS_ERROR'] == "Y":
                retry_count += 1
                if retry_count >= 3:
                    dispatcher.utter_message(json_message={
                        'text': 'Tracking number is incorrect. Please contact our helpline number 16116.',
                        'tracking_number': last_user_input
                    })
                    return [SlotSet(requested_slot, None),FollowupAction("action_reset_slots"), SlotSet("tracking_number_retry", 0)]
                    # return [SlotSet("tracking_number_retry", retry_count),FollowupAction("action_loop_completion")]
                else:
                    dispatcher.utter_message(json_message={
                        'text': "The tracking number provided is incorrect. Please provide the correct tracking number."
                    })
                    return [SlotSet(requested_slot, None), SlotSet("tracking_number_retry", retry_count)]

            dispatcher.utter_message(json_message={
                'text': "For more information visit this url <a href='https://dpdc.org.bd/site/home_gov/online_application_tracking?trac_no={no}'>https://dpdc.org.bd/site/home_gov/online_application_tracking?trac_no={no}</a> or contact our helpline number 16116 or your concern NOCS.",
                'tracking_number': last_user_input
            })
            return [SlotSet(requested_slot, last_user_input),SlotSet("tracking_number_retry", 0)]
        # TRY REMOVING THIS
        elif requested_slot == "electricity_office":
            return [SlotSet(requested_slot, last_user_input)]
        else:
            dispatcher.utter_message(response="utter_oos")
        return []

class ActionHandleAffirmDeny(Action):
    
    def name(self) -> Text:
        return "action_handle_affirm_deny"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[str, Any]]]:
    
        print("\nACTION: action_handle_affirm_deny")
        active_loop = tracker.active_loop_name
        last_intent = tracker.latest_message['intent']['name']
        last_user_input = tracker.latest_message.get('text')
        
        # get the last intent that was not affirm or deny
        intents = [event for event in tracker.events if event.get("event") == "user"]
        last_non_affirm_deny_intent = None
        for index in range(len(intents) -1, -1, -1):
            # print(intents[index]['parse_data']['intent']['name'])
            intent = intents[index]['parse_data']['intent']['name']
            if intent != 'affirm' and intent != 'deny':
                last_non_affirm_deny_intent = intent
                break

        # get the last action
        last_action = None
        for event in tracker.events:
            if event.get("event") == "action":
                # print("action:", event.get("name"))
                if event.get("name") != "action_listen" and\
                    event.get("name") != "action_default_fallback" and\
                    event.get("name") != "action_handle_affirm_deny":
                    last_action = event.get("name")
        
        print("Last user input:", last_user_input)
        print("Active loop:", active_loop)
        print("Last intent:", last_intent)
        print("The last non affirm or deny intent was:", last_non_affirm_deny_intent)
        print("Last action:", last_action)

        if last_intent == "nlu_fallback" or (last_intent != "affirm" and last_intent != "deny"):
            # dispatcher.utter_message(response="utter_oos")
            return []
        # elif last_non_affirm_deny_intent == "nlu_fallback":
        #     for event in tracker.events:
        #         if event.get("event") == "action":
        #             print("Last valid action:", event.get("name"))


        # if there is no active loop and this wasn't called right after an action
        if last_non_affirm_deny_intent == "token_issue":
            if last_intent == "affirm":
                return [SlotSet('last_loop', 'token_issue_form'), FollowupAction("token_issue_form")]
            else:
                return [
                    SlotSet("requested_slot", "customer_number"),
                    SlotSet("customer_number", None),
                    SlotSet('last_loop', 'token_issue_form'), 
                    ActiveLoop("token_issue_form"),
                ]
        elif last_non_affirm_deny_intent == "need_meter":
            if last_intent == "affirm":
                return [SlotSet('last_loop', 'new_meter_form'), ActiveLoop("new_meter_form")]
            else:
                dispatcher.utter_message(response="utter_application_link")

        
        # if this was called as a result of responding to an action
        # if active_loop is None:
        if last_action == "utter_is_customer_number_known":
            if last_intent == "affirm":
                # check if customer number already exists
                if tracker.get_slot('customer_number') is not None:
                    dispatcher.utter_message(json_message={
                        'text': "Would you like to initiate the inquiry using {no}?",
                        'customer_number': tracker.get_slot('customer_number')
                    })
                    return [FollowupAction("utter_retry_customer_number")]
                return [FollowupAction("no_electricity_form"), SlotSet("last_loop", "no_electricity_form")]
            else:
                return [FollowupAction("utter_ask_for_complaint")]
        elif last_action == "utter_retry_customer_number":
            # handle re-entering custom number
            if last_intent == "affirm":
                if tracker.get_slot("phone_number") is not None:
                    dispatcher.utter_message(json_message={
                        "text": "Would you like to continue with this phone number {no}?",
                        "phone_number": tracker.get_slot("phone_number")
                    })
                    return [FollowupAction("utter_retry_phone_number")]
                else:
                    return [SlotSet('last_loop', 'no_electricity_form'), ActiveLoop("no_electricity_form"),]
            else:
                return [
                    SlotSet("requested_slot", "customer_number"),
                    SlotSet("customer_number", None),
                    SlotSet('last_loop', 'no_electricity_form'), 
                    ActiveLoop("no_electricity_form"),
                ]
        elif last_action == "utter_retry_phone_number":
            if last_intent == "affirm":
                return [SlotSet('last_loop', 'no_electricity_form'), ActiveLoop("no_electricity_form")]
            else:
                return [
                    SlotSet("requested_slot", "customer_number"),
                    SlotSet("phone_number", None),
                    SlotSet('last_loop', 'no_electricity_form'),
                    ActiveLoop("no_electricity_form")
                ]
        elif last_action == "utter_confirm_complaint":
            if last_intent == "affirm":
                complaint_number = get_complaint_number(tracker.sender_id, tracker.get_slot('customer_number'), tracker.get_slot('phone_number'), None, None)
                dispatcher.utter_message(json_message={
                    'text': "Dear Sir/Madam, Your Complaint No : {no} has been submitted successfully.",
                    'complaint_number': complaint_number
                })
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
            return [FollowupAction("utter_need_help")]
        elif last_action == "utter_ask_for_complaint":
            if last_intent == "affirm":
                return [
                    SlotSet('last_loop', 'file_complaint_form'), 
                    SlotSet("phone_number", None),
                    ActiveLoop("file_complaint_form")]
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
                dispatcher.utter_message(response="utter_need_help")
                return [FollowupAction("action_reset_slots")]
        elif last_action == "utter_need_help" or last_action == "action_session_start": # check why action reset start is here. remove it and check
            if last_intent == "affirm":
                dispatcher.utter_message(json_message={
                    "text": "",
                    "init": "",
                })
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
            return [FollowupAction("action_reset_slots")]
        elif last_action == "utter_meter_sufficient_balance":
            if last_intent == "affirm":
                return [FollowupAction("utter_confirm_complaint")]
            else:
                dispatcher.utter_message(text="Recharge your meter for uninterrupted electricity service.")
                return [FollowupAction("utter_need_help")]
        # there is a loop going on
        elif active_loop == "no_electricity_form":
            if last_intent == "affirm":
                return [SlotSet('last_loop', 'no_electricity_form'), FollowupAction("no_electricity_form")]
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
                return [ActiveLoop(None), FollowupAction("action_loop_completion")]
        elif active_loop == "file_complaint_form":
            if last_intent == "affirm":
                return [SlotSet('last_loop', "file_complaint_form"), ActiveLoop("file_complaint_form")]
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
                return [ActiveLoop(None), FollowupAction("action_loop_completion")]
        elif active_loop == "bill_due_form":
            if last_intent == "affirm":
                return [
                    SlotSet("requested_slot", "bill_number"),
                    SlotSet("bill_number", None),
                    SlotSet('last_loop', 'bill_due_form'), 
                    ActiveLoop("bill_due_form"),
                ]
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
                return [FollowupAction("action_reset_slots")]
        elif active_loop == "token_issue_form":
            if last_intent == "affirm":
                return [
                    SlotSet("requested_slot", "customer_number"),
                    SlotSet("customer_number", None),
                    SlotSet('last_loop', 'token_issue_form'), 
                    ActiveLoop("token_issue_form"),
                ]
            else:
                dispatcher.utter_message(response="utter_thankyou_message")
                return [FollowupAction("action_reset_slots")]
        elif last_action == "utter_retry_tracking_number_help":
            dispatcher.utter_message(json_message={
                'text': "Tracking number is incorrect. Please contact our helpline number 16116.",
                'tracking_number': tracker.get_slot('tracking_number'),
            })
            return [FollowupAction("utter_need_help")]

        return []
            
class ActionLoopCompletion(Action):
    def name(self) -> Text:
        return "action_loop_completion"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        print("\nACTION: action_loop_completion")

        last_loop = tracker.get_slot('last_loop')
        last_request_slot = tracker.get_slot('requested_slot')
        last_tracking_number_retry = tracker.get_slot('tracking_number_retry')
        last_intent = tracker.latest_message['intent']['name']
        print("The last loop was:", last_loop)
        print("Last intent:", last_intent)
        print("Last request slot:", last_request_slot)
        print("Last tracking number retry:", last_tracking_number_retry)

        if last_loop == "no_electricity_form":
            if last_intent == "inform_customer_number":
                dispatcher.utter_message(json_message={
                    "text": "Would you like to continue with this phone number {no}?",
                    "phone_number": tracker.get_slot("phone_number")
                })
                return [FollowupAction("utter_retry_phone_number")]
            customer_number = tracker.get_slot('customer_number')
            phone_number = tracker.get_slot('phone_number')
            print(f"customer number: {customer_number}, phone number: {phone_number}")
            if customer_number is not None and phone_number is not None:
                # check if customer is postpaid or prepaid
                customer_info = dpdc_api.customer_information(customer_number, phone_number)
                if customer_info['Customer_type'] == "Prepaid Customer":
                    return [FollowupAction("utter_meter_sufficient_balance")]
                else:
                    return [FollowupAction("utter_confirm_complaint")]
            else:
                # dispatcher.utter_message(response="utter_thankyou_message")
                return [FollowupAction("action_reset_slots")]
        elif last_loop == "file_complaint_form":
            phone_number = tracker.get_slot("phone_number")
            customer_address = tracker.get_slot("customer_address")
            electricity_office = tracker.get_slot("electricity_office")
            if phone_number and customer_address and electricity_office:
                complaint_number = get_complaint_number(tracker.sender_id, None, phone_number, customer_address, electricity_office)
                # print("Complaint number:", complaint_number)
                dispatcher.utter_message(json_message={
                    'text': "Dear Sir/Madam, Your Complaint No : {no} has been submitted successfully.",
                    'complaint_number': complaint_number
                })
            return [FollowupAction("utter_need_help")]
        # elif last_loop == "token_issue_form" or last_loop == "bill_due_form" or last_loop == "new_meter_form":
        #     return [FollowupAction("action_reset_slots")]
        elif last_loop == "token_issue_form":
            customer_number = tracker.get_slot('customer_number')
            dpdc_response = dpdc_api.prepaid_information(customer_number, None)
            dispatcher.utter_message(text=dpdc_response['message'])
            return [FollowupAction("action_reset_slots")]
        elif last_loop == "new_meter_form" and last_request_slot == "tracking_number" and last_tracking_number_retry >=3:
            # dispatcher.utter_message(json_message={
            #     'text': "Tracking number is incorrect. Please contact our helpline number 16116.",
            #     'tracking_number': tracker.get_slot("tracking_number")
            # }
            return [FollowupAction("utter_need_help"),SlotSet("tracking_number_retry", 0),SlotSet(last_request_slot, None)]
        elif last_loop == "bill_due_form" or last_loop == "new_meter_form":
            return [FollowupAction("action_reset_slots")]


        return []

class ActionResetSlots(Action):

    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Coroutine[Any, Any, List[Dict[Text, Any]]]:
        print("\nACTION: action_reset_slots")

        last_intent = tracker.latest_message['intent']['name']
        customer_number = tracker.get_slot('customer_number')
        phone_number = tracker.get_slot('phone_number')
        last_active_loop = None

        for event in reversed(tracker.events):
            if event.get("event") == "active_loop":
                last_active_loop = event.get("name")
                if event.get("name") is not None:
                    # print("Last active loop:", event.get("name"))
                    last_active_loop = event.get("name")
                    break
        
        print(f"Last intent: {last_intent}, last active loop: {last_active_loop}")

        slots_to_reset = [
            'customer_number',
            'phone_number',
            'customer_address', 
            'electricity_office',
            'tracking_number',
            'bill_number']
        
        # pprint.pp(tracker.events)
        events = [SlotSet(slot, None) for slot in slots_to_reset]
        
        # Make sure no loops/forms are running
        events.append(Restarted())
        
        if last_intent == 'stop_conversation':
            events.append(SlotSet('customer_number', None))
            events.append(SlotSet('phone_number', None))
        else:
            events.append(SlotSet('customer_number', customer_number))
            if last_active_loop == "no_electricity_form":
                events.append(SlotSet('phone_number', phone_number))

        # Print each slot and its value
        for slot_name, slot_value in tracker.slots.items():
            print(f"Slot '{slot_name}': {slot_value}")
            
        print("Slots are being reset\n************************************************")

        # call this global function
        save_last_intent(tracker.sender_id, last_intent)
        
        return events

class ActionStopCurrentConversation(Action):

    def name(self) -> Text:
        return "action_stop_current_conversation"
    
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        events = []

        # Check if a loop is active
        if tracker.active_loop_name:
            # Deactivate the active loop
            events.append(ActiveLoop(None))

            # Get the required slots of the active loop
            loop_name = tracker.active_loop_name
            form_slots = domain.get("forms", {}).get(loop_name, {}).get("required_slots", [])
            
            # Reset the required slots
            for slot in form_slots:
                events.append(SlotSet(slot, None))
            
        dispatcher.utter_message(text="Your current service has been terminated.")
        return events

class ActionPreLoopSteps(Action):

    def name(self) -> Text:
        return "action_pre_loop_steps"
    
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("\nACTION: action_pre_loop_steps")
        last_intent = tracker.latest_message['intent']['name']
        print("Last intent:", last_intent)

        active_loop = tracker.active_loop_name
        print(f"This is the active loop: {active_loop}")
        # if active_loop is not None:
        #     tracker.active_loop = None
            # return [SlotSet('requested_slot', None), ActiveLoop(None)]

        # events = []

        if last_intent == "no_electricity":
            # dispatcher.utter_message(response="utter_is_customer_number_known")
            return [FollowupAction("utter_is_customer_number_known")]
        elif last_intent == "token_issue":
            # check if the customer number is already set
            customer_number = tracker.get_slot('customer_number')
            print("This is customer number:", customer_number)
            if customer_number is None:
                return [SlotSet("last_loop", "token_issue_form"), ActiveLoop('token_issue_form')]
            else:
                dispatcher.utter_message(json_message={
                    'text': 'Would you like to initiate the inquiry using {no}?',
                    'customer_number': customer_number
                })
                return [FollowupAction('action_listen')]
        elif last_intent == "bill_due":
            return [SlotSet('last_loop', "bill_due_form"), ActiveLoop("bill_due_form")]
        elif last_intent == "need_meter":
            dispatcher.utter_message(response="utter_applied_online")

        # elif last_intent == "inform_customer_number":
        #     if tracker.get_slot("phone_number") is not None:
        #         phone_number = tracker.get_slot("phone_number")
        #         dispatcher.utter_message(json_message={
        #             'text': 'Would you like to initiate the inquiry using {no}?',
        #             'phone_number': phone_number
        #         })
        #         return [FollowupAction('utter_ask_continue_with_phone_number')]

        return []