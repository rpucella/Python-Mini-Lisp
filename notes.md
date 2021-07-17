# Notes

Make this baby case sensitive? [like most languages anyway]

    class VArray(Value):
      ...
    
    register_reader('array', <values> -> (as-array (quote <values>)))
    def_primitive('array', ...)
    def_primitive('as-array', ...)
    def_primitive('array-get', ...)
    def_primitive('array-set!', ...)
    def_primitive('array-items', ...)


    class VDictionary(Value):
      ...
    
    register_reader('dict', <key/value pairs> -> (as-dict (quote <key/value pairs>)))
    def_primitive('dict', ...)
    def_primitive('as-dict', ...)
    def_primitive('dict-get', ...)
    def_primitive('dict-set!', ...)
    def_primitive('dict-items, ...)


    class VSet(Value):
      ...
    
    register_reader('set', <values> -> (as-set (quote <values>)))
    def_primitive('set', ...)
    def_primitive('set-in', ...)
    def_primitive('set-add', ...)
    def_primitive('set-remove', ...)
    def_primitive('set-items', ...)
