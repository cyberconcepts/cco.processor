#
# cco.processor.storage
#

from logging import getLogger
from zope.traversing.api import getName

from loops.common import adapted, baseObject
from loops.concept import Concept
from loops.setup import addAndConfigureObject

from cco.processor.common import Error, _invalid

logger = getLogger('cco.processor.storage')


# access to persistent objects

def create_or_update_object(context, type_name, data):
    obj = get_object(context, type_name, data)
    if obj is None:
        return create_object(context, type_name, data)
    else:
        return update_object(obj, data)

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

