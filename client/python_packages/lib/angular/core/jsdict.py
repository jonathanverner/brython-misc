class JSDict():
    def __init__(self,data):
        for (k,v) in data.items():
            self.__setattr__(k,v)
        del self.__class__


class dct:

    def items(self):
        for k in self.__keys:
            yield getattr(self,k)

    def keys(self):
        return self.__keys

    def __repr__(self):
        lst = []
        for k in self.__keys:
            lst.append(repr(k)+":"+repr(getattr(self,k)))
        return "{"+",".join(lst)+"}"
        #return "{"+",".join([ "'"+k+"':'"+repr(getattr(self,k))+"'" for k in self.__keys])+"}"

def dict_to_obj(data):
    if type(data) == dict:
        ret = dct()
        ret.__keys = []
        for (k,v) in data.items():
            ret.__setattr__(k,dict_to_obj(v))
            ret.__keys.append(k)
    elif type(data) == tuple:
        ret = []
        for item in data:
            ret.append(dict_to_obj(item))
        ret = tuple(ret)
    elif type(data) == list:
        ret = []
        for item in data:
            ret.append(dict_to_obj(item))
    else:
        ret = data
    return ret



    