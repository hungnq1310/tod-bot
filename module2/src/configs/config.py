from typing import (
    Optional, 
    Union, 
    List
)
import logging
import time
import os
from dataclasses import dataclass, field, fields
from dotenv import load_dotenv

@dataclass
class DST_Config:
    config_model: str = field(
        default="google/flan-t5-base", 
        metadata={"help": "config of model"}
    )
    model_name_or_path: str = field(
        default="google/flan-t5-base", 
        metadata={"help": "path to folder contains checkpoint or huggingface name"}
    )
    tokenizer_path: str = field(
        default="google/flan-t5-base", 
        metadata={"help": "path to folder contains tokenizer or huggingface name"}
    )

class Policy_Config:
    db_path: str = field(
        default="./db/mydatabase.db", 
        metadata={"help": "path to database"}
    )
