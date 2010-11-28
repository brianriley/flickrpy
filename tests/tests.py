import unittest
import fixtures

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import flickr

class TestURLOpen(object):
    URL = ''
    
    def __init__(self, *args, **kwargs):
        TestURLOpen.URL = args[0]
    
    @staticmethod
    def read():
        for key, value in fixtures.RESPONSES.iteritems():
            if key in TestURLOpen.URL:
                return value
        return ''

class FlickrAPITestCase(unittest.TestCase):
    
    def setUp(self):
        flickr.urllib.urlopen = TestURLOpen
        self.flickr = flickr.Flickr(api_key='123', api_secret='456')
    
    def test_photos_get_info(self):
        response = self.flickr.photos.get_info(photo_id=5157647292)
        self.assertEquals('ok', response['stat'])
    
    def test_blogs_get_services(self):
        response = self.flickr.blogs.get_services()
        self.assertEquals('ok', response['stat'])
    
    def test_commons_get_institutions(self):
        response = self.flickr.commons.get_institutions()
        self.assertEquals('8623220@N02', response['institutions']['institution'][0]['nsid'])
    
    def test_login_url(self):
        _expected_login_url = 'http://api.flickr.com/services/auth/?perms=read&api_sig=b15ac92c6df03403cfe748330c541d06&api_key=123'
        login_url = self.flickr.login_url('read')
        self.assertEquals(_expected_login_url, login_url)
    
    def test_unknown_method(self):
        response = self.flickr.unknown_method()
        self.assertEquals('fail', response['stat'])

if __name__ == '__main__':
    unittest.main()