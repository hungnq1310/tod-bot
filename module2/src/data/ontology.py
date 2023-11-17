hotel_1_ontology_slot = [
    "destination",
    "number_of_rooms",
    "check_in_date",
    "number_of_days",
    "star_rating",
    "hotel_name",
    "street_address",
    "phone_number",
    "price_per_night",
    "has_wifi"
]

policy_constraint_hotels_1 = {
    "required_slots_search" : ["destination"],
    "required_slots_book" : ["hotel_name", "check_in_date", "number_of_days", "destination", "number_of_rooms"],
    "required_slots_info" : ["hotel_name", "destination"],
}

policy_domain = {
    "Hotels_1": policy_constraint_hotels_1
}