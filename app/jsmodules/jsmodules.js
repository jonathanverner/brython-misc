var $module=(function($B) {
    var modules = {}
    return {
        jsimport:function(name) {
            modules[name] = modules[name] || eval(name);
            return modules[name];
        },
        get:function(name) {
            return modules[name];
        }
    }
})(__BRYTHON__)