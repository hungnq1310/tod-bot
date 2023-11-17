import logging
from typing import Dict

from src.logging import init_logger

logger = init_logger(__name__)

class DialogueStateTracker:
    def __init__(self, ontology):
        self.reset_states(ontology) # init states

    def reset_states(self, ontology: dict):
        # reset after ending conversation
        self.states = {k: None for k, v in ontology.items()}

    def update_states(self, predicted_states: Dict[str, str]):
        for slot, value in predicted_states.items():
            if value.isdigit():
                value = int(value)
            self.states[slot] = value
