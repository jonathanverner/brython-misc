"""
    Parse (most) python expressions into an AST

    Notable differences:

      - chaining bool operators, e.g. `1 <= 2 < 3` is not allowed

      - `-` immediately followed by a number is always taken to be a negative number, thus
        expressions like `10-1` are invalid

      - Slicing and indexing only works for variables, not for expressions, e.g

          `"ahoj"[0]`, `[10,20,30][-1]`, and `([a]+[b])[0]`

        are all invalid expressions.

      - Tuples are not supported at all
"""

import re

T_SPACE = 0
T_NUMBER = 1            # A number immediately preceded by '-' is a negative number, the '-' is not taken as an operator, so 10-11 is not a valid expression
T_LBRACKET = 2
T_RBRACKET = 3
T_LPAREN = 4
T_RPAREN = 5
T_DOT=6
T_COMMA=7
T_COLON=8
T_OPERATOR = 9
T_STRING = 10           # Started by " or '; there is NO distinction between backslash escaping between the two; """,''' and modifiers (e.g. r,b) not implemented"
T_IDENTIFIER = 11       # Including True, False, None, an identifier starts by alphabetical character and is followed by alphanumeric characters and/or _$
T_LBRACKET_INDEX = 12   # Bracket starting a list slice
T_LBRACKET_LIST = 13    # Bracket starting a list
T_LPAREN_FUNCTION = 14  # Parenthesis starting a function call
T_LPAREN_EXPR = 15      # Parenthesis starting a subexpression
T_EQUAL = 16
T_KEYWORD = 17          # Warning: This does not include True,False,None; these fall in the T_IDENTIFIER category, also this includes 'in' which can, in certain context, be an operator
T_UNKNOWN = 18

IDENTIFIER_INNERCHAR_RE = re.compile('[a-z_$0-9]',re.IGNORECASE)
KEYWORD_RE = re.compile('(for)[^a-z_$].*|(if)[^a-z_$].*|(in)[^a-z_$].*')
IS_NOT_RE = re.compile('^(is\s*not).*$')
match_token_res = [
    (T_SPACE,re.compile('\s.*')),
    (T_NUMBER,re.compile('-*[0-9].*')),
    (T_LBRACKET,re.compile('\[.*')),
    (T_RBRACKET,re.compile('\].*')),
    (T_LPAREN,re.compile('\(.*')),
    (T_RPAREN,re.compile('\).*')),
    (T_DOT,re.compile('\..*')),
    (T_COMMA,re.compile(',.*')),
    (T_COLON,re.compile(':.*')),
    (T_EQUAL,re.compile('=[^=].*')),
    (T_OPERATOR,re.compile('([-+*/<>%].*)|(==.*)|(!=.*)|(<=.*)|(>=.*)|(or[^a-z_$])|(and[^a-z_$])|(is[^a-z_$])|(not[^a-z_$])')),
    (T_STRING,re.compile('["\'].*')),
    (T_KEYWORD,re.compile('(for[^a-z_$])|(if[^a-z_$].*)|(in[^a-z_$].*)')),
    (T_IDENTIFIER,re.compile('[a-z_$].*',re.IGNORECASE)),
]
OP_PRIORITY = {
    '(':-1,    # Parenthesis have lowest priority so that we always stop partial evaluation when
               # reaching a parenthesis
    '==':0,
    'and':0,
    'or':0,
    'is':0,
    'is not':0,
    'in':0,
    'not':1,   # not has higher priority then other boolean operations so that 'a and not b' is interpreted as 'a and (not b)'
    '+':2,
    '-':2,
    '*':3,
    '/':3,
    '//':3,
    '%':3,
    '**':4,
    '.':5      # Attribute access has highest priority (e.g. a.c**2 is not a.(c**2))
}

def token_type(start_chars):
    """ Identifies the next token type based on the
        next four characters """
    for tp,pat in match_token_res:
        if pat.match(start_chars):
            return tp
    return T_UNKNOWN

def parse_number(expr,pos):
    """ Parses a number """
    if expr[pos] == '-':
        negative=True
        pos = pos + 1
    else:
        negative = False
    ret = int(expr[pos])
    pos = pos + 1
    decimal_part = True
    div = 10
    while pos < len(expr) and ((expr[pos] in ['0','1','2','3','4','5','6','7','8','9']) or ( decimal_part and expr[pos]=='.' )):
        if expr[pos] == '.':
            decimal_part = False
        else:
            if decimal_part:
                ret *= 10
                ret += int(expr[pos])
            else:
                ret += int(expr[pos])/div
                div = div*10
        pos = pos + 1
    if negative:
        return -ret,pos
    else:
        return ret,pos

