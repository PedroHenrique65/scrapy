import pandas as pd
import sqlite3
from datetime import datetime

dados_ecommerce = pd.read_json('data/data.jsonl', lines = True)

print(dados_ecommerce)