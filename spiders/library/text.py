from __future__ import absolute_import
import re as rebasic
import HTMLParser

def normalize(string, preserve_breaks = True):
    """Takes a string, replaces all multiple spaces/breaks with one space/break"""
    
    string = rebasic.sub(r'&nbsp;?', ' ', string, flags=rebasic.I)
    string = rebasic.sub(r'\0', ' ', string)
    if preserve_breaks:
        string = rebasic.sub(r'\r\n', '\n', string)
        string = rebasic.sub(r'[\t ]+', ' ', string)
        string = rebasic.sub(r'^ +', '', string, flags=rebasic.M)
        string = rebasic.sub(r' +$', '', string, flags=rebasic.M)
        string = rebasic.sub(r'\n{2,}', '<twon>', string)
        string = rebasic.sub(r'\n+', '\n', string)
        string = rebasic.sub(r'<twon>', '\n\n', string)
    else:
        string = rebasic.sub(r'\s+', ' ', string)
    
    return string

def remove_between_tags(string, tag):
    """Takes a string and a tag type. Removes all text between open and close versions of said tag.
    E.g.
        html_source = "Hey<script>alert('yo')</script>dude"
        new_html_source = text.remove_between_tags(html_source, 'script')
        print new_html_source
        #Prints "Heydude"
    """
    string = rebasic.sub(r'<%s.*?</%s>' % (tag, tag), '', string, flags=rebasic.I|rebasic.S)
    return string

def remove_comments(string):
    """Takes a string and removes all text between <!-- and --> in the string"""
    string = rebasic.sub(r'<!--.*?-->', '', string, flags=rebasic.S)
    return string
    
def remove_tags(string, preserve_breaks = True, preserve_spacing = False):
    """Takes a string and removes tags, with the following mutually exclusive options:
    preserves_breaks - This will replace tags that normally break lines with a newline.
                    This is enabled by default.
    preserve_spacing - This will replace tags that normally break lines with a space.
                    This is disabled by default.
                    
    Enabling both preserve_breaks and preserve_spacing will only use preserve_breaks.
    Disabling both preserve_breaks and preserve_spacing will cause line-breaking tags to be removed.
    
    E.g.:
        string = "hey man<br>good to hear from you"
        print text.remove_tags(string) #same as text.remove_tags(string, preserve_breaks = True)
        #prints "hey man
        #good to hear from you"
        print text.remove_tags(string, preserve_spacing = True) #Both enabled, doesn't change
        #prints "hey man
        #good to hear from you"
        print text.remove_tags(string, preserve_breaks = False, preserve_spacing = True)
        #prints "hey man good to hear from you"
        print text.remove_tags(string, preserve_breaks = False, preserve_spacing = False)
        #prints "hey mangood to hear from you"
        
    """
    if preserve_breaks or preserve_spacing:
        string = remove_between_tags(string, "applet");
        string = remove_between_tags(string, "button");
        string = remove_between_tags(string, "iframe");
        string = remove_between_tags(string, "noframes");
        string = remove_between_tags(string, "noscript");
        string = remove_between_tags(string, "script");
        string = remove_between_tags(string, "select");
        string = remove_between_tags(string, "style");
        string = remove_between_tags(string, "title");
        
        if preserve_breaks:
            string = rebasic.sub(r'''<(?:address|blockquote|br|center|dir|div|dl|dt|fieldset|form|h\d|hr|li|menu|ol|p|pre|textarea|tr|ul|caption|col|colgroup|table|iframe|noframes|noscript|script|select|style|title)[^><]*?>''', '\r\n', string, flags=rebasic.I)
            string = rebasic.sub(r'''<(?:img|input|q|td|th|tbody|tfoot|thead|applet|button)[^><]*?>''', ' ', string, flags=rebasic.I)
    
        elif preserve_spacing:
            string = rebasic.sub(r'''<(?:address|blockquote|br|center|dir|div|dl|dt|fieldset|form|h\d|hr|img|input|li|menu|ol|p|pre|q|td|textarea|th|tr|ul|caption|col|colgroup|tbody|tfoot|thead|table|applet|button|iframe|noframes|noscript|script|select|style|title)[^><]*?>''',' ', string, flags=rebasic.I)
    
    string = rebasic.sub(r'<[^><]*?>', '', string)
    #string = rebasic.sub(r'''<\S{1,9}(?:[^>=]*(?:=\s*'[^']*?')*(?:=\s*"[^"]*?")*(?:=[^>\s]*?)*)*>''', '', string, flags=rebasic.I)
    return string

