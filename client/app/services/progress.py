from lib.angular.core import Service
from lib.angular.core import JSDict
from lib.events import EventMixin

from lib.logger import Logger
logger = Logger(__name__)

class Task(EventMixin):
    _NEXT_TASK_ID = 0

    def __init__(self, name='', description='', clear_on_done=True):
        super(Task,self).__init__()
        self.id = Task._NEXT_TASK_ID
        Task._NEXT_TASK_ID += 1
        self.name = name
        self.description = description

    def set_progress(self, progress):
        self.progress = progress
        if self.progress == 100:
            self.emit('done',self)

class ProgressService(Service):

    def __init__(self):
        super(ProgressService,self).__init__()
        self.tasks = {}
        self.empty_task = Task()
        self.main_task = self.empty_task

    def add_task(self, name, description, clear_on_done=True):
        task =  Task(name, description)
        self.tasks[task.id] = task
        if self.main_task == self.empty_task:
            self.main_task = task
        if clear_on_done:
            task.bind('done',self.clear_task)
        return task

    def get_task(self,id):
        return self.tasks[id]

    def clear_task(self,task):
        if self.main_task == task:
            self.main_task = self.empty_task
        del self.tasks[task.id]
        task.unbind('done',self.clear_task)

    def set_main_task(self,task):
        self.main_task = task