def parse_string(expr,pos):
    """ Parses a string, properly interpretting backslashes. """
    end_quote=expr[pos]
    backslash=False
    ret = ""
    pos = pos + 1
    while pos < len(expr) and (backslash or expr[pos] != end_quote):
        if not backslash:
            if expr[pos] == '\\':
                backslash = True
            else:
                ret += expr[pos]
        else:
            if expr[pos] == '\\':
                ret += '\\'
            elif expr[pos] == '"':
                ret += '"'
            elif expr[pos] == "'":
                ret += "'"
            elif expr[pos] == "n":
                ret += "\n"
            elif expr[pos] == "r":
                ret += "\r"
            elif expr[pos] == "t":
                ret += "\t"
            backslash = False
        pos = pos + 1
    if pos >= len(expr):
        raise Exception("String is missing end quote: "+end_quote)
    return ret, pos+1

def parse_identifier(expr,pos):
    """ Parses an identifier. """
    ret = expr[pos]
    pos = pos + 1
    while pos < len(expr) and IDENTIFIER_INNERCHAR_RE.match(expr[pos]):
        ret += expr[pos]
        pos = pos + 1
    return ret, pos

def tokenize(expr):
    """ A generator which takes a string and converts it to a
        stream of tokens, yielding the triples (token, its value, next position in the string)
        one by one.  """
    pos = 0
    while pos < len(expr):
        tokentype = token_type(expr[pos:pos+4])
        if tokentype == T_SPACE:
            pos = pos + 1
            pass
        elif tokentype == T_NUMBER:
            number,pos = parse_number(expr,pos)
            yield (T_NUMBER,number,pos)
        elif tokentype == T_STRING:
            string,pos = parse_string(expr,pos)
            yield (T_STRING,string,pos)
        elif tokentype == T_IDENTIFIER:
            identifier,pos = parse_identifier(expr,pos)
            yield (T_IDENTIFIER, identifier, pos)
        elif tokentype == T_OPERATOR:
            if expr[pos] == '*' and pos+1 < len(expr) and expr[pos+1] == '*':
                yield (T_OPERATOR,'**',pos+2)
                pos = pos + 2
            elif expr[pos] == '/' and pos+1 < len(expr) and expr[pos+1] == '/':
                yield (T_OPERATOR,'//',pos+2)
                pos = pos + 2
            elif expr[pos] == '=' and pos+1 < len(expr) and expr[pos+1] == '=':
                yield (T_OPERATOR,'==',pos+2)
                pos = pos + 2
            elif expr[pos] == '<' and pos+1 < len(expr) and expr[pos+1] == '=':
                yield (T_OPERATOR,'<=',pos+2)
                pos = pos + 2
            elif expr[pos] == '>' and pos+1 < len(expr) and expr[pos+1] == '=':
                yield (T_OPERATOR,'>=',pos+2)
                pos = pos + 2
            elif expr[pos] == '!':
                yield (T_OPERATOR,'!=',pos+2)
                pos = pos + 2
            elif expr[pos] == 'o':
                yield (T_OPERATOR,'or',pos+2)
                pos = pos + 2
            elif expr[pos] == 'i':
                match = IS_NOT_RE.match(expr[pos:])
                if match:
                    yield (T_OPERATOR,'is not',pos+len(match.groups()[0]))
                    pos = pos + len(match.groups()[0])
                else:
                    yield (T_OPERATOR,'is',pos+2)
                    pos = pos + 2
            elif expr[pos] == 'a':
                yield (T_OPERATOR,'and',pos+3)
                pos = pos + 3
            elif expr[pos] == 'n':
                yield (T_OPERATOR,'not',pos+3)
                pos = pos + 3
            else:
                yield (T_OPERATOR,expr[pos],pos+1)
                pos = pos + 1
        elif tokentype == T_KEYWORD:
            match = KEYWORD_RE.match(expr[pos:pos+4])
            kwd = match.groups()[0] or match.groups()[1] or match.groups()[2]
            yield (tokentype,kwd,pos+len(kwd))
            pos = pos + len(kwd)
        else:
            yield (tokentype,expr[pos],pos+1)
            pos = pos+1

