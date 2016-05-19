This is a port of JInfinote, implemented in Python


Usage
=====

>>> from infinote.document import InfinoteDocument
>>> newdoc = InfinoteDocument('Hello world')
>>> newdoc.state
('1:1', 'Hello world')
>>> newdoc.try_delete([1,newdoc.state[0], 4, 7])
>>> newdoc.state
('1:2', 'Hell')
>>> newdoc.try_insert([2,newdoc.state[0], 4,' is the place where all cool people go'])
>>> newdoc.state
('1:2;2:1', 'Hell is the place where all cool people go')
>>> newdoc.try_delete([1,newdoc.state[0], 24, 3])
>>> newdoc.state
('1:3;2:1', 'Hell is the place where  cool people go')
>>> newdoc.try_undo([1])
>>> newdoc.state
('1:4;2:1', 'Hell is the place where all cool people go')
>>> newdoc.try_delete([1,newdoc.state[0], 24, 4])
>>> newdoc.state
('1:5;2:1', 'Hell is the place where cool people go')


