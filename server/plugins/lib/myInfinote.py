#!/usr/bin/env python
# -*- coding:utf-8 -*-

#    A Python port of the jinfinote JavaScript implementation of the Infinote
#    Protocol
#
#    Copyright (c) 2009-2011 Simon Veith <simon@jinfinote.com>
#    Copyright (c) 2015 Jonathan Verner <jonathan.verner@matfyz.cz> (porting)
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.

class JSONSerializable:
    def toDict(self):
        ret = self.__dict__.copy()
        ret['_class']=self.__class__.__name__
        return ret

class Segment(object,JSONSerializable):
    def __init__(self, user, text):
        self.user = user
        self.text = text

    @classmethod
    def fromDict(cls, data):
        return Segment(data['user'],data['text'])

    def __str__(self):
        return self.text

    def copy(self):
        return Segment(self.user,self.text)

    def join(self,seg):
        """ Appends the text of seg to self if users match.
            Returns True if users match, False otherwise """
        if self.user == seg.user:
            self.text += seg.text
            return True
        return False

    def __getitem__(self,key):
        return Segment(self.user,self.text[key])

    def __len__(self):
        return len(self.text)

class Buffer(object,JSONSerializable):
    def __init__(self, Segments = []):
        if isinstance(Segments,Buffer):
            Segments = Segments.segments
        self.segments  = []
        self._len = 0
        for s in Segments:
            self.segments.append(s.copy())
            self._len += len(s)

    @classmethod
    def fromDict(cls, data):
        return Buffer(data['segments'])

    @classmethod
    def from_array(data):
        segments = []
        for seg in data:
            segments.push(Segment(seg['user'],seg['text']))
        return Buffer(segments)

    def compact(self):
        new_segs = []
        active_segment = self.segments[0]
        for s in self.segments[1:]:
            if len(s) == 0:
                continue
            if not active_segment.join(s):
                new_segs.append(active_segment)
                active_segment = s
        new_segs.append(active_segment)
        self.segments = new_segs

    def splice(self,start,num_remove,insert):
        seg_i,offset = self._index_to_seg(self,start)
        self._len -= num_remove
        self._len += len(insert)
        if num_remove < len(self.segments[seg_i])-offset:
            self.segments = self.segments[:seg_i] + self.segments[seg_i][:offset] + insert.segments + self.segments[seg_i][offset+num_remove:]+ self.segments[seg_i+1:]
            self.compact()
            return

        new_segs = self.segments[:seg_i]+self.segments[seg_i][:offset]
        num_remove-=(len(self.segments[seg_i])-offset)
        seg_i += 1
        while num_remove > 0 and seg_i < len(self.segments):
            if num_remove < len(self.segments[seg_i]):
                self.segments = new_segs + self.segments[seg_i][:num_remove] + insert.segments + self.segments[seg_i+1:]
                self.compact()
                return
            num_remove -= len(self.segments[seg_i])
            seg_i += 1
        self._len += num_remove
        self.segments = new_segs + insert.segments
        self.compact()

    def copy(self):
        return self[:]

    def __len__(self):
        return self._len

    def __iter__(self):
        for seg in self.segments:
            for char in seg.text:
                yield char

    def _index_to_seg(self,index,nothrow=False):
        index = self._positive_key(index,nothrow)
        cur_seg_start = 0
        cur_seg = 0
        for seg in self.segments:
            if index < cur_seg_start +len(seg):
                return (cur_seg,index-cur_seg_start)
            cur_seg_start += len(seg)
            cur_seg += 1


    def _positive_key(self,key,nothrow=False):
        lh = len(self)
        if key >= lh:
            if nothrow:
                return lh-1
            else:
                raise IndexError()
        if key < 0:
            key = lh+key
            if key < 0:
                if nothrow:
                    return 0
                else:
                    raise IndexError()
        return key


    def __getitem__(self,key):
        if type(key) == type(0):
            seg_i,offset = self._index_to_seg(key)
            return self.segments[seg_i][offset]
        elif type(key) == slice:
            if key.start is None: start = 0
            else: start = self._positive_key(key.start,nothrow=True)
            if key.stop is None: stop = len(self)
            else: stop = self._positive_key(key.stop,nothrow=True)
            if key.step is None: step = 1
            else: step = key.step
            if abs(step) != 1:
                raise NotImplementedError()
            if step < 0:
                reverse = True
                start,stop = stop,start
            else:
                reverse = False
            ret = []
            cur_seg_start = 0
            in_slice = False
            last_slice = False
            for seg in self.segments:
                if start >= cur_seg_start and start < cur_seg_start + len(seg):
                    in_slice = True
                if stop <= cur_seg_start + len(seg):
                    last_slice = True
                if in_slice:
                    csl = seg[start-cur_seg_start:stop-cur_seg_start:step]
                    if reverse:
                        ret.insert(0,csl)
                    else:
                        ret.append(csl)
                if last_slice:
                    return Buffer(ret)
                cur_seg_start = cur_seg_start + len(seg)

