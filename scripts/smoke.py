"""Three-step check of the running diary API; no extra Python packages needed."""
import json
import os
import uuid
from urllib.request import Request, urlopen

base = os.environ.get('API_BASE_URL', 'http://localhost:8000').rstrip('/')

def query(document, variables=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = Request(base + '/graphql', headers=headers, data=json.dumps({
        'query': document, 'variables': variables or {},
    }).encode())
    with urlopen(request, timeout=15) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(result['errors'][0]['message'])
    return result['data']

token = None
try:
    data = query('mutation($x:RegisterInput!){register(input:$x){accessToken}}', {
        'x': {'username': 'smoke', 'email': f'smoke-{uuid.uuid4().hex}@example.org',
              'password': 'StudySmoke2026!'},
    })
    token = data['register']['accessToken']
    print('1. Register: OK')
    meal = query('mutation {addMealLog(input:{name:"Овсяная каша",calories:250,protein:8,fat:5,carbs:42,mealType:"breakfast"}){id}}', token=token)['addMealLog']
    print('2. Add meal: OK')
    data = query('{meals{id} todayStats{calories protein fat carbs}}', token=token)
    assert meal['id'] in [m['id'] for m in data['meals']]
    assert data['todayStats'] == dict(calories=250, protein=8, fat=5, carbs=42)
    print('3. Diary and daily totals: OK (250 / 8 / 5 / 42)')
    print('SMOKE OK')
finally:
    if token:
        query('mutation {deleteAccount}', token=token)
