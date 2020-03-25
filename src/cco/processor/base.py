#
# cco.processor.base
#

from logging import getLogger
from zope.traversing.api import getName

from loops.common import adapted, baseObject
from loops.concept import Concept
from loops.setup import addAndConfigureObject

logger = getLogger('cco.processor.base')


class Error(object):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return '<Error %r>' % self.message

    __repr__ = __str__

def error(msg):
    return Error(msg)

_not_found = object()
_invalid = object()


# access to persistent objects

def create_object(context, type_name, data, includeOnly=None):
    logCreate = data.get('_log_create', True)
    ident = data.get('_identifier')
    type = adapted(context['concepts'][type_name])
    cont = type.conceptManager or 'concepts'
    name = (type.namePrefix or (type_name + '.')) + ident
    attrs = {}
    for attr, val in data.items():
        if attr.startswith('_'):
            continue
        if includeOnly is not None and attr not in includeOnly:
            continue
        if isinstance(val, Error):
            logger.warn('create_object error: %s: %s %s' % (ident, attr, val))
            return 'error'
        if val is not _invalid:
            attrs[attr] = val
    addAndConfigureObject(context[cont], Concept, name, 
            conceptType=baseObject(type), **attrs)
    if logCreate:
        logger.info('create_object %s %s: %s' % (type_name, ident, attrs))
    return 'created'

def update_object(obj, data, includeOnly=None):
    logUpdate = data.get('_log_update', True)
    ident = (data.get('_identifier') or 
                getattr(obj, 'identifier', getName(baseObject(obj))))
    changedValues = {}
    for attr, nv in data.items():
        if attr.startswith('_'):
            continue
        if includeOnly is not None and attr not in includeOnly:
            continue
        if isinstance(nv, Error):
            logger.warn('update_object error: %s: %s %s' % (ident, attr, nv))
            return 'error'
        if nv is _invalid:
            continue
        ov = getattr(obj, attr)
        if nv != ov:
            changedValues[attr] = (ov, nv)
            setattr(obj, attr, nv)
    if changedValues:
        if logUpdate:
            logger.info('update_object %s: %s' % (ident, changedValues))
        # TODO: notify(ObjectModifiedEvent())
        return 'updated'
    return None

def get_object(context, type_name, data):
    if context is None:
        logger.error('get_object %s: context not set, data: %s' % (type_name, data))
    ident = data.get('_identifier')
    if ident is None:
        logger.warn('get_object %s: _identifier missing: %s' % (type_name, data))
    type = adapted(context['concepts'][type_name])
    cont = type.conceptManager or 'concepts'
    name = (type.namePrefix or (type_name + '.')) + ident
    ob = context[cont].get(name)
    if ob:
        return adapted(ob)
    return None

