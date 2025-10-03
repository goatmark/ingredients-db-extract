import os
import pandas as pd
from notion_client import Client

import dotenv
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DB_ID = os.getenv('NOTION_INGREDIENTS_DB_ID')

notion = Client(auth=NOTION_API_KEY)

rows = []
has_more = True
next_cursor = None

while has_more:
    query_kwargs = {"page_size": 100}
    if next_cursor:
        query_kwargs["start_cursor"] = next_cursor
    response = notion.databases.query(database_id=NOTION_DB_ID, **query_kwargs)
    for result in response.get('results', []):
        props = result.get('properties', {})
        row = {"page_id": result.get('id')}
        for key, value in props.items():
            vtype = value.get('type')
            if vtype == 'title' and value['title']:
                row[key] = value['title'][0]['plain_text']
            elif vtype == 'rich_text' and value['rich_text']:
                row[key] = value['rich_text'][0]['plain_text']
            elif vtype == 'number':
                row[key] = value.get('number')
            elif vtype == 'checkbox':
                row[key] = value.get('checkbox')
            elif vtype == 'select' and value.get('select'):
                row[key] = value['select']['name']
            elif vtype == 'multi_select' and value.get('multi_select'):
                row[key] = ', '.join([opt['name'] for opt in value['multi_select']])
            elif vtype == 'date' and value.get('date'):
                row[key] = value['date'].get('start')
            else:
                row[key] = ''
        rows.append(row)
    has_more = response.get('has_more', False)
    next_cursor = response.get('next_cursor')

df = pd.DataFrame(rows)
df = df.loc[:, ~df.columns.duplicated()]
df.to_csv('notion_ingredients.csv', index=False)
print('Saved as notion_ingredients.csv (with page IDs)')

# Save a simplified CSV with only the key columns
simple_cols = ['page_id','Ingredient', 'Section', 'Plant']
df_simple = df[[col for col in simple_cols if col in df.columns]]
df_simple.to_csv('notion_ingredients_simple.csv', index=False)
print('Saved as notion_ingredients_simple.csv (ingredient, page_id, section, plant)')