class ReconSegment(object,JSONSerializable):
    """ReconSegments store a range of text combined with the offset at which they are to be inserted upon restoration."""
    def __init__(self, offset,buffer):
        self.offset = offset;
        self.buffer = buffer.copy();

    @classmethod
    def fromDict(cls, data):
        return Buffer(data['offset'],data['buffer'])

class Recon(object,JSONSerializable):
    """ The Recon class is a helper class which collects the parts of a
        Delete operation that are lost during transformation. This is used to
        reconstruct the text of a remote Delete operation that was issued in a
        previous state, and thus to make such a Delete operation reversible.
        @param {Recon} [recon] Pre-initialize the Recon object with data from
        another object.
    """
    def __init__(self,recon=None):
        if recon is None:
            self.segments = []
        else:
            self.segments = recon.segments[:]

    @classmethod
    def fromDict(cls, data):
        ret = Recon()
        ret.segments = data['segments']

    def update(self, offset, buffer):
        """ Creates a new Recon object with an additional piece of text to be restored later. """
        newRecon = Recon(self)
        if isinstance(buffer,Buffer):
            newRecon.segments.append(ReconSegment(offset,buffer))
        return newRecon

    def restore(self, buffer):
        """Restores the recon data in the given buffer."""
        for seg in self.segments:
            buffer.splice(seg.offset,0,seg.buffer)


class Operation(object,JSONSerializable):
    def __init__(self):
        self.requiresCID = True
        self._op='Operation';

    @classmethod
    def fromDict(cls, data):
        return Operation()

    def apply(self, buffer):
        """ Applies the operation to the given buffer """
        pass

    def transform(self, req):
        return self.__class__()

    def mirror(self):
        return self.__class__()

    def cid(self,op):
        """ Computes the concurrency ID against another operation of the same type."""
        return self

class NoOp(Operation,JSONSerializable):
    def __init__(self):
        super(NoOp,self).__init__()
        self.requiresCID = False
        self._op = 'NoOp'

    @classmethod
    def fromDict(cls, data):
        return NoOp()

class Insert(Operation,JSONSerializable):
    def __init__(self, position, text):
        """ Instantiates a new Insert operation object.
            @class An operation that inserts a txt.Buffer at a certain offset.
            @param {Number} position The offset at which the text is to be inserted.
            @param {Buffer} text The Buffer to insert.
        """
        super(Insert,self).__init__()
        self._op='Insert'
        self.position=position
        self.text = text.copy()

    @classmethod
    def fromDict(cls, data):
        return Insert(data['position'],data['text'])

    def apply(self, buffer):
        buffer.splice(self.position,0,self.text)

    def cid(self,op):
        if self.position < op.position:
            return op
        elif self.position > op.position:
            return self

    def __len__(self):
        return len(self.text)

    def transform(self, other, cid):
        """ Transforms this Insert operation against another operation, returning the
            resulting operation as a new object.
            @param {Operation} other The operation to transform against.
            @param {Operation} [cid] The cid to take into account in the case of
            conflicts.
            @type Operation
        """
        if isinstance(other, NoOp):
            return Insert(self.position, self.text)

        if isinstance(other,Split):
                # We transform against the first component of the split operation
                # first.
                if cid == self:
                    transformFirst = self.transform(other.first,self)
                else:
                    transformFirst = self.transform(other.first,other.first)

                # The second part of the split operation is transformed against its
                # first part.
                newSecond = other.second.transform(other.first);

                if cid == self:
                    transformSecond = transformFirst.transform(newSecond,transformFirst)
                else:
                    transformSecond = transformFirst.transform(newSecond,newSecond)

                return transformSecond


        pos1 = self.position;
        str1 = self.text;
        pos2 = other.position;

        if isinstance(other, Insert):
                str2 = other.text
                if (pos1 < pos2 or (pos1 == pos2 and cid == other)):
                    return Insert(pos1, str1);
                if (pos1 > pos2 or (pos1 == pos2 and cid == self)):
                    return Insert(pos1 + len(str2), str1)

        elif isinstance(other,Delete):
                len2 = len(other)
                if pos1 >= pos2 + len2:
                    return Insert(pos1 - len2, str1)
                if pos1 < pos2:
                    return Insert(pos1, str1)
                if (pos1 >= pos2 and pos1 < pos2 + len2):
                    return Insert(pos2, str1)

    def mirror(self):
        return Delete(self.position, self.text.copy())

