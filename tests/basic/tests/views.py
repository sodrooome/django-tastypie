from django.http import HttpRequest
from django.test import TestCase
try:
    import json
except ImportError:
    import simplejson as json


class ViewsTestCase(TestCase):
    def test_gets(self):
        resp = self.client.get('/api/v1/', data={'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        deserialized = json.loads(resp.content)
        self.assertEqual(len(deserialized), 2)
        self.assertEqual(deserialized['notes'], u'/api/v1/notes/')
        
        resp = self.client.get('/api/v1/notes/', data={'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        deserialized = json.loads(resp.content)
        self.assertEqual(len(deserialized), 2)
        self.assertEqual(deserialized['meta']['limit'], 20)
        self.assertEqual(len(deserialized['objects']), 2)
        self.assertEqual([obj['title'] for obj in deserialized['objects']], [u'First Post!', u'Another Post'])
        
        resp = self.client.get('/api/v1/notes/1/', data={'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        deserialized = json.loads(resp.content)
        self.assertEqual(len(deserialized), 9)
        self.assertEqual(deserialized['title'], u'First Post!')
        
        resp = self.client.get('/api/v1/notes/set/2;1/', data={'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        deserialized = json.loads(resp.content)
        self.assertEqual(len(deserialized), 1)
        self.assertEqual(len(deserialized['objects']), 2)
        self.assertEqual([obj['title'] for obj in deserialized['objects']], [u'Another Post', u'First Post!'])
    
    def test_posts(self):
        request = HttpRequest()
        post_data = '{"content": "A new post.", "is_active": true, "title": "New Title", "slug": "new-title", "user": "/api/v1/users/1/"}'
        request._raw_post_data = post_data
        
        resp = self.client.post('/api/v1/notes/', data=post_data, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp['location'], 'http://testserver/api/v1/notes/3/')

        # make sure posted object exists
        resp = self.client.get('/api/v1/notes/3/', data={'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        obj = json.loads(resp.content)
        self.assertEqual(obj['content'], 'A new post.')
        self.assertEqual(obj['is_active'], True)
        self.assertEqual(obj['user'], '/api/v1/users/1/')
