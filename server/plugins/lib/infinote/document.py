from protocol import State, Vector, Segment, Buffer, Insert, Delete, \
UndoRequest, DoRequest


class InfinoteDocument(object):

    def __init__(self, initial_text=None):
        '''
        Document helper class to make interaction with the Infinote library
        a little bit easier. Each collaboratively edited document can be
        instantiated as an InfinoteDocument
        :param str initial_text: Start this document with initial text
        '''
        self.log = []
        self._state = State()

        if initial_text is not None:
            self.try_insert([1, '', 0, str(initial_text)])

    def insert(self, params):
        '''
        try to perform an insert operation and add the operation to the log
        :param list params: [user, vector, position, text]
        '''
        segment = Segment(params[0], params[3])
        buffer = Buffer([segment])
        operation = Insert(params[2], buffer)
        request = DoRequest(params[0], Vector(params[1]), operation)
        if self._state.canExecute(request):
            self._state.execute(request)
            self.log.append(["i", tuple(params)])

    def delete(self, params):
        '''
        try to perform a delete operation and add the operation to the log
        :param list params: [user, vector, position, text_length]
        '''
        operation = Delete(params[2], params[3])
        request = DoRequest(params[0], Vector(params[1]), operation)
        if self._state.canExecute(request):
            self._state.execute(request)
            self.log.append(["d", tuple(params)])

    def undo(self, params):
        '''
        try to perform an undo operation and add the operation to the log
        :param list params: [user]
        '''
        request = UndoRequest(params[0], self._state.vector)
        if self._state.canExecute(request):
            self._state.execute(request)
            self.log.append(["u", tuple(params)])

    def sync(self):
        '''
        Synchronize a document based on it's ot-log
        '''
        for log in self.log:
            if log[0] == 'i':
                self.try_insert(log[1])
            elif log[0] == 'd':
                self.try_delete(log[1])
            elif log[0] == 'u':
                self.try_undo(log[1])

    def get_log(self, limit=None):
        """
        Get the document's ot-log
        :param int limit: Specify a limit on the amount of log-operations
        to replay on the client
        :return: tuple - The document's log of operations
        """
        if limit != None:
            if len(self.log) >= limit:
                return (limit, self.log[-limit:])
            else:
                return (limit, self.log)
        else:
            return (limit, self.log)

    def _state(self):
        '''
        Return this document's current state
        :return: tuple - The document's current state
        '''
        return (self._state.vector.toString(), self._state.buffer.toString())

    state = property(_state)