class ExpNode(object):
    """ Base class for nodes in the AST tree """

    def evaluate(self,context):
        """ Evaluates the node looking up identifiers in @context."""
        pass

class ConstNode(ExpNode):
    """ Node representing a string or number constant """
    def __init__(self,val):
        self._last_val = val

    def evaluate(self,context):
        return self._last_val

    def __repr__(self):
        return repr(self._last_val)


class IdentNode(ExpNode):
    """
            Nodes which have an identifier in them which can looked up in two different
            ways:

              -- the normal way just looks the identifier up in the provided @context

              -- if a self_obj is provided, the identifier is instead looked up as an attribute
                 of this obj

            This includes VarNode, FuncNode and AttrAccessNode.
    """
    def evaluate(self, context, self_obj=None):
        pass


class VarNode(IdentNode):
    """ Node representing an identifier or one of the predefined constants True, False, None"""
    CONSTANTS = {
        'True':True,
        'False':False,
        'None':None
    }
    def __init__(self,identifier):
        self._ident = identifier
        if self._ident in VarNode.CONSTANTS:
            self._const = True
            self._last_val = VarNode.CONSTANTS[self._ident]
        else:
            self._const = False

    def name(self):
        return self._ident

    def evaluate(self,context,self_obj=None):
        if self_obj is None:
            if not self._const:
                self._last_val = context._get(self._ident)
        else:
            return getattr(self_obj,self.name())
        return self._last_val

    def __repr__(self):
        return str(self._ident)


class FuncNode(IdentNode):
    """ Node representing a function call. """
    def __init__(self, identifier, args, kwargs):
        self._ident = identifier
        self._args = args
        self._kwargs = kwargs

    def name(self):
        return self._ident

    def evaluate(self, context, self_obj=None):
        if self_obj is None:
            func = context._get(self.name())
        else:
            func = getattr(self_obj,self.name())
        args = []
        kwargs = {}
        for a in self._args:
            args.append(a.evaluate(context))
        for a,v in self._kwargs.items():
            kwargs[a] = v.evaluate(context)
        self._last_val = func(*args,**kwargs)
        return self._last_val

    def __repr__(self):
        return str(self.name())+'('+','.join([repr(a) for a in self._args])+','.join([repr(k)+'='+repr(v) for (k,v) in self._kwargs.items()])+')'


class ListAccessNode(IdentNode):
    """ Node representing an array slice, e.g. lst[10:15] (also includes lst[1]) """
    def __init__(self,identifier,slice,start,end,step):
        self._ident = identifier
        self._start = start
        self._end = end
        self._step = step
        self._slice = slice

    def evaluate(self, context, self_obj = None):
        start,end,step = self._start,self._end,self._step
        if start is not None:
            start = start.evaluate(context)
        if end is not None:
            end = end.evaluate(context)
        if step is not None:
            step = step.evaluate(context)
        if self._slice:
            sl = slice(start, end, step)
        else:
            sl = start
        self._last_val = self._ident.evaluate(context,self_obj=None)[sl]
        return self._last_val

    def __repr__(self):
        if self._slice:
            return str(self._ident)+'['+':'.join([repr(self._start),repr(self._end or ''),repr(self._step or '')])+']'
        else:
            return str(self._ident)+'['+repr(self._start)+']'

class AttrAccessNode(IdentNode):
    """ Node representing attribute access, e.g. obj.prop """
    def __init__(self, obj, attribute):
        self._obj = obj
        self._attr = attribute

    def name(self):
        return self._obj.name()

    def evaluate(self,context, self_obj = None):
        if self_obj is None:
            obj = self._obj.evaluate(context)
        else:
            if isinstance(self._obj,VarNode):
                obj = getattr(self_obj,self._obj.name())
            else:
                obj = self._obj.evaluate(context,self_obj=self_obj)
        self._last_val = self._attr.evaluate(context,self_obj=obj)
        return self._last_val

    def __repr__(self):
        return repr(self._obj)+'.'+repr(self._attr)


