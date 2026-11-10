"""Live API acceptance checks. Run only against a disposable study database."""
import json
import os
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

BASE = os.environ.get('API_BASE_URL', 'http://localhost:8000').rstrip('/')


def graphql(query, variables=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = Request(BASE + '/graphql', data=json.dumps({'query': query, 'variables': variables or {}}).encode(), headers=headers)
    with urlopen(req, timeout=15) as response:
        return json.load(response)


class DiaryAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounts = []
        cls.users = []
        for n in range(2):
            email = f'lab-{uuid.uuid4().hex}@example.org'
            password = 'УчебныйПароль42!'
            r = graphql('mutation($x:RegisterInput!){register(input:$x){accessToken refreshToken}}', {'x': {'username':f'lab_{n}', 'email':email, 'password':password}})
            assert not r.get('errors'), r
            auth = r['data']['register']
            cls.accounts.append((email,password,auth['accessToken'],auth['refreshToken']))
            cls.users.append(auth['accessToken'])
        cls.a,cls.b=cls.users

    @classmethod
    def tearDownClass(cls):
        for token in cls.users:
            graphql('mutation {deleteAccount}', token=token)

    def ok(self, query, variables=None, token=None):
        r=graphql(query, variables, token or self.a)
        self.assertNotIn('errors', r, r)
        return r['data']

    def bad(self, query, variables=None, token=None):
        r=graphql(query, variables, token or self.a)
        self.assertTrue(r.get('errors'),r)
        return r

    def add(self, **extra):
        fields={'name':'Овсяная каша','calories':250,'protein':8,'fat':5,'carbs':42,'mealType':'breakfast'}
        fields.update(extra)
        return self.ok('mutation($x:AddMealLogInput!){addMealLog(input:$x){id name source nutrition{calories protein fat carbs}}}', {'x':fields})['addMealLog']

    def remove(self, id):
        self.ok('mutation($id:Int!){deleteMealLog(logId:$id)}', {'id':id})

    def test_01_health_and_schema(self):
        with urlopen(BASE+'/health') as r: h=json.load(r)
        self.assertEqual(h,{'status':'ok','database':'ok','photos_enabled':False})
        self.assertEqual(self.ok('{__typename}')['__typename'],'AppQuery')

    def test_02_login_and_refresh(self):
        email,password,_,refresh=self.accounts[0]
        d=self.ok('mutation($x:LoginInput!){login(input:$x){accessToken}}',{'x':{'email':email,'password':password}})
        self.assertTrue(d['login']['accessToken'])
        self.assertTrue(self.ok('mutation($x:RefreshInput!){refreshTokens(input:$x){accessToken}}',{'x':{'refreshToken':refresh}})['refreshTokens']['accessToken'])

    def test_03_bad_credentials_and_token_type(self):
        email,_,access,refresh=self.accounts[0]
        self.bad('mutation($x:LoginInput!){login(input:$x){accessToken}}',{'x':{'email':email,'password':'wrong'}})
        self.bad('{me{id}}', token=refresh)
        self.bad('mutation($x:RefreshInput!){refreshTokens(input:$x){accessToken}}',{'x':{'refreshToken':access}})
        self.assertTrue(graphql('{me{id}}').get('errors'))
        self.bad('{me{id}}',token='invalid-token')

    def test_04_duplicate_registration(self):
        email,password,*_=self.accounts[0]
        self.bad('mutation($x:RegisterInput!){register(input:$x){accessToken}}',{'x':{'username':'duplicate','email':email,'password':password}})

    def test_05_manual_diary_stats_and_ownership(self):
        m=self.add()
        try:
            self.assertEqual(m['nutrition'],{'calories':250.0,'protein':8.0,'fat':5.0,'carbs':42.0})
            self.assertEqual(m['source'],'manual')
            self.assertIn(m['id'],[v['id'] for v in self.ok('{meals{id}}')['meals']])
            self.assertNotIn(m['id'],[v['id'] for v in self.ok('{meals{id}}',token=self.b)['meals']])
            self.bad('mutation($id:Int!){deleteMealLog(logId:$id)}',{'id':m['id']},token=self.b)
            self.assertEqual(self.ok('{todayStats{calories protein fat carbs}}')['todayStats'],m['nutrition'])
            self.assertEqual(self.ok('{weeklyAverage{calories}}')['weeklyAverage']['calories'],35.7)
        finally:
            self.remove(m['id'])
        self.assertNotIn(m['id'],[v['id'] for v in self.ok('{meals{id}}')['meals']])

    def test_06_validation_without_write(self):
        before=self.ok('{me{id totalRecords}}')['me']['totalRecords']
        base={'name':'x','calories':250,'protein':8,'fat':5,'carbs':42,'mealType':'breakfast'}
        for invalid in [{'calories':-1},{'protein':-1},{'name':' '},{'mealType':'invalid'}]:
            self.bad('mutation($x:AddMealLogInput!){addMealLog(input:$x){id}}',{'x':dict(base,**invalid)})
        self.bad('mutation($x:AddMealLogInput!){addMealLog(input:$x){id}}',{'x':{k:v for k,v in base.items() if k!='name'}})
        self.assertEqual(before,self.ok('{me{id totalRecords}}')['me']['totalRecords'])

    def test_07_week_boundary_and_timezone(self):
        today=datetime.now(timezone.utc).replace(tzinfo=None,hour=8,minute=0,second=0,microsecond=0)
        inside=self.add(calories=1400,eatenAt=(today-timedelta(days=6)).isoformat())
        outside=self.add(calories=7000,eatenAt=(today-timedelta(days=7)).isoformat())
        future=self.add(calories=9000,eatenAt=(today+timedelta(days=1)).isoformat())
        try:
            self.assertEqual(self.ok('{weeklyAverage{calories}}')['weeklyAverage']['calories'],200.0)
            self.assertEqual(self.ok('{todayStats{calories}}')['todayStats']['calories'],0)
        finally:
            for m in [inside,outside,future]:self.remove(m['id'])
        aware=self.add(eatenAt=datetime.now(timezone.utc).isoformat())
        self.remove(aware['id'])

    def test_08_goal_create_update_validation_and_progress(self):
        x={'goalType':'loss','targetKg':5,'currentWeightKg':80,'dailyCalories':2000}
        q='mutation($x:GoalInput!){upsertGoal(input:$x){id targetKg progressPercent}}'
        first=self.ok(q,{'x':x})['upsertGoal']
        self.assertEqual(first['progressPercent'],0)
        for patch in [{'targetKg':0},{'dailyCalories':-1},{'goalType':'gain'},{'goalType':'invalid'}]:
            self.bad(q,{'x':dict(x,**patch)})
        second=self.ok(q,{'x':dict(x,targetKg=4)})['upsertGoal']
        self.assertEqual(first['id'],second['id'])
        self.assertEqual(second['targetKg'],4)
        self.assertIsNone(self.ok('{goal{id}}',token=self.b)['goal'])
        positive=self.add(calories=1500)
        try:
            progress=self.ok('{goal{progressPercent totalCalorieDeficit}}')['goal']
            self.assertEqual(progress['progressPercent'],1.62)
            self.assertEqual(progress['totalCalorieDeficit'],500.0)
        finally:self.remove(positive['id'])
        m=self.add(calories=2500)
        try:self.assertEqual(self.ok('{goal{progressPercent}}')['goal']['progressPercent'],0)
        finally:self.remove(m['id'])

    def test_09_profile_preferences_and_privacy(self):
        self.assertEqual(self.ok('{me{username} achievements{totalRecords}}')['me']['username'],'lab_0')
        q='mutation($x:PreferencesInput!){updatePreferences(input:$x){dietType mealsPerDay waterGoalMl notificationsEnabled}}'
        p=self.ok(q,{'x':{'dietType':'balanced','mealsPerDay':4,'waterGoalMl':2500,'notificationsEnabled':False}})['updatePreferences']
        self.assertEqual(p,self.ok('{preferences{dietType mealsPerDay waterGoalMl notificationsEnabled}}')['preferences'])
        updated=self.ok(q,{'x':{'mealsPerDay':5}})['updatePreferences']
        self.assertEqual(updated['waterGoalMl'],2500)
        self.bad(q,{'x':{'mealsPerDay':0}})
        self.assertEqual(self.ok('{preferences{mealsPerDay}}',token=self.b)['preferences']['mealsPerDay'],3)
        self.ok('mutation {updatePrivacySettings(input:{analyticsEnabled:false}){analyticsEnabled}}')
        self.assertFalse(self.ok('{privacySettings{analyticsEnabled}}')['privacySettings']['analyticsEnabled'])

    def test_10_photo_disabled_and_pagination(self):
        r=self.bad('mutation {requestPhotoUpload{requestId}}')
        self.assertIn('Core',r['errors'][0]['message'])
        self.bad('mutation {confirmPhotoUpload(requestId:1){status}}')
        self.bad('{meals(skip:-1){id}}')
        self.bad('{meals(limit:0){id}}')

    def test_11_registration_validation(self):
        base={'username':'student','email':'unused@example.org','password':'GoodPassword42!'}
        for patch in [{'username':' '},{'email':'invalid'},{'password':'short'},{'password':'x'*73}]:
            self.bad('mutation($x:RegisterInput!){register(input:$x){accessToken}}',{'x':dict(base,**patch)})

if __name__=='__main__':unittest.main(verbosity=2)
