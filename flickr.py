"""
Flickrpy
========

A lightweight Pythonic [Flickr API](http://www.flickr.com/services/api/) metaprogram.

*Requires Python 2.6+*

Usage
-----

Flickr API methods are mapped directly to class methods, except for two small 
exceptions: (1) method names follow PEP 8 style, and (2) they do not need to 
begin with `flickr`. So: `flickr.photos.getInfo` and `flickr.photos.geo.getLocation` 
become: `<Flickr object>.photos.get_info()` and `<Flickr object>.photos.geo.get_location()`.

Arguments required by the API method should be passed as a dictionary to the call 
(except for `api_key`, which is required on every call and set on class instantiation).
    
Full usage example:

    >>> flickr = Flickr(api_key='123', api_secret='321')
    >>> flickr.photos.get_info({'photo_id': 5157647292})['stat']
    'ok'
    >>> flickr.commons.get_institutions()['institutions']['institution'][0]['nsid']
    '8623220@N02'

Responses
---------

Requests to Flickr are made as JSON calls, and responses are Python dictionaries.

Notes
-----

- The photo upload API isn't yet implemented

"""
import urllib
import json
import hashlib

class FlickrError(Exception):
    """
    FlickrError
    -----------
    
    Exception thrown by any Flickr error.
    """
    pass

class Flickr(object):
    """
    Flickr
    ------
    
    The main wrapper class.
    """
    
    def __init__(self, api_key, api_secret):
        """The constructor takes the following arguments:
        
            * api_key <string>
            * api_secret <string>
        
        """
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Meta-attributes used by the service
        self.base_url = 'http://api.flickr.com/services/rest/?{0}'
        self.auth_url = 'http://api.flickr.com/services/auth/?{0}'
        self.method_name = self._init_method()
    
    def __getattr__(self, attr):
        """
        If the attribute exists on Flickr, return it. Otherwise, save the attribute(s) 
        in self.method_name for later use in the Flickr call and return self.
        """
        try:
            return super(self.__class__, self).__getattr__(attr)
        except AttributeError:
            self.method_name += '.{0}'.format(attr)
            return self
    
    def __call__(self, extra_params={}):
        """
        When a call is made to a Flickr method, the parameter list is constructed--using 
        self.method_name--self.method_name is cleared for future use, and the call is made 
        to the REST API.
        """
        params = self._get_params(extra_params)
        self.method_name = self._init_method()
        return self._make_call(params)
    
    def _init_method(self):
        """
        Initialize the method name to `flickr`--the prefix used by all Flickr method calls.
        """
        return 'flickr'
    
    def _get_params(self, params):
        """
        Create a full dictionary of parameters combining a base set with extra parameters 
        passed in to the calls.
        """
        _params = {
            'api_key': self.api_key,
            'format': 'json',
            'nojsoncallback': 1,
            'method': self._format_method_name()
        }
        
        _params.update(params)
        return _params
    
    def _format_method_name(self):
        """
        Format the Pythonic method_name into the Flickr API's methodName camel case.
        """
        parts = self.method_name.split('_')
        _parts = [part.capitalize() for part in parts[1:]]
        _parts.insert(0, parts[0])
        return ''.join(_parts)
    
    def _make_call(self, params):
        """
        Make the call to Flickr.
        """
        # All calls must be signed
        params.update({'api_sig': self._sign_params(params)})
        try:
            response = urllib.urlopen(self.base_url.format(urllib.urlencode(params)))
        except IOError:
            raise FlickrError('Service down')
        
        try:
            return json.loads(response.read())
        except ValueError:
            raise FlickrError('Malformed response')
    
    def _sign_params(self, params):
        """
        Given a dictionary of parameters, return an MD5 hash of the `api_secret` + the API call parameters 
        alphabetized and listed as <name><value>.
        
        As described in [Flickr Authentication API](http://www.flickr.com/services/api/auth.howto.web.html).
        """
        keys = params.keys()
        keys.sort()
        signature = '{0}{1}'.format(self.api_secret, ''.join(['{0}{1}'.format(key, params[key]) for key in keys]))
        return hashlib.md5(signature).hexdigest()
    
    def login_url(self, perms):
        """
        API calls that require authorization must provide an `auth_token` parameter. To 
        obtain an `auth_token`, the following must happen:
        
            1. Login through an application-unique Flickr URL
            2. Have a callback URL that accepts a `frob` GET query parameter
            3. Call `flickr.auth.getToken` with `frob` as a parameter
        
        This method returns the application-unique login URL. It has one required argument 
        `perms`, which is one of the following:
        
            * read
            * write
            * delete
            
        See [Flickr Authentication API](http://www.flickr.com/services/api/auth.howto.web.html) 
        for more on `perms` and the general authentication process.
        """
        params = {
            'api_key': self.api_key,
            'perms': perms
        }
        params.update({'api_sig': self._sign_params(params)})
        return self.auth_url.format(urllib.urlencode(params))