def trim(string):
    """ Eliminates leading and trailing spacing, including tabs/linebreaks/etc """
    string = rebasic.sub(r'^\s+|\s+$', '', string)
    return string

def sanitize(string, preserve_breaks = True):
    """ Performs the following transformations on a string (typically a segment of HTML):
        1. text.remove_comments
        2. text.remove_tags
            a. If preserve_breaks is True (default True), it uses preseves_breaks = True on text.remove_tags
            a. If preserve_breaks is False, it uses preseves_breaks = False but preserve_spacing = True on text.remove_tags
        3. text.normalize
        4. text.trim
    """
    if not string:
        return None

    string = remove_comments(string)
    if preserve_breaks:
        string = remove_tags(string, preserve_breaks = True)
    else:
        string = remove_tags(string, preserve_breaks = False, preserve_spacing = True)

    string = normalize(string, preserve_breaks)

    string = trim(string)

    return string
    
def _decode_entities_help(m):
    character_code = int(m.group(1))
    #Will not decode emoji
    if character_code > 65535:
        return '&#{};'.format(character_code)
    return unichr(character_code)

def decode_entities(string, charset='utf-8'):
    if string is not None:
        if isinstance(string, unicode):
            string = rebasic.sub('&(?:amp;)+', '&', string, flags=rebasic.I)
            xed_re = rebasic.compile(r'&#(\d+);?')
            string = HTMLParser.HTMLParser().unescape(string )            
            string = xed_re.sub(_decode_entities_help, string)
        else:
            u = unicode(string, charset)
            u = rebasic.sub('&(?:amp;)+', '&', u, flags=rebasic.I)
            xed_re = rebasic.compile(r'&#(\d+);?')
            u = HTMLParser.HTMLParser().unescape(u)
            u = xed_re.sub(_decode_entities_help, u)
            string = u.encode(charset)
    return string

#################
#Emoji handling
def _replace_emoji_placeholders_in_match(m, placeholder_string='[emoji:{}]'):
    character_code = int(m.group(1))
    #Will not decode emoji
    if character_code > 128000:
        return placeholder_string.format(character_code)
    return m.group(0)

def _remove_emoji_from_match(m):
    return _replace_emoji_placeholders_in_match(m, placeholder_string='')

def _replace_emoji_entities(ustring):
    emojis = rebasic.findall(u'([\uD800-\uDBFF][\uDC00-\uDFFF])', ustring)
    for emoji in emojis:
        if len(emoji) != 2:
            continue
        ord_emoji = 0x10000 + (ord(emoji[0]) - 0xD800) * 0x400 + (ord(emoji[1]) - 0xDC00)
        ustring = rebasic.sub(emoji, '&#%s;' % ord_emoji, ustring)
    return ustring

def _clean_emoji_help(ustring, as_entities=False, remove=False):
    ustring = _replace_emoji_entities(ustring)
    if not as_entities:
        xed_re = rebasic.compile(r'&#(\d+);?')
        if remove:
            ustring = xed_re.sub(_remove_emoji_from_match, ustring)
        else:
            ustring = xed_re.sub(_replace_emoji_placeholders_in_match, ustring)
    return ustring

def clean_emoji(string, as_entities=False, remove=False, charset='utf-8'):
    if string is not None:
        if isinstance(string, unicode):
            string = _clean_emoji_help(string, as_entities=as_entities, remove=remove)
        else:
            u = unicode(string, charset)
            u = _clean_emoji_help(u, as_entities=as_entities, remove=remove)
            string = u.encode(charset)
    return string
#End Emoji handling
#################

