var $module=(function($B) {
    var bind = function(obj,method) {
        return function() {
            var args = Array.from(arguments);
            args.unshift(obj)
            method.apply(this,args);
        }
    }
    return {
        pyobj2js:function(obj) {
            for(m in obj.__class__.$methods) {
                obj[m] = bind(obj, obj.__class__[m]);
            }
            return obj
        }
    }
})(__BRYTHON__)