from .factory import Service

class StatusService(Service):
    def __init__(self):
        self.status_message = 'No message'
