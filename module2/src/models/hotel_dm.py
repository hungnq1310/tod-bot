
import logging

from base.policy_base import PolicyBase
from base.dm_base import Dialogue_Manage_Base

class Hotel_DM(Dialogue_Manage_Base):
    def __init__(self, 
                 policy: PolicyBase):
        super.__init__(self, policy)
        

    def transform_action(self):
        if self.user_intent == "SearchHotel":
            self.offer_intent = "ReserveHotel"
        print("---action:", self.input_transformed)

        # Add old REQUESTS in previous turns
        self.policy.system_action.clear()
        if self.dict_negate_request["REQUEST"] != []:
            self.input_transformed.update(self.dict_negate_request)
            self.dict_negate_request["REQUEST"].clear()

        # Set USER_INTENT
        self.input_transformed.update({"INTENT":self.user_intent})

        # Analyze actions
        for user_action, slot_value in self.input_transformed.items():

            # Analyze action INFORM
            if user_action == "INFORM":

                # Step 1: update slots
                self.policy.tracker.update_slots(slot_value)

                # Step 2: OFFER
                if "REQUEST_ALTS" not in self.input_transformed.keys():
                    if "NEGATE" not in self.input_transformed.keys():

                        # Step 3: check slot to search
                        result_check_search = self.policy.check_slot_to_search()
                        if result_check_search == "accept_search":
                            dict_to_search = self.policy.search_hotel() # dict_to_search cantains current slots to select hotel

                            # Step 4: offer hotel
                            if "hotel_name" not in dict_to_search.keys():
                                self.policy.system_action.setdefault("OFFER", {})
                                self.policy.system_action["OFFER"].update({"hotel_name": self.policy.current_result["hotel_name"]})
                                self.policy.system_action["OFFER"].update({"star_rating": self.policy.current_result["star_rating"]})
                            if self.user_intent == "":
                                self.user_intent = "SearchHotel"
                            if self.user_intent == "SearchHotel":
                                self.offer_intent = "ReserveHotel"
                            if all(self.policy.tracker.slots[slot] != None for slot in
                                   ["hotel_name", "destination"]):
                                self.policy.system_action.update({"OFFER_INTENT": self.offer_intent})

                        # Request missing slots
                        else:
                            if "REQUEST" not in self.policy.system_action.keys():
                                self.policy.system_action.setdefault("REQUEST", [])
                            for slot in result_check_search:
                                self.policy.system_action["REQUEST"].append(slot)
                    else:
                        # Step 3: add new slots to change_slots_after_negate
                        self.policy.change_slots_after_negate.update(slot_value)

                        # Case: change hotel_name or destination
                        if "hotel_name" in slot_value.keys() or "destination" in slot_value.keys():
                            # remove info of old hotel
                            remove_info = {slot: None for slot in
                                           ["street_address", "star_rating", "price_per_night", "has_wifi", "phone_number"]}
                            self.policy.tracker.update_slots(remove_info)

                            # search new hotel
                            if "hotel_name" not in slot_value.keys():
                                self.policy.tracker.update_slots({"hotel_name": None})
                                _ = self.policy.search_hotel()
                                self.policy.system_action.setdefault("OFFER", {})
                                self.policy.system_action["OFFER"].update({"hotel_name": self.policy.current_result["hotel_name"]})
                                self.policy.system_action["OFFER"].update({"star_rating": self.policy.current_result["star_rating"]})
                            else:
                                self.policy.tracker.update_slots({"destination": None})
                                _ = self.policy.search_hotel()
                                self.policy.tracker.update_slots({"destination": self.policy.current_result["destination"]})
                                self.policy.change_slots_after_negate.update({"destination": self.policy.tracker.slots["destination"]})
                            if self.user_intent == "":
                                self.user_intent = "SearchHotel"
                            if self.user_intent == "SearchHotel":
                                self.offer_intent = "ReserveHotel"
                            if all(self.policy.tracker.slots[slot] != None for slot in ["hotel_name", "destination"]):
                                self.policy.system_action.update({"OFFER_INTENT": self.offer_intent})

            elif user_action == "REQUEST" and slot_value != {}:
                result_check_search = self.policy.check_slot_to_search()
                if result_check_search == "accept_search":
                    inform_value = self.policy.search_info(slot_value)
                    self.policy.system_action.update({"INFORM":inform_value})

                # Request missing slots
                else:
                    self.dict_negate_request["REQUEST"].append(slot_value)
                    self.policy.system_action.setdefault("REQUEST", [])
                    for slot in result_check_search:
                        self.policy.system_action["REQUEST"].append(slot)

            elif user_action == "INFORM_INTENT":
                self.user_intent = slot_value
                if self.user_intent == "SearchHotel":
                    self.offer_intent = "ReserveHotel"

            elif user_action == "AFFIRM_INTENT" or user_action == "SELECT":
                self.policy.tracker.update_slots({"hotel_name":self.policy.current_result["hotel_name"]})
                self.user_intent = "ReserveHotel"
                self.system_intent = ""

            elif user_action == "AFFIRM":
                self.user_intent = ""
                self.policy.system_action.update({"NOTIFY_SUCCESS": None})
                self.policy.system_action.update({"REQ_MORE": None})

            elif user_action == "THANK_YOU":
                if "NEGATE" in self.input_transformed.keys() or "GOODBYE" in self.input_transformed.keys():
                    self.policy.system_action.update({"GOODBYE": None})
                else:
                    self.policy.system_action.update({"REQ_MORE": None})
                    self.clear_current()

            elif user_action == "NEGATE_INTENT":
                if "GOODBYE" in self.input_transformed.keys():
                    self.policy.system_action.update({"GOODBYE": None})
                else:
                    self.policy.system_action.update({"REQ_MORE": None})
                    self.input_transformed["INTENT"] = ""
                    self.clear_current()

            elif user_action == "REQUEST_ALTS":
                dict_to_search = self.policy.search_hotel(alts=True)
                if "hotel_name" not in dict_to_search.keys():
                    self.policy.system_action.setdefault("OFFER", {})
                    self.policy.system_action["OFFER"].update({"hotel_name": self.policy.current_result["hotel_name"]})
                    self.policy.system_action["OFFER"].update({"star_rating": self.policy.current_result["star_rating"]})
                if self.user_intent == "SearchHotel":
                    self.offer_intent = "ReserveHotel"
                if all(self.policy.tracker.slots[slot] != None for slot in ["hotel_name", "destination"]):
                    self.policy.system_action.update({"OFFER_INTENT": self.offer_intent})

        if self.user_intent == "ReserveHotel":
            self.offer_intent = ""
            if "OFFER_INTENT" in self.policy.system_action.keys():
                del self.policy.system_action["OFFER_INTENT"]
            result_check_book = self.policy.check_slot_to_book()
            if result_check_book == "accept_book":
                self.policy.book_hotel()
                confirm_slot = self.policy.confirm_book()
                self.policy.system_action.setdefault("CONFIRM", {})
                self.policy.system_action["CONFIRM"].update(confirm_slot)
            # Request missing slots
            else:
                self.policy.system_action.setdefault("REQUEST", [])
                for slot in result_check_book:
                    self.policy.system_action["REQUEST"].append(slot)

        print("---user  intent:", self.user_intent)
        print("---offer intent:", self.offer_intent)
        if self.dict_negate_request["REQUEST"] != []:
            print("---old requests:", self.dict_negate_request)
        if self.policy.current_book != {}:
            print("---book :", self.policy.current_book)

        print("\nUser's current slots")
        for k,v in self.policy.tracker.slots.items():
            if v != None:
                print("---",k,":",v)
        print("\n")
