import pandas as pd
import sqlite3
from datetime import datetime


df = pd.read_json('data/data.jsonl', lines = True)

pd.options.display.max_columns = None

df['_source'] = 'mercadolivre'
df['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Tratar nulos
df['old_money'] = df['old_money'].fillna('0')
df['new_money'] = df['new_money'].fillna('0')
df['reviews_rating_number'] = df['reviews_rating_number'].fillna('0')
df['reviews_amount'] = df['reviews_amount'].fillna('0')

#Garanrir que os dados estão como string antes de usar o .str
df['old_money'] = df['old_money'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
df['new_money'] = df['new_money'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
df['reviews_amount'] = df['reviews_amount'].astype(str).str.replace('[\(\)]', '', regex=True).str.replace('.', '', regex=False)

# converter para float
df['old_money'] = df['old_money'].astype(float)
df['new_money'] = df['new_money'].astype(float)
df['reviews_amount'] = df['reviews_amount'].astype(float)
df['reviews_rating_number'] = df['reviews_rating_number'].astype(int)

# Filtrar apenas produtos com preço entre 1000 e 10000 reais

df = df[
    (df['old_money'] >= 1000) & (df['old_money'] <= 10000) &
    (df['new_money'] >= 1000) & (df['new_money'] <= 10000)
]
print(df)

# Conectar ao banco de dados SQLite (ou criar um novo, se não existir)
conn = sqlite3.connect('data/mercadolivre.db')

#Salvar o DataFrame no banco de dados
df.to_sql('mercadolivre', conn, if_exists='replace', index=False)

# Fechar a conexão
conn.close()