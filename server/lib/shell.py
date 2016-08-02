import os,re
def ls(path, pattern='.*', recursive=False, relative=True,_start_match=None):
    if _start_match is None:
        _start_match = len(path)
        if not path.endswith('/'):
            _start_match += 1
    ret = []
    pattern = re.compile(pattern)
    if not os.path.isdir(path):
        return [path]
    for node in os.listdir(path):
        try:
            node_path = os.path.join(path,node)
            if pattern.match(node_path[_start_match:]):
                if os.path.isdir(node_path):
                    if relative:
                        ret.append(node_path[_start_match:]+os.path.sep)
                    else:
                        ret.append(node_path+os.path.sep)
                    if recursive:
                        ret.extend(ls(node_path,pattern=pattern,recursive=recursive,relative=relative,_start_match=_start_match))
                else:
                    if relative:
                        ret.append(node_path[_start_match:])
                    else:
                        ret.append(node_path)
        except:
            pass
    return ret