class ListComprNode(ExpNode):
    """ Node representing comprehension, e.g. [ x+10 for x in lst if x//2 == 0 ] """
    def __init__(self,expr, var, lst, cond):
        self._expr = expr
        self._var = var
        self._lst = lst
        self._cond = cond

    def evaluate(self,context):
        lst = self._lst.evaluate(context)
        ret = []
        var_name = self._var.name()
        context._save(var_name)
        for elem in lst:
            context._set(var_name,elem)
            if self._cond is None or self._cond.evaluate(context):
                ret.append(self._expr.evaluate(context))

        context._restore(var_name)
        self._last_val = ret
        return self._last_val

    def __repr__(self):
        if self._cond is None:
            return '['+repr(self._expr)+' for '+repr(self._var)+' in ' + repr(self._lst) + ']'
        else:
            return '['+repr(self._expr)+' for '+repr(self._var)+' in ' + repr(self._lst) + ' if '+repr(self._cond)+']'


class ListNode(ExpNode):
    """ Node representing a list constant, e.g. [1,2,"ahoj",3,None] """
    def __init__(self,lst):
        self._lst = lst

    def evaluate(self,context):
        ret = []
        for e in self._lst:
            ret.append(e.evaluate(context))
        self._last_val = ret
        return self._last_val

    def __repr__(self):
        return repr(self._lst)


class OpNode(ExpNode):
    """ Node representing an arithmetical/boolean operation, e.g. a is None or a**5 """
    OPS = {
        '+':lambda x,y:x+y,
        '-':lambda x,y:x-y,
        '*':lambda x,y:x*y,
        '/':lambda x,y:x/y,
        '//':lambda x,y:x//y,
        '%':lambda x,y:x%y,
        '**':lambda x,y:x**y,
        '==':lambda x,y:x==y,
        '!=':lambda x,y:x!=y,
        '<':lambda x,y:x<y,
        '>':lambda x,y:x>y,
        '<=':lambda x,y:x<=y,
        '>=':lambda x,y:x>=y,
        'and':lambda x,y:x and y,
        'or':lambda x,y:x or y,
        'not':lambda y:not y,
        'is':lambda x,y:x is y,
        'in':lambda x,y:x in y,
        'is not':lambda x,y: x is not y,
    }

    def __init__(self,operator,l_exp,r_exp):
        self._opstr = operator
        self._op = OpNode.OPS[operator]
        self._larg = l_exp
        self._rarg = r_exp

    def evaluate(self,context):
        if self._opstr == 'not':
            self._last_val = self._op(self._rarg.evaluate(context))
        else:
            l = self._larg.evaluate(context)
            r = self._rarg.evaluate(context)
            self._last_val = self._op(l,r)
        return self._last_val

    def __repr__(self):
        if self._opstr == 'not':
            return '('+self._opstr+' '+repr(self._rarg)+')'
        else:
            return '('+repr(self._larg)+' '+self._opstr+' '+repr(self._rarg)+')'


def partial_eval(arg_stack,op_stack,pri=-1):
    """ Partially evaluates the stack, i.e. while the operators in @op_stack have strictly
        higher priority then @pri, they are converted to OpNodes/AttrAccessNodes with
        arguments taken from the @arg_stack. The result is always placed back on the @arg_stack"""
    while len(op_stack) > 0 and pri < OP_PRIORITY[op_stack[-1][1]]:
        token,op = op_stack.pop()
        ar = arg_stack.pop()
        if op == 'not':
            al = None
        else:
            al=arg_stack.pop()
        if op == '.':
            arg_stack.append(AttrAccessNode(al,ar))
        else:
            arg_stack.append(OpNode(op,al,ar))

def parse_args(token_stream):
    """ Parses function arguments from the stream and returns them as a pair (args,kwargs)
        where the first is a list and the second a dict """
    args = []
    kwargs = {}
    state = 'args'
    while state == 'args':
        arg, endt, pos = _parse(token_stream,[T_COMMA,T_EQUAL,T_RPAREN])
        if endt == T_EQUAL:
            state = 'kwargs'
        elif endt == T_RPAREN:
            args.append(arg)
            return args, kwargs
        else:
            args.append(arg)
    val, endt, pos = _parse(token_stream,[T_COMMA,T_RPAREN])
    kwargs[arg._ident]=val
    while endt != T_RPAREN:
        arg,endt,pos = _parse(token_stream,[T_EQUAL])
        val,endt,pos = _parse(token_stream,[T_COMMA,T_RPAREN])
        kwargs[arg._ident] = val
    return args, kwargs