class Split(Operation,JSONSerializable):
    """ An operation which wraps two different operations into a single
        object. This is necessary for example in order to transform a Delete
        operation against an Insert operation which falls into the range that is
        to be deleted.
    """
    def __init__(self,op1,op2):
        super(Split,self).__init__()
        self._op='Split'
        self.first = op1
        self.second = op2

    @classmethod
    def fromDict(cls, data):
        return Split(data['first'],data['second'])

    def apply(self, buffer):
        """ Applies the two components of this split operation to the given buffer
            sequentially. The second component is implicitly transformed against the
            first one in order to do so.
            @param {Buffer} buffer The buffer to which this operation is to be applied.
        """
        self.first.apply(buffer)
        transformedSecond = self.second.transform(self.first)
        transformedSecond.apply(buffer)

    def transform(self, other, cid = None):
        """ Transforms this Split operation against another operation. This is done
            by transforming both components individually.
            @param {Operation} other
            @param {Operation} [cid]
        """
        if cid is None:
            return Split(self.first.transform(other),
                         self.second.transform(other))
        elif cid == self:
            return Split( self.first.transform(other, self.first),
                          self.second.transform(other,self.second) )
        else:
            return Split( self.first.transform(other, other),
                          self.second.transform(other, other))

    def mirror(self):
        """ Mirrors this Split operation. This is done by transforming the second
            component against the first one, then mirroring both components
            individually.
            @type Split
        """
        newSecond = self.second.transform(self.first)
        return Split(self.first.mirror(), newSecond.mirror())

    def getAffectedString(self, buffer):
        """Returns the range of text in a buffer that this operation removes.
           NOTE: Works only for split delete operations
        """

        if not isinstance(self.first,Delete) or not isinstance(self.second.Delete):
            raise NotImplementedError()

        part1 = self.first.getAffectedString(buffer);
        part2 = self.second.getAffectedString(buffer);
        part2.splice(0,0,part1)
        return part2

