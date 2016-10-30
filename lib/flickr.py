# -*- coding: utf-8 -*-

from lib.settings import Settings
import logging
import hashlib
import urllib
import urllib2
import json
import mimetools
import os, sys
import mimetypes
import codecs
from xml.dom.minidom import parse
import datetime

class APIConstants:
    """ APIConstants class
    """

    base = "https://api.flickr.com/services/"
    rest   = base + "rest/"
    auth   = base + "auth/"
    upload = base + "upload/"
    replace = base + "replace/"

    def __init__( self ):
       """ Constructor
       """
       pass

api = APIConstants()


class Flickr:

    def __init__(self, frob = None):
        self.section_name_setting = 'flickr'
        settings = Settings()
        s = settings.get(self.section_name_setting)

        self.api_key = str(s['api_key'])
        self.secret = str(s['secret'])
        self.token = str(s['token']) or None
        self.perms = None
        self.frob = frob

        self.title = str(s['title'])
        self.description = str(s['description'])
        self.tags = str(s['tags'])
        self.is_private = str(s['is_private'])
        self.is_public = str(s['is_public'])
        self.is_family = str(s['is_family'])
        self.is_friend = str(s['is_friend'])
        self.is_power = str(s['is_power'])
        self.album_format = str(s['album_format'])

        self.timeout = 120
        
        self.log = logging.getLogger("app")

    def generateToken(self):
        if (not self.checkToken()):
            return self._authenticate()
        return True
        
    def checkToken(self):        
        if (self.token == None):
            return False
        else:
            d = {
                "auth_token"      :  self.token,
                "method"          :  "flickr.auth.checkToken",
                "format"          : "json",
                "nojsoncallback"  : "1"
            }
            sig = self._signCall(d)

            url = self._urlGen(api.rest, d, sig)
            try:
                res = self._getResponse(url)
                if (self._isGood(res)):
                    self.token = res['auth']['token']['_content']
                    self.perms = res['auth']['perms']['_content']
                    return True
                else :
                    self._reportError(res)
            except:
                self.log.info(str(sys.exc_info()))
            return False

    def _signCall(self, data):
        keys = data.keys()
        keys.sort()
        foo = ""
        for a in keys:
            foo += (a + data[a])

        f = self.secret + "api_key" + self.api_key + foo

        return hashlib.md5(f).hexdigest()

    def _urlGen(self, base, data, sig):
        data['api_key'] = self.api_key
        data['api_sig'] = sig
        encoded_url = base + "?" + urllib.urlencode( data )
        return encoded_url

    def _getResponse(self, url):
        try:
            res = urllib2.urlopen(url, timeout=self.timeout).read()
        except urllib2.HTTPError, e:
            self.log.error("Flickr Error 1: " + e.code)
        except urllib2.URLError, e:
            self.log.error("Flickr Error 2: " + e.args)
        return json.loads(res)

    def _isGood(self, res):
        if (not res == "" and res['stat'] == "ok" ):
            return True
        else :
            return False

    def _reportError(self, res):
        try:
            self.log.error("Error: " + str(res['code'] + " " + res['message']))
        except:
            self.log.error("Error: " + str(res))

    def _authenticate(self):
        self.log.info("Getting new token")
        self._getFrob()
        return self._getAuthKey()

    def _getFrob(self):
        d = {
            "method"          : "flickr.auth.getFrob",
            "format"          : "json",
            "nojsoncallback"    : "1"
            }
        sig = self._signCall(d)
        url = self._urlGen(api.rest, d, sig)
        try:
            response = self._getResponse(url)
            if (self._isGood(response)):
                self.frob = str(response["frob"]["_content"])
            else:
                self._reportError(response)
        except:
            self.log.error("Error: cannot get frob:" + str(sys.exc_info()))


    def _getAuthKey(self):
        d =  {
            "frob" : self.frob,
            "perms" : "delete"
        }
        sig = self._signCall(d)
        return {
            'frob': self.frob,
            'url': self._urlGen(api.auth, d, sig)
        }


    def authenticate_save(self):
        d = {
            "method"          : "flickr.auth.getToken",
            "frob"            : str(self.frob),
            "format"          : "json",
            "nojsoncallback"    : "1"
        }
        sig = self._signCall(d)
        url = self._urlGen(api.rest, d, sig)
        try:
            res = self._getResponse(url)
            if (self._isGood(res)):
                self.token = str(res['auth']['token']['_content'])
                self.perms = str(res['auth']['perms']['_content'])
                return self._cacheToken()
            else :
                self._reportError(res)
        except:
            self.log.error("Flickr Error 3: " + str(sys.exc_info()))

        return False

    def _cacheToken(self):
        self.log.info('save')
        try:
            settings = Settings()
            settings.set_params(self.section_name_setting, 'token', str(self.token))
            return settings.set_params(self.section_name_setting, 'frob', '')     
        except:
            self.log.error("Issue writing token to local cache ", str(sys.exc_info()))

    def isPower(self):
        if self.is_power == '1':
            return True
        return False
            
    def uploadFile(self, file):
            
        self.log.info("Uploading " + file + "...")
        if self.checkToken() is False:
            self.log.error('No authorization Flickr');
            return False

        success = False
        last_modified = os.stat(file).st_mtime;
        head, setName = os.path.split(os.path.dirname(file))
        try:
            photo = ('photo', file, open(file, 'rb').read())
            d = {
                "auth_token"    : self.token,
                "perms"         : self.perms,
                "title"         : self.title,
                "description"   : self.description,
                "tags"          : self.tags + " " + setName,
                "is_public"     : self.is_public,
                "is_friend"     : self.is_friend,
                "is_family"     : self.is_family
            }
            sig = self._signCall(d)
            d["api_sig"] = sig
            d["api_key"] = self.api_key
            url = self.build_request(api.upload, d, (photo,))
            res = parse(urllib2.urlopen(url, timeout=self.timeout))
            if (not res == "" and res.documentElement.attributes['stat'].value == "ok" ):
                self.log.info("Successfully uploaded the file: " + file)
                photo_id = int(str(res.getElementsByTagName('photoid')[0].firstChild.nodeValue))
                self.createSets(file, photo_id)
                success = True
            else :
                self.log.error("A problem occurred while attempting to upload the file: " + file)
                try:
                    self.log.error("Flickr Error 4: " + str(res.toxml()))
                except:
                    self.log.error("Flickr Error 5: " + str(res.toxml()))
        except:
            self.log.error("Flickr Error 6: " + str(sys.exc_info()))
        return success

    def build_request(self, theurl, fields, files, txheaders=None):
        """
        build_request/encode_multipart_formdata code is from www.voidspace.org.uk/atlantibots/pythonutils.html

        Given the fields to set and the files to encode it returns a fully formed urllib2.Request object.
        You can optionally pass in additional headers to encode into the opject. (Content-type and Content-length will be overridden if they are set).
        fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        """

        content_type, body = self.encode_multipart_formdata(fields, files)
        if not txheaders: txheaders = {}
        txheaders['Content-type'] = content_type
        txheaders['Content-length'] = str(len(body))

        return urllib2.Request(theurl, body, txheaders)

    def encode_multipart_formdata(self,fields, files, BOUNDARY = '-----'+mimetools.choose_boundary()+'-----'):
        """ Encodes fields and files for uploading.
        fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return (content_type, body) ready for urllib2.Request instance
        You can optionally pass in a boundary string to use or we'll let mimetools provide one.
        """
        
        CRLF = '\r\n'
        L = []
        if isinstance(fields, dict):
            fields = fields.items()
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(str(value))
        for (key, filename, value) in files:
            filetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % filetype)
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY        # XXX what if no files are encoded
        return content_type, body


    def createSets(self, file, photo_id):
        self.log.info('*****Creating Sets*****')
        setName = self.modification_date(file)
        
        fSets = self.getFlickrSets()
        issetSet = False
        for f in fSets:
            if f['setName'] == setName:
                issetSet = True
                self.addFileToSet(f['setId'], photo_id, file)

        if issetSet is False:
            setId = self.createSet(setName, photo_id)
            self.log.info("Created the set: " + setName)
            if setId:
                self.addFileToSet(setId, photo_id, file)
            
        self.log.info('*****Completed creating sets*****')

    def addFileToSet(self, setId, photo_id, file):
        try:
            d = {
                "auth_token"          : str(self.token),
                "perms"               : str(self.perms),
                "format"              : "json",
                "nojsoncallback"      : "1",
                "method"              : "flickr.photosets.addPhoto",
                "photoset_id"         : str(setId),
                "photo_id"            : str(photo_id)
            }
            sig = self._signCall(d)
            url = self._urlGen(api.rest, d, sig)

            res = self._getResponse(url)
            if (self._isGood(res)):
                self.log.info("Successfully added file " + file + " to its set.")
            else :
                self._reportError(res)
        except:
            self.log.error(str(sys.exc_info()))

    def createSet(self, setName, photo_id):
        self.log.info("Creating new set: " + str(setName))

        try:
            d = {
                "auth_token"          : str(self.token),
                "perms"               : str(self.perms),
                "format"              : "json",
                "nojsoncallback"      : "1",
                "method"              : "flickr.photosets.create",
                "primary_photo_id"    : str(photo_id),
                "title"               : setName
            }

            sig = self._signCall(d)

            url = self._urlGen(api.rest, d, sig)
            res = self._getResponse(url)
            if ( self._isGood(res)):
                return res["photoset"]["id"]
            else :
                self._reportError(res)
        except:
            self.log.error(str(sys.exc_info()))
        return False

    def modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t).strftime(self.album_format)

    def getFlickrSets(self):
        try:
            d = {
                "auth_token"          : str(self.token),
                "perms"               : str(self.perms),
                "format"              : "json",
                "nojsoncallback"      : "1",
                "method"              : "flickr.photosets.getList"
            }
            url = self._urlGen(api.rest, d, self._signCall(d))
            res = self._getResponse(url)
            ret = []
            if (self._isGood(res)):
                for row in res['photosets']['photoset']:
                    ret.append({
                        'setId': row['id'],
                        'setName': row['title']['_content'],
                        'primaryPhotoId': row['primary']
                    })
                return ret
            else:
                self._reportError(res)
        except:
            self.log.error(str(sys.exc_info()))

    def getPhotos(self, photoset_id, page):
        try:
            d = {
                "auth_token"          : str(self.token),
                "perms"               : str(self.perms),
                "photoset_id"         : str(photoset_id),
                "page"                : str(page),
                "per_page"            : "500",
                "extras"              : "url_o,last_update",
                "format"              : "json",
                "nojsoncallback"      : "1",
                "method"              : "flickr.photosets.getPhotos"
            }
            url = self._urlGen(api.rest, d, self._signCall(d))
            res = self._getResponse(url)
            if (self._isGood(res)):
                return res
            else:
                self._reportError(res)
        except:
            self.log.error(str(sys.exc_info()))


