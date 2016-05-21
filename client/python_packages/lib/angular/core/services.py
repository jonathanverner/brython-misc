class Service:
    pass

class ServiceFactory:
    SERVICES = {}

    @classmethod
    def get_service(cls, svc_cls):
        if svc_cls not in cls.SERVICES:
            cls.SERVICES[svc_cls] = svc_cls()
        return cls.SERVICES[svc_cls]