class Delete(Operation,JSONSerializable):
    """ Instantiates a new Delete operation object.
        Delete operations can be reversible or not, depending on how they are
        constructed. Delete operations constructed with a txt.Buffer object know which
        text they are removing from the buffer and can therefore be mirrored,
        whereas Delete operations knowing only the amount of characters to be
        removed are non-reversible.
        @class An operation that removes a range of characters in the target
        buffer.
        @param {Number} position The offset of the first character to remove.
        @param what The data to be removed. This can be either a numeric value
        or a txt.Buffer object.
    """
    def __init__(self, position, what, recon = None):
        super(Delete,self).__init__()
        self._op = 'Delete'
        self.position = position
        self.requiresCID = False
        if isinstance(what,Buffer):
            self.what = what.copy()
        else:
            self.what = what
        if recon is not None:
            self.recon = recon
        else:
            self.recon = Recon()

    @classmethod
    def fromDict(cls, data):
        return Delete(data['position'],data['what'],data['recon'])

    def copy(self):
        return Delete(self.position, self.what, self.recon)

    def apply(self,buffer):
        buffer.splice(self.position,len(self))

    def transform(self, other, cid = None):
        """Transforms this Delete operation against another operation."""

        if isinstance(other,NoOp):
            return self.copy()

        if isinstance(other,Split):
                # We transform against the first component of the split operation
                # first.
                if cid == self:
                    transformFirst = self.transform(other.first,self)
                else:
                    transformFirst = self.transform(other.first,other.first)

                # The second part of the split operation is transformed against its
                # first part.
                newSecond = other.second.transform(other.first);

                if cid == self:
                    transformSecond = transformFirst.transform(newSecond,transformFirst)
                else:
                    transformSecond = transformFirst.transform(newSecond,newSecond)

                return transformSecond;


        pos1 = self.position;
        len1 = len(self)

        pos2 = other.position;
        len2 = len(other)

        if isinstance(other, Insert):
            if pos2 >= pos1 + len1:
                return Delete(pos1, self.what, self.recon)
            if pos2 <= pos1:
                return Delete(pos1 + len2, self.what, self.recon)
            else:
                result = self.split(pos2 - pos1)
                result.second.position += len2
                return result

        if isinstance(other, Delete):

            if pos1 + len1 <= pos2:
                return Delete(pos1, self.what, self.recon)

            if pos1 >= pos2 + len2:
                return Delete(pos1 - len2, self.what, self.recon)

            if pos2 <= pos1 and pos2 + len2 >= pos1 + len1:
                #     1XXXXX|
                # 2-------------|
                #
                # This operation falls completely within the range of another,
                # i.e. all data has already been removed. The resulting
                # operation removes nothing.

                if self.isReversible():
                    newData = Buffer()
                else:
                    newData = 0
                newRecon = self.recon.update(0, other.what.slice(pos1 - pos2, pos1 - pos2 + len1))
                return Delete(pos2, newData, newRecon)

            if pos2 <= pos1 and pos2 + len2 < pos1 + len1:
                #     1XXXX----|
                # 2--------|
                #
                # The first part of self operation falls within the range of another.

                result = self.split(pos2 + len2 - pos1)
                result.second.position = pos2
                result.second.recon = self.recon.update(0, other.what.slice(pos1 - pos2))
                return result.second

            if pos2 > pos1 and pos2 + len2 >= pos1 + len1:
                # 1----XXXXX|
                #     2--------|
                #
                # The second part of self operation falls within the range of another.
                result = self.split(pos2 - pos1);
                result.first.recon = self.recon.update(len(result.first), other.what.slice(0, pos1 + len1 - pos2))
                return result.first

            if pos2 > pos1 and pos2 + len2 < pos1 + len1:
                # 1-----XXXXXX---|
                #      2------|
                #
                # Another operation falls completely within the range of self
                # operation. We remove that part.


                # We split self operation two times: first at the beginning of
                # the second operation, then at the end of the second operation.
                r1 = self.split(pos2 - pos1)
                r2 = r1.second.split(len2)

                # The resulting Delete operation consists of the first and the
                # last part, which are merged back into a single operation.
                result = r1.first.merge(r2.second)
                result.recon = self.recon.update(pos2 - pos1, other.what)
                return result

    def mirror(self):
        """ Mirrors this Delete operation. Returns an operation which inserts the text
            that this Delete operation would remove. If this Delete operation is not
            reversible, the return value is None.
            @type Operations.Insert
        """
        if self.isReversible():
            return Insert(self.position, self.what.copy())

    def split(self,at):
        """ Splits self Delete operation into two Delete operations at the given
            offset. The resulting Split operation will consist of two Delete
            operations which, when combined, affect the same range of text as the
            original Delete operation.
            @param {Number} at Offset at which to split the Delete operation.
            @type Operations.Split
        """
        if self.isReversible():
            # This is a reversible Delete operation. No need to to any
            # processing for recon data.
            return Split(Delete(self.position, self.what.slice(0, at)),
                         Delete(self.position + at, self.what.slice(at)));

        # This is a non-reversible Delete operation that might carry recon
        # data. We need to split that data accordingly between the two new
        # components.
        recon1 = Recon();
        recon2 = Recon();
        for seg in self.recon.segments:
            if seg.offset < at:
                recon1.segments.push(seg)
            else:
                recon2.segments.push( ReconSegment(seg.offset-at,seg.buffer))

        return Split(Delete(self.position, at, recon1),
                     Delete(self.position + at, self.what - at, recon2))

    def isReversible(self):
        return isinstance(self.what,Buffer)

    def makeReversible(self, transformed, state):
        """ Makes this Delete operation reversible, given a transformed version of
            this operation in a buffer matching its state. If this Delete operation is
            already reversible, this function simply returns a copy of it.
            @param {Operations.Delete} transformed A transformed version of this operation.
            @param {State} state The state in which the transformed operation could be applied.
        """
        if self.isReversible():
            return self.copy()
        return Delete(self.position,self.getAffectedString(transformed,state.buffer))

    def getAffectedString(self, buffer):
        """Returns the range of text in a buffer that this Delete operation removes."""

        # In the process of determining the affected string, we also
        # have to take into account the data that has been "transformed away"
        # from the Delete operation and which is stored in the Recon object.
        reconBuffer = buffer.slice(self.position, self.position + len(self))
        self.recon.restore(reconBuffer)
        return reconBuffer

    def merge(self,other):
        """ Merges a Delete operation with another one. The resulting Delete operation
            removes the same range of text as the two separate Delete operations would
            when executed sequentially.
            @param {Delete} other
            @type Delete
        """
        if self.isReversible():
            if not other.isReversible():
                raise Exception("Cannot merge reversible operations with non-reversible ones")
                newBuffer = self.what.copy()
                newBuffer.splice(len(newBuffer), 0, other.what)
                return Delete(self.position, newBuffer)
        else:
            newLength = len(self) + len(other)
            return Delete(self.position, newLength)

    def __len__(self):
        if isinstance(self.what,Buffer):
            return len(self.what)
        return self.what


