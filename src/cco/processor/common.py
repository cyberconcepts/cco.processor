#
# cco.processor.common
#

"""
Common stuff for the cco.processor package
"""


class Error(object):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return '<Error %r>' % self.message

    __repr__ = __str__

def error(msg):
    return Error(msg)

# TODO: create a class (with __repr__() method) for _not_found and _invalid

_not_found = object()
_invalid = object()


