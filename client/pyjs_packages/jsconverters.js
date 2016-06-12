var $module=(function($B) {
    var bind = function(obj,method) {
        return function() {
            var args = Array.from(arguments);
            args.unshift(obj)
            return method.apply(this,args);
        }
    }
    var defineProperty = function(obj,property) {
        if (obj.__class__[property].fget) {
            obj.__defineGetter__(property, function() { 
                return obj.__class__[property].fget(obj)
            });
        }
        if (obj.__class__[property].fset) {
            obj.__defineSetter__(property, function(val) {
                return obj.__class__[property].fset(obj,val)
            });
        }
        if (obj.__class__[property].fdel) {
            obj.__defineDeleter__(property, function() {
                return obj.__class__[property].fdel(obj)
            });
        }
    }
    var copyPrototype = function(obj) { 
        for( m in obj.prototype ) { 
            if (m[0] !== '_') { 
                obj[m] = obj.prototype[m];
            }
        }
    }
    return {
        pyobj2js:function(obj) {
            if (obj.__class__) {
                for(m in obj.__class__.$methods) {
                    obj[m] = bind(obj, obj.__class__[m]);
                }
                for(p in obj.__class__) {
                    prop = obj.__class__[p]
                    if (prop && prop.__class__ && prop.__class__.__name__ == "property") {
                        defineProperty(obj,p)
                    }
                }
            }
//             copyPrototype(obj);
            return obj
        }
    }
})(__BRYTHON__)