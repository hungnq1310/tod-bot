import logging

from base.policy_base import PolicyBase

class Dialogue_Manage_Base:
    def __init__(self, 
                 policy: PolicyBase):
        self.input_transformed = {}
        self.policy = policy
        self.dict_negate_request = {"REQUEST": []}
        self.user_intent = ""
        self.offer_intent = "SearchHotel"

    def is_odd(self, output_dst) -> str:
        return True if output_dst == "general_asking" else False

    def format_string_input(self, output_dst: str):
        self.input_transformed.clear()
        
        if self.is_odd(output_dst):
            reverse_map_ontology = {v: k for k, v in self.policy.map_ontology.items()}
            # format: domain:[inform(slot=value)]
            action_slot_value = output_dst.split(":")[1]
            action_slot_value_list = [e_.strip() \
                                        .replace("[", "") \
                                        .replace("]", "") \
                                        .replace(")", "") for e_ in  action_slot_value.split("and")
                                     ]

            for sub in action_slot_value_list:
                # format: [inform(slot=value), action(slot=value)]
                if "(" not in sub:
                    if sub.upper() in ["AFFIRM_INTENT"]:
                        action = sub.upper()
                        self.input_transformed.setdefault(action, "")
                    elif sub.upper() in ["SELECT", "AFFIRM", "NEGATE", "REQUEST_ALTS", "THANK_YOU", "GOODBYE", "NEGATE_INTENT"]:
                        action = sub.upper()
                        self.input_transformed.setdefault(action, None)
                else:
                    action, slot_value = sub.split("(")
                    action = action.upper()
                    # set type value for each action
                    if action not in self.input_transformed.keys():
                        if action == "INFORM_INTENT":
                            self.input_transformed.setdefault(action, "")
                        elif action == "REQUEST":
                            self.input_transformed.setdefault(action, [])
                        else:
                            self.input_transformed.setdefault(action, {})
                    

                    if action == "INFORM_INTENT":
                        self.input_transformed[action] = slot_value
                    else:
                        # case inform
                        if "=" in slot_value:
                            # slot = reverse_map_ontology[slot_value.split("=")[0]]
                            slot, value = slot_value.split("=")
                            # hotel_name -> slot0
                            slot = reverse_map_ontology[slot]
                            self.input_transformed[action].setdefault(slot, value)
                        # case request(slot)
                        else:
                            slot = reverse_map_ontology[slot_value]
                            self.input_transformed[action].append(slot)

    def clear_current(self):
        self.policy.tracker.reset_states(self.policy.map_ontology)
        self.policy.clear_information()
        self.dict_negate_request = {"REQUEST": []}
        self.offer_intent = ""
        self.user_intent = "SearchHotel"

    def transform_action(self):
        raise NotImplementedError