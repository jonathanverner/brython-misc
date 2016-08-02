import json, inspect

class ObjectEncoder(json.JSONEncoder):
    """ A general purpose JSON Object Encoder from
        tobigue @stackoverflow:

        http://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
    """
    def default(self, obj):
        if hasattr(obj, "__json__"):
            return self.default(obj.__json__())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
                and not isinstance(value,set)
            )
            return self.default(d)
        return obj

def to_json(obj):
    return json.dumps(obj,cls=ObjectEncoder,sort_keys=True)