import urllib2
import urllib
import os.path
import cookielib
import time
import random
from library import text, re
import urlparse

UNRESERVED_SET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    + "0123456789-._~")


def unquote_unreserved(uri):
    """Un-escape any percent-escape sequences in a URI that are unreserved
    characters.
    This leaves all reserved, illegal and non-ASCII bytes encoded.
    """
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2:
            try:
                c = chr(int(h, 16))
                if c in UNRESERVED_SET:
                    parts[i] = c + parts[i][2:]
                else:
                    parts[i] = '%' + parts[i]
            except ValueError:
                parts[i] = '%' + parts[i]
        else:
            parts[i] = '%' + parts[i]
    return ''.join(parts)


def requote_uri(uri):
    """Re-quote the given URI.

    This function passes the given URI through an unquote/quote cycle to
    ensure that it is fully and consistently quoted.
    """
    # Unquote only the unreserved characters
    # Then quote only illegal characters (do not quote reserved, unreserved,
    # or '%')
    return urllib.quote(unquote_unreserved(uri), safe="-!#$%&'()*+,/:;=?@[]~")

class Request(urllib2.Request):
    """Wrapper for urllib2 Request()
    See: http://docs.python.org/library/urllib2.html"""

    def __init__(self, *args, **kwargs):
        urllib2.Request.__init__(self, *args, **kwargs)

class EncodeFixHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        newurl = None
        if 'Location' in headers:
            newurl = headers['Location']
        elif 'uri' in headers:
            newurl = headers['uri']
        if newurl:
            newurl = urlparse.urljoin(req.get_full_url(), requote_uri(headers['Location']))
            headers['Location'] = newurl
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

def reset_cookies(cookie_jar_file_path):
    """Pass it a cookie jar file path, and it deletes it if it exists"""
    if os.path.isfile(cookie_jar_file_path):
        try:
            os.remove(cookie_jar_file_path)
        except:
            raise NotImplementedError("Could not reset cookies")
    
def get(request, use_proxy = False, use_cookies = False, proxy_address = None, cookie_jar_file_path = None, timeout = 180):
    """Pass it a web.Request object, along with options.
    It returns a response object. """
    if request.__class__ is not Request:
        print "class not right"
        raise NotImplementedError("Class must be web.Request, not %s" % request.__class__)
    
    redirect_handler = EncodeFixHTTPRedirectHandler()
    cookie_handler = None
    if use_cookies == True:
        if not cookie_jar_file_path:
            cookie_jar_file_path = str(time.time()) + str(random.random()) + '.lwp'
            
        cj = cookielib.LWPCookieJar()
        
        if os.path.isfile(cookie_jar_file_path):
            cj.load(cookie_jar_file_path, ignore_discard=True, ignore_expires=True)
        else:
            try:
                cookie_dir = os.path.dirname(cookie_jar_file_path)
                os.makedirs(cookie_dir)
            except OSError:
                pass
    
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
    
    proxy_handler = False
    if use_proxy == True:
        if not proxy_address:
            raise NotImplementedError("Requires proxy address")
            
        proxy_handler = urllib2.ProxyHandler({"http" : proxy_address, "https" : proxy_address})
    else:
        proxy_handler = urllib2.ProxyHandler({})
        
    if cookie_handler:
        opener = urllib2.build_opener(redirect_handler, cookie_handler, proxy_handler, urllib2.HTTPHandler)
    else:
        opener = urllib2.build_opener(redirect_handler, proxy_handler, urllib2.HTTPHandler)
        
    urllib2.install_opener(opener)
    
    if not request.has_header('User-Agent') and not request.has_header('User-agent'):
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0')
        
    if not request.has_header('Accept-Encoding') and not request.has_header('Accept-encoding'):
        request.add_header('Accept-Encoding', 'gzip, deflate')

    def returnnone():
        return None
    
    response = None
    try:
        response = urllib2.urlopen(request, timeout = timeout)
        #response = None
    except urllib2.HTTPError, e:
        response = e
    except urllib2.URLError, response:
        errorcode = None
        try:
            errorcode = int(response.args[0][0])
        except:
            errorcode = 666
            
        response.code = errorcode
        response.read = returnnone
        response.info = returnnone
        response.geturl = returnnone

    
    
    if use_cookies == True:
        # Set the expiration dates for all cookies that have an expiration date specified to "2020-02-20 02:02:02Z"
        for c in cj:
            if c.expires:
                c.expires = 1582164122
        cj.save(cookie_jar_file_path, ignore_discard=True, ignore_expires=True)
    
    return response

def urlencode(string, space_as_plus=True):
    """Makes a string URL friendly.
    Note: Do not pass a whole URL to this unless you want to change all non-alphanumeric characters!"""
    
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    if space_as_plus:
        return urllib.quote_plus(string)
    else:
        return urllib.quote(string)

def urldecode(string):
    """Converts most %XX characters into their ASCII equivalents"""
    
    return urllib.unquote(string)
    
def encode_viewstate(string):
    """Viewstate cleanup"""
    
    return string.replace('+', '%2B').replace('=', '%3D').replace('/', '%2F')
    
def detect_charset(html_source):
    """Detects the character set of HTML based on the charset tag
    Returns a string representing a charset (e.g. 'utf-8')
    
    This can be used in conjunction with string.decode(charset) to normalize content.
    E.g.:
    charset = web.detect_charset(html_source)
    if charset:
        html_source = html_source.decode(charset).encode('utf-8')
    else:
        raise NotImplementedError("Unrecognized charset")
    """
    charset = None
    for match in re.finditer(r'''(?:<meta\s+http-equiv=(?:'|")?content-type(?:'|"|\s)?\s*content=[^;]*?;\s*?charset=([^"]+?)(?:;[^'"]*?)?(?:'|")\s*/?>)|(?:<meta\s+content="[^;]*?;\s*?charset=([^"]+?)(?:;[^"]*?)?"(?: http-equiv="?Content-Type"?)?\s*/?>)|(?:<meta\s+content='[^;]*?;\s*?charset=([^']+?)(?:;[^']*?)?'(?: http-equiv='?Content-Type'?)?\s*/?>)|(?:<meta\s+http-equiv="charset"\s*content="([^']+?)"\s*/?>)|(?:<\?xml[^>]*?encoding="([^"]*?)")''', html_source, flags=re.I|re.S):
        charset = re.get_last_matched_group(match)
 
    if not charset:
        for match in re.finditer(r'''(?:<[^>]*?charset=(?:'|")?([^'">]*?)(?:'|")[^>]*?>)''', html_source, flags=re.I|re.S):
            charset = re.get_last_matched_group(match)
    if charset:
        charset = re.sub(r'&.*?$', '', charset)
        charset = re.sub(r'\s\?$', '', charset)
        charset = text.sanitize(charset, False)

    if charset == '\\':
        charset = None
    
    return charset
    
    