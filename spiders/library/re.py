from __future__ import absolute_import
from re import *
import re
from . import text
import traceback
"""Much of this library may be unnecessary if there's undiscovered built-in functionality in python"""

class CaptureException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class NoCaptureException(CaptureException):
    def __init__(self, value):
        self.value = 'Required match failed {}'.format(value)
    def __str__(self):
        return repr(self.value)

class TooManyCaptureException(CaptureException):
    def __init__(self, value):
        self.value = 'Too many matches found {}'.format(value)
    def __str__(self):
        return repr(self.value)
    
def get_last_matched_group(match):
    """ Takes a re.MatchObject, returns a string representing the last matched group
    This should be the same functionality as $+ in Perl """
    return next(s for s in reversed(match.groups()) if s)

def capture(regex, within, flags=re.I|re.S, required=True, sanitize=True, exception_info=None, allow_duplicates=False):
    regex_list = regex
    if not isinstance(regex_list, (list, tuple)):
        regex_list = [regex,]
    for i in range(0, len(regex_list)):
        last_regex = False
        if i == len(regex_list)-1:
            last_regex = True
        regex = regex_list[i]
        matches = re.findall(regex, within, flags=flags)
        if not matches:
            if not last_regex:
                continue
            if required:
                _capture_raise_exception(NoCaptureException, exception_info)
            if re.compile(regex).groups > 1:
                return [None for i in range(1, re.compile(regex).groups+1)]
            else:
                return None
        elif len(matches) > 1:
            if not allow_duplicates or not _capture_check_equality(matches, sanitize):
                _capture_raise_exception(TooManyCaptureException, exception_info)
        
        if matches:
            match_groups = matches[0]
            if sanitize:
                return _sanitized(match_groups)
            elif isinstance(match_groups, (list, tuple)):
                return [g for g in match_groups]
            else:
                return match_groups

def _sanitized(str_or_list):
    if isinstance(str_or_list, (list, tuple)):
        return [text.sanitize(g) for g in str_or_list]
    return text.sanitize(str_or_list)

def _capture_check_equality(iterator, sanitize):
    # Adapted from http://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
    try:
        iterator = iter(iterator)
        if sanitize:
            first = _sanitized(next(iterator))
            return all(first == _sanitized(rest) for rest in iterator)
        else:
            first = next(iterator)
            return all(first == rest for rest in iterator)

    except StopIteration:
        return True
def _capture_raise_exception(exception_class, exception_info):
    var_names_or_line = None
    try:
        last_line = traceback.extract_stack(limit=3)[0]
        last_line_text = last_line[3]
        last_line_number = last_line[1]
    except:
        var_names_or_line = None
    else:
        try:
            equals_match = re.search(r'\s*=', last_line_text)
            if equals_match:
                var_names_or_line = last_line_text[:equals_match.start()]
            else:
                var_names_or_line = 'line {}'.format(last_line_number)
        except:
            var_names_or_line = 'line {}'.format(last_line_number)
    if exception_info:
        raise exception_class("(%s) - Info: %s " % (var_names_or_line, exception_info))
    else:
        raise exception_class("(%s)" % (var_names_or_line))