def parse_lst(token_stream):
    """ Parses a list constant or list comprehension from the token_stream
        and returns the appropriate node """
    elem, endt, pos = _parse(token_stream,[T_RBRACKET,T_COMMA,T_KEYWORD])
    if endt == T_KEYWORD:
        expr = elem
        var, endt, pos = _parse(token_stream,[T_KEYWORD])
        lst, endt, pos = _parse(token_stream,[T_KEYWORD,T_RBRACKET])
        if endt == T_KEYWORD:
            cond, endt, pos = _parse(token_stream,[T_RBRACKET])
        else:
            cond = None
        return ListComprNode(expr,var,lst,cond)
    else:
        lst = [elem]
        while endt != T_RBRACKET:
            elem, endt, pos = _parse(token_stream,[T_RBRACKET,T_COMMA, T_KEYWORD])
            lst.append(elem)
        return ListNode(lst)

def parse_slice(token_stream):
    """ Parses a slice (e.g. a:b:c) or index from the token_stream and returns the slice as a quadruple,
        the first element of which indicates whether it is a slice (True) or an index (False)
    """
    index_s, endt, pos = _parse(token_stream,[T_COLON,T_RBRACKET])
    if endt == T_COLON:
        slice = True
        index_e, endt, pos = _parse(token_stream,[T_RBRACKET,T_COLON])
        if endt == T_COLON:
            step, endt, pos = _parse(token_stream,[T_RBRACKET])
        else:
            step = None
    else:
        slice = False
        index_e = None
        step = None
    return slice,index_s, index_e, step



def parse(expr):
    token_stream = tokenize(expr)
    ast,etok,pos = _parse(token_stream)
    return ast

def _parse(token_stream,end_tokens=[]):
    """
        Parses the token_stream, optionally stopping when an
        unconsumed token from end_tokens is found. Returns
        the parsed tree (or None if the token_stream is empty),
        the last token seen and the position corresponding to
        the next position in the source string
    """
    arg_stack = []
    op_stack = []
    for (token,val,pos) in token_stream:
        if token in end_tokens: # The token is unconsumed and in the stoplist, so we evaluate what we can and stop parsing
            partial_eval(arg_stack,op_stack)
            if len(arg_stack) == 0:
                return None, token, pos
            else:
                return arg_stack[0], token, pos
        elif token == T_IDENTIFIER:
            arg_stack.append(VarNode(val))
        elif token in [T_NUMBER, T_STRING]:
            arg_stack.append(ConstNode(val))
        elif token == T_OPERATOR or token == T_DOT or (token == T_KEYWORD and val == 'in'):
            # NOTE: '.' and 'in' are, in this context, operators.
            # If the operator has lower priority than operators on the @op_stack
            # we need to evaluate all pending operations with higher priority
            pri = OP_PRIORITY[val]
            partial_eval(arg_stack,op_stack,pri)
            op_stack.append((token,val))
        elif token == T_LBRACKET:
            # '[' can either start a list constant/comprehension, e.g. [1,2,3] or list slice, e.g. ahoj[1:10];
            #    we distinguish between the two cases by noticing that the second case needs an identifier
            #    to immediately precede it
            # FIXME: This does not allow slicing strings or expressions, e.g. "ahoj"[:-1] is invalid as is [1,2,3][0]
            if len(arg_stack)>0 and isinstance(arg_stack[-1],VarNode):
                slice,index_s, index_e, step = parse_slice(token_stream)
                ident = arg_stack.pop()
                lst_node = ListAccessNode(ident,slice,index_s,index_e,step)
            else:
                lst_node = parse_lst(token_stream)
            arg_stack.append(lst_node)
        elif token == T_LPAREN:
            # A '(' can either start a parenthesized expression or a function call.
            # We destinguish between the two cases by noticing that the second case needs an identifier
            # to immediately precede it
            # TODO: Implement Tuples
            if len(arg_stack)>0 and isinstance(arg_stack[-1],VarNode):
                args, kwargs = parse_args(token_stream)
                arg_stack.append(FuncNode(arg_stack.pop().name(),args,kwargs))
            else:
                op_stack.append((T_LPAREN_EXPR,val))
        elif token == T_RPAREN:
            partial_eval(arg_stack,op_stack)
            if op_stack[-1][0] != T_LPAREN_EXPR:
                raise "Expecting '(' at "+str(pos)
            op_stack.pop()
        else:
            raise Exception("Unexpected token "+str((token,val))+" at "+str(pos))
    partial_eval(arg_stack,op_stack)
    if len(arg_stack) > 2 or len(op_stack) > 0:
        raise Exception("Invalid expression, leftovers: args:"+str(arg_stack)+"ops:"+str(op_stack))
    return arg_stack[0],None,pos