class Request(object,JSONSerializable):
    def __init__(self, user, vector):
        self.user = user
        self.vector = vector;
        self._req='Request'

    def copy(self):
        return Request(self.user,self.vector)

    @classmethod
    def fromDict(cls, data):
        return Request(data['user'],data['vector'])

    def mirror(self,amount=1):
        """ Mirrors the request. This inverts the operation and increases the issuer's
            component of the request time by the given amount.
            @param {Number} [amount] The amount by which the request time is
            increased. Defaults to 1.
            @type Request
        """
        return Request(self.user,Vector.increment(self.vector,self.user,amount))

    def fold(self,user,foldBy):
        """ Folds the request along another user's axis. This increases that user's
            component by the given amount, which must be a multiple of 2.
        """
        if foldBy % 2 == 1:
            raise Exception("Fold amounts must be multiples of 2.")
        ret = self.copy()
        ret.vector = Vector.increment(ret.vector,user,foldBy)
        return ret

class DoRequest(Request,JSONSerializable):
    def __init__(self, user, vector, operation):
        super(DoRequest,self).__init__(user, vector)
        self.operation = operation
        self._req='DoRequest'

    @classmethod
    def fromDict(cls, data):
        return DoRequest(data['user'],data['vector'],data['operation'])

    def execute(self, state):
        self.operation.apply(state.buffer)
        state.vector = Vector.increment(state.vector,self.user, 1)
        return self

    def makeReversible(self, translated_self, state):
        """ Makes a request reversible, given a translated version of this request
            and a State object. This only applies to requests carrying a Delete
            operation; for all others, this does nothing.
            @param {DoRequest} translated_self This request translated to the given state
            @param {State} state The state which is used to make the request
            reversible.
        """
        result = self.copy()
        if isinstance(self.operation, Delete):
            result.operation = self.operation.makeReversible(translated_self.operation,state)

        return result

    def mirror(self, amount):
        return DoRequest(self.user,Vector.increment(self.vector,self.user,amount),self.operation.mirror())

    def copy(self):
        return DoRequest(self.user,self.vector,self.operation)

    def transform(self, req, cid):
        """ Transforms this request against another request.
            @param {DoRequest} req
            @param {DoRequest} [cid] The concurrency ID of the two requests. This is
            the request that is to be transformed in case of conflicting operations.
            @type DoRequest
        """
        if isinstance(self.operation, NoOp):
            newOperation = NoOp()
        else:
            if cid == self:
                op_cid = self.operation
            else:
                op_cid = req.operation
            newOperation = self.operation.transform(req.operation, op_cid)

        return DoRequest(self.user, Vector.increment(self.vector,req.user),newOperation)

class HistoryRequest(Request,JSONSerializable):
    def __init__(self,user,vector):
        self.user = user
        self.vector = vector
        self._req='HistoryRequest'
        pass

    @classmethod
    def fromDict(cls, data):
        return HistoryRequest(data['user'],data['vector'])

    def associatedRequest(self,log):
        """ Finds the corresponding DoRequest to this HistoryRequest.
            @param {Array} log The log to search
        """
        sequence = 1
        index = log.find(self)
        if index == -1:
            index = len(log)-1

        while index >=0:
            req = log[index]
            index = index - 1

            if req is self or req.user != self.user or req.vector.get(self.user,0) > self.vector.get[self.user]:
                continue

            if isinstance(req, self.__class__):
                sequence += 1
            else:
                sequence -= 1

            if sequence == 0:
                return req

