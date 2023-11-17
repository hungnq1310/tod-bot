import logging
from typing import List, Dict, Any, Optional
import sqlite3

from abc import ABC, abstractmethod
from models.dst import DialogueStateTracker
from configs.config import Policy_Config

"""
Example Ontology of Hotel:
{
    "destination": "descript0",
    "number_of_rooms": "descript1",
    "check_in_date": "descript2",
    "number_of_days": "descript3",
    "star_rating": "descript4",
    "hotel_name": "descript5",
    "street_address": "descript6",
    "phone_number": "descript7",
    "price_per_night": "descript8",
    "has_wifi": "descript9"
}
"""

class PolicyBase(ABC):
    def __init__(self, config: Policy_Config, ontology: dict):
        self.config = config
        self.map_ontology = self.create_map_ontology(ontology)
        self.tracker = DialogueStateTracker(self.map_ontology)
        

    def create_map_ontology(self, ontology: dict) -> Dict[str, str]:
        map_ontology = {}
        for idx, (slot, _) in enumerate(ontology.items()):
            map_ontology.setdefault(slot, f"slot{idx}")
        return map_ontology

    def check_slot_to_search(self, required_slots_search: List[str]):
        list_missing_required_slots_search = self.check_missing_slots(self.tracker.states, required_slots_search)
        if len(list_missing_required_slots_search) == 0:
            return "accept_search"
        return list_missing_required_slots_search

    def check_slot_to_book(self, required_slots_book: List[str]):
        list_missing_required_slots_book = self.check_missing_slots(self.tracker.states, required_slots_book)
        if len(list_missing_required_slots_book) == 0:
            return "accept_book"
        return list_missing_required_slots_book
    
    def check_missing_slots(self, current_state, required_slots):
        missing_slots = []
        for slot in required_slots:
            if current_state[slot] is None:
                missing_slots.append(slot)
        return missing_slots

    def select_db(self, query: str) -> Optional[List[Any]]:
        # check connection
        try:
            conn = sqlite3.connect(self.config.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            return rows
        except:
            raise Exception("Cannot connect to database")
        
    def generate_query(self, 
                       domain: str,
                       constraint_to_search: Dict[str, Any], 
                       slot_to_query_dif: str = None,
                       negate_current_result: Dict[str, Any] = {}
                       ) -> str:
        query = f"SELECT * FROM {domain} WHERE "
        conditions = []
        for slot, value in constraint_to_search.items():
            value = "'{}'".format(value) if type(value) == str else value
            condition = f"{slot} = {value}"
            conditions.append(condition)
        # when user  need another after negate the current result from db and
        if not negate_current_result:
            if not slot_to_query_dif:
                print("Need to have `slot_to_query_dif` for getting the other results")
            value = "'{}'".format(negate_current_result.get(slot_to_query_dif))
            condition = f"{slot} != {value}"
            conditions.append(condition)
        query += " AND ".join(conditions)
        print("---query: ", query)
        return query

    def clear_information(self):
        raise NotImplementedError
    
