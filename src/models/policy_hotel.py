import logging
from typing import Dict, Any


from configs.config import Policy_Config
from base.policy_base import PolicyBase
from models.dst import DialogueStateTracker



class PolicyHotel(PolicyBase):
    def __init__(self, 
                 config: Policy_Config, 
                 policy_domain: str,
                 ontology: Dict[str, str]):
        super().__init__(config=config,
                         ontology=ontology
                         )
        self.policy_domain = policy_domain
        # define needed slots for search and book
        self.database_slots = ["hotel_name", "destination", "street_address", "number_of_rooms_available",
                               "star_rating", "price_per_night", "has_wifi", "phone_number"]
        self.required_slots_search = ["destination"]
        self.required_slots_book = ["hotel_name", "check_in_date", "number_of_days", "destination", "number_of_rooms"]
        self.required_slots_info = ["hotel_name", "destination"]

        # manage search results
        self.count_search = 0
        self.current_result = {}
        self.current_book = {}
        self.change_slots_after_negate = {}


    def search_hotel(self, alts=False):
        dict_to_search = {}
        # get not none slot_values to search from states tracker
        for slot, value in self.tracker.states.items():
            if value != None and slot in self.database_slots:
                dict_to_search.setdefault(slot, value)

        query = None
        if alts:
            query = self.generate_query(domain="Hotels_1",
                                        constraint_to_search=dict_to_search,
                                        slot_to_query_dif="hotel_name",
                                        negate_current_result=self.current_result,
                                        )
        else:
            query = self.generate_query(domain="Hotels_1",
                                        constraint_to_search=dict_to_search)
        rows = self.select_db(query)
        if rows:
            self.current_result.clear()
            for i in range(len(self.database_slots)):
                self.current_result.setdefault(self.database_slots[i], rows[0][i])
            self.count_search = len(rows)
            print("---result:", self.current_result)
        return dict_to_search

    def search_info(self, slots_values_requested):
        # self.current_result == {}
        if not self.current_result:
            dict_to_search = {"hotel_name" : self.tracker.states["hotel_name"]}
            query = self.generate_query(
                domain = "Hotels_1",
                constraint_to_search = dict_to_search,
            )
            rows = self.select_db(query)
            if rows:
                for i in range(len(self.database_slots)):
                    self.current_result.setdefault(self.database_slots[i], rows[0][i])
                print("---result:", self.current_result)
            else: 
                print("Not have any query results")

        inform_value = {}
        for i in slots_values_requested:
            slot = i
            inform_value.setdefault(slot, self.current_result[i])
        return inform_value


    def book_hotel(self):
        for slot in self.database_slots:
            if slot not in ["number_of_rooms_available"]:
                self.current_book[slot] = self.current_result[slot]
        for slot in self.required_slots_book:
            if self.tracker.slots[slot] != None:
                self.current_book[slot] = self.tracker.states[slot]

    def confirm_book(self):
        confirm_slot = {}
        if self.change_slots_after_negate != {}:
            confirm_slot.update(self.change_slots_after_negate)
            self.change_slots_after_negate.clear()
        else:
            for slot in ["destination", "hotel_name", "check_in_date", "number_of_days", "number_of_rooms"]:
                confirm_slot.setdefault(slot, self.current_book[slot])
        return confirm_slot