class UndoRequest(HistoryRequest,JSONSerializable):
    def __init__(self,user,vector):
        super(UndoRequest,self).__init__(user, vector)
        self._req='UndoRequest'

    @classmethod
    def fromDict(cls, data):
        return UndoRequest(data['user'],data['vector'])

    def copy(self):
        return UndoRequest(self.user,self.vector)

class RedoRequest(HistoryRequest,JSONSerializable):
    def __init__(self,user,vector):
        super(RedoRequest,self).__init__(user, vector)
        self._req='RedoRequest'
        pass

    @classmethod
    def fromDict(cls, data):
        return RedoRequest(data['user'],data['vector'])

    def copy(self):
        return RedoRequest(self.user,self.vector)


class Vector(object,JSONSerializable):
    def __init__(self,data):
        self._components = {}
        if type(data) == dict:
            self._components = data.copy()
        if isinstance(data,Vector):
            self._components = data._components.copy()

    @classmethod
    def fromDict(cls, data):
        return Vector(data['_components'])

    def __str__(self):
        return [str(k)+':'+str(v) for (k,v) in sorted(self._components.items()) if v > 0]

    def __getitem__(self,k):
        return self._components[k]

    def __setitem__(self, key, value):
        self._components[key] = value

    def __iter__(self):
        return self._components.__iter__()

    def get(self, k, default):
        return self._components.get(k,default)

    def items(self):
        return self._components.items()

    def copy(self):
        return Vector(self)

    @staticmethod
    def increment(vec,user,by=1):
        """ Returns a new vector with a specific component increased by a given amount. """
        ret = Vector(vec)
        ret[user] = vec.get(user,0)+by
        return ret

    @staticmethod
    def sup(v1,v2):
        """ Calculates the supremum (least common successor) of two vectors """
        ret = Vector(v1)
        for (k,v) in v2.items():
            ret[k] = max(v1.get(k,0),v)
        return ret

    @staticmethod
    def leastCommonSuccessor(v1,v2):return Vector.sup(v1,v2)

    def __add__(self, other):
        ret = Vector(self._components)
        for (u,v) in other.items():
            ret[u] = self.get(u,0) + v
        return ret

    def causallyBefore(self, other): return self <= other

    def __le__(self, other):
        for k in other:
            if k in self and self[k] > other[k]:
                return False
        return True

    def __eq__(self, other):
        for (k,v) in other.items():
            if self.get(k,v) != v: return False
        for (k,v) in self.items():
            if other.get(k,v) != v: return False
        return True

