#
# cco.processor.transformer
#

"""
Transform a data structure (represented by a dictionary )
"""

from logging import getLogger
import traceback

from cco.processor.base import Error, error, _invalid, _not_found

logger = getLogger('cco.processor.transformer')



def transform(sdata, fmap, context=None):
    tdata = {}
    for tname, spec in fmap.items():
        if isinstance(spec, str):
            sname, modif = spec, None
        else:
            sname, modif = spec
        if sname is None:
            if modif is None:
                tdata[tname] = None
                continue
            svalue = sdata # modif will extract values!
        else:
            svalue = sdata.get(sname, _not_found)
            if svalue is _not_found:
                tdata[tname] = error('transform: not found: %s' % sname)
                continue
        if modif is None:
            tvalue = svalue
        else:
            tvalue = modify_value(modif, svalue, context)
        tdata[tname] = tvalue
    return tdata

def modify_value(fct, value, context=None):
    try:
        return fct(value, context)
    except TypeError:
        try:
            return fct(value)
        except:
            tb = traceback.format_exc()
            return error('modify_value: %s, %s\n%s' % (fct, value, tb))

# predefined modifiers

def map_value(map):
    def do_map(key):
        v = map.get(key, _not_found)
        if v is _not_found:
            v = map.get('*', _not_found)
            if v is _not_found:
                return error('map_value: not found: %s' % key)
        return v
    return do_map

def const(val):
    return lambda x: val

def int_inv(val):
    if isinstance(val, basestring) and val == '':
        return _invalid
    return int(val)

def float_inv(val):
    if isinstance(val, basestring) and val == '':
        return _invalid
    return float(val)

