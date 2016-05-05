class JSDict():
    def __init__(self,data):
        for (k,v) in data.items():
            self.__setattr__(k,v)
        del self.__class__
    