class State(object,JSONSerializable):
    """ Stores and manipulates the state of a document by keeping track of
        its state vector, content and history of executed requests.
        @param {Buffer} [buf] Pre-initialize the buffer
        @param {Vector} [vec] Set the initial state vector
    """
    def __init__(self, buf = None, vec = None):
        self.buffer = Buffer(buf)
        self.vector = Vector(vec)
        self.request_queue=[]
        self.log = []
        self.cache = {}

    @classmethod
    def fromDict(cls, data):
        s = State(data['buffer'],data['vector'])
        s.log = data['log']
        return s

    def toDict(self):
        return {
                '_class':'State',
                'buffer':self.buffer,
                'vector':self.vector,
                'log':self.log
        }

    def queue(self, request):
        """ Adds a request to the requst queue """
        self.request_queue.append(request)

    def canExecute(self, request):
        """ Checks whether a given request can be executed in the current state. """
        if isinstance(request,HistoryRequest):
            return request.associatedRequest(self.log) is not None
        else:
            return (request.vector <= self.vector)

    def execute(self, request=None):
        """ Executes a request that is executable.
            @param {Request} [request] The request to be executed. If omitted, an
            executable request is picked from the request queue instead.
            @returns The request that has been executed, or None if no request
            has been executed.
        """
        if request is None:
            # Pick an executable request from the queue.
            for i in range(self.request_queue):
                request = self.request_queue[i]
                if self.canExecute(self.request_queue[i]):
                    del self.request_queue[i]
                    break

        if not self.canExecute(request):
            # Not executable yet - put it (back) in the queue.
            if request is not None:
                self.queue(request)
                return None

        if request.vector[request.user] < self.vector.get(request.user,-1):
            # If the request has already been executed, skip it, but record it into the log.
            # FIXME: this assumes the received request is already reversible
            self.log.push(request)
            return None

        request = request.copy()

        if isinstance(request,HistoryRequest):
            # For undo and redo requests, we change their vector to the vector
            # of the original request, but leave the issuing user's component
            # untouched.
            assocReq = request.associatedRequest(self.log)
            newVector = Vector(assocReq.vector)
            newVector[request.user] = request.vector[request.user]
            request.vector = newVector

        translated = self.translate(request, self.vector)

        if isinstance(request, DoRequest) and isinstance(request.operation,Delete):
            # Since each request might have to be mirrored at some point, it
            # needs to be reversible. Delete requests are not reversible by
            # default, but we can make them reversible.
            self.log.push(request.makeReversible(translated, self))
        else:
            self.log.push(request)

        translated.execute(self)

        if callable(self.onexecute):
                self.onexecute(translated)

        return translated

    def executeAll(self):
        """ Executes all queued requests that are ready for execution. """
        while self.execute() is not None:
            pass

    def reachable(self, vector):
        """ Determines whether a given state is reachable by translation.
            @param {Vector} vector
            @type Boolean
        """
        for (u,t) in self.vector.items():
            if not self.reachableUser(vector, u):
                return False
        return True

    def reachableUser(self,vector,user):
        n = vector[user]
        firstRequest = self.firstRequestByUser(user)
        if firstRequest is None:
             firstRequestNumber = self.vector[user]
        else:
            firstRequestNumber = firstRequest.vector[user]

        while True:
            if n == firstRequestNumber:
                return True

            r = self.requestByUser(user, n - 1)

            if r is None:
                return False

            if isinstance(r, DoRequest):
                w = r.vector;
                return Vector.increment(w,r.user) <= vector
            else:
                assocReq = r.associatedRequest(self.log)
                n = assocReq.vector[user]

    def requestByUser(self,user,time):
        """ Retrieve an user's request by its index.
            @param {Number} user
            @param {Number} time The number of the request to be returned
        """
        for i in range(len(self.log)):
            if self.log[i].user == user and self.log[i].vector[user] == time:
                return self.log[i]
        return None

    def firstRequestByUser(self,user):
        """ Retrieve the first request in the log that was issued by the given user. """
        firstRequest = None
        for req in self.log:
            if req.user == user and (firstRequest is None or firstRequest.vector[user] > req.vector[user]):
                firstRequest = req
        return firstRequest

    def translate(self, request, targetVector, noCache=False):
        """ Translates a request to the given state vector.
            @param {Request} request The request to translate
            @param {Vector} targetVector The target state vector
            @param {Boolean} [nocache] Set to true to bypass the translation cache.
        """

        if isinstance(request,DoRequest) and request.vector == targetVector:
            # If the request vector is not an undo/redo request and is already
            # at the desired state, simply return the original request since
            # there is nothing to do.
            return request.copy()

        # Check the cache first
        key = str(request)+str(targetVector)
        if  not noCache:
            if not key in self.cache:
                self.cache[key] = self.translate(request,targetVector,True)
            return self.cache[key]

        if isinstance(request,HistoryRequest):
            # If we're dealing with an undo or redo request, we first try to see
            # whether a late mirror is possible. For this, we retrieve the
            # associated request to this undo/redo and see whether it can be
            # translated and then mirrored to the desired state.
            assocReq = request.associatedRequest(self.log)

            # The state we're trying to mirror at corresponds to the target
            # vector, except the component of the issuing user is changed to
            # match the one from the associated request.
            mirrorAt = targetVector.copy();
            mirrorAt[request.user] = assocReq.vector.get(request.user,0)

            if self.reachable(mirrorAt):
                translated = self.translate(assocReq, mirrorAt)
                mirrorBy = targetVector.get(request.user,0)-mirrorAt.get(request.user,0)
                mirrored = translated.mirror(mirrorBy)
                return mirrored

            # If mirrorAt is not reachable, we need to mirror earlier and then
            # perform a translation afterwards, which is attempted next.

        for user in self.vector:
            # We now iterate through all users to see how we can translate
            # the request to the desired state.


            # The request's issuing user is left out since it is not possible
            # to transform or fold a request along its own user.
            if user == request.user:
                continue

            # We can only transform against requests that have been issued
            # between the translated request's vector and the target vector.
            if targetVector.get(user,0) <= request.vector.get(user,0):
                continue

            # Fetch the last request by this user that contributed to the
            # current state vector.
            lastRequest = self.requestByUser(user, targetVector.get(user,0) - 1);

            if isinstance(lastRequest, HistoryRequest):
                # When the last request was an undo/redo request, we can try to
                # "fold" over it. By just skipping the do/undo or undo/redo pair,
                # we pretend that nothing has changed and increase the state
                # vector.

                foldBy = targetVector.get(user,0) - lastRequest.associatedRequest(self.log).vector.get(user,0)

                if targetVector.get(user,0) >= foldBy:
                    foldAt = Vector.increment(targetVector,user, -foldBy)

                    # We need to make sure that the state we're trying to
                    # fold at is reachable and that the request we're translating
                    # was issued before it.

                    if  self.reachable(foldAt) and request.vector <= foldAt:
                        translated = self.translate(request, foldAt)
                        folded = translated.fold(user, foldBy)
                        return folded

            # If folding and mirroring is not possible, we can transform this
            # request against other users' requests that have contributed to
            # the current state vector.
            transformAt = targetVector.incr(user, -1)

            if transformAt.get(user,0) >= 0 and self.reachable(transformAt):
                lastRequest = self.requestByUser(user, transformAt[user])
                r1 = self.translate(request, transformAt)
                r2 = self.translate(lastRequest, transformAt)

                if r1.operation.requiresCID:
                    # For the Insert operation, we need to check whether it is
                    # possible to determine which operation is to be transformed.
                    cid = r1.operation.cid(r2.operation)

                    if cid is None:
                        # When two requests insert text at the same position,
                        # the transformation result is undefined. We therefore
                        # need to perform some tricks to decide which request
                        # has to be transformed against which.

                        # The first try is to transform both requests to a
                        # common successor before the transformation vector.
                        lcs = Vector.sup(request.vector,lastRequest.vector);

                        if self.reachable(lcs):
                            r1t = self.translate(request, lcs)
                            r2t = self.translate(lastRequest, lcs)

                            # We try to determine the CID at this vector, which
                            # hopefully yields a result.
                            cidt = r1t.operation.cid(r2t.operation);

                            if cidt == r1t.operation: cid = r1.operation
                            elif cidt == r2t.operation: cid = r2.operation

                            if cid is None:
                                # If we arrived here, we couldn't decide for a CID,
                                # so we take the last resort: use the user ID of the
                                # requests to decide which request is to be
                                # transformed. This behavior is specified in the
                                # Infinote protocol.

                                if r1.user < r2.user: cid = r1.operation
                                else: cid = r2.operation


                    if cid == r1.operation: cid_req = r1
                    else: cid_req = r2
                    return r1.transform(r2, cid_req)

        raise Exception("Could not find a translation path")


_classes = { 'Segment':Segment, 'Buffer':Buffer, 'ReconSegment':ReconSegment, 'Recon':Recon,
             'Vector':Vector, 'State':State, 'Insert':Insert, 'Delete':Delete, 'Split':Split,
             'NoOp':NoOp, 'DoRequest':DoRequest, 'UndoRequest':UndoRequest, 'RedoRequest':RedoRequest }

def objectFromDict(data):
    if '_class' not in data:
        return data
    cls = _classes.get(data['_class'],None)
    if cls is None:
        return data
    if hasattr(cls,'fromDict'):
        return cls.fromDict(data)
    return data

def objectToDict(obj):
    if hasattr(obj,'toDict'):
        d = obj.toDict()
        ret = {}
        for (k,v) in d.items():
            ret[k] = objectToDict(v)
        return ret
    elif type(obj) == list:
        return [ objectToDict(v) for v in obj ]
    elif type(obj) == dict:
        ret = {}
        for (k,v) in obj.items():
            ret[k] = objectToDict(v)
        return ret
    return obj


import json
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,"toDict"):
            return obj.toDict()
        else:
            super(JSONEncoder,self).default(obj)