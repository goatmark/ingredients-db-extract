import os
import requests
import pandas as pd

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DB_ID = os.getenv('NOTION_INGREDIENTS_DB_ID')

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"

rows = []
has_more = True
next_cursor = None

while has_more:
    payload = {"page_size": 100}
    if next_cursor:
        payload["start_cursor"] = next_cursor
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    for result in data.get('results', []):
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
    has_more = data.get('has_more', False)
    next_cursor = data.get('next_cursor')

df = pd.DataFrame(rows)
df = df.loc[:, ~df.columns.duplicated()]
df.to_csv('notion_ingredients.csv', index=False)
print('Saved as notion_ingredients.csv (with page IDs)')
