import os, re, subprocess

class Gitolite(object):
    WARNING_MESSAGE="# Generated automatically by Gitolite.py\n"
    KEYFILE_PATTERN=re.compile('^(?P<user_name>[a-zA-Z0-9][a-zA-Z0-9_\-.]*(@[a-zA-Z0-9_\-][a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-.]{2,2}[a-zA-Z0-9_\-.]*){0,1})\.pub$')
    REPO_CONF_PATTERN=re.compile('^(?P<repo_name>[a-zA-Z_.-]*)\.conf$')
    REPO_NAME_PATTERN=re.compile('^(?P<repo_name>[a-zA-Z_.-]*)$')
    REPO_RULE_PATTERN=re.compile('\s*(?P<access>(-)|([rRwW+]{1,3}))\s*(?P<refs>\s[a-zA-Z0-9_][a-zA-Z0-9_\-.*/]*){0,1}\s*=\s*(?P<users>[a-zA-Z0-9_.\- @]*)\s*#*.*$')
    GROUP_PATTERN=re.compile('^[a-zA-Z0-9][a-zA-Z0-9_.\-]*$')
    GROUP_LINE_PATTERN=re.compile('^\s*@(?P<group_name>[a-zA-Z0-9][a-zA-Z0-9_.\-]*)\s*=\s*(?P<users>[a-zA-Z0-9_.\- @]*)\s*#*.*$')

    def __init__(self, path, url=None):
        self._admin_path=path
        self._actions=[]
        self._groups={}
        self._users=[]
        self._repos={}
        if url is not None and not os.path.isdir(self._admin_path):
            subprocess.check_call(["git","clone","url",self._admin_path])
        else:
            subprocess.check_call(["git", "pull"], cwd=self._admin_path)
        self._load_users()
        self._load_groups()
        self._load_repos()

    def _load_users(self):
        self._users=[]
        for f in os.listdir(os.path.join(self._admin_path,'keydir')):
            match = Gitolite.KEYFILE_PATTERN.match(f)
            if match:
                self._users.append(match.group('user_name'))

    def _load_groups(self):
        if not os.path.isfile(os.path.join(self._admin_path,'conf/groups.conf')):
            raise Exception("Missing conf/groups.conf")
        conf = open(os.path.join(self._admin_path,'conf/groups.conf'),'r').read()
        for ln in conf.split('\n'):
            match = Gitolite.GROUP_LINE_PATTERN.match(ln)
            if match:
                self._groups[match.group('group_name')] = match.group('users').split(' ')

    def _save_groups(self):
        conf = open(os.path.join(self._admin_path,'conf/groups.conf'),'w')
        conf.write(Gitolite.WARNING_MESSAGE)
        for group,users in self._groups.items():
            conf.write("@"+group+" = "+" ".join(users)+"\n")
        conf.close()
        subprocess.check_call(["git", "add", "./conf/groups.conf"], cwd=self._admin_path)

    def _load_repos(self):
        if os.path.isdir(os.path.join(self._admin_path,'conf/repos')):
            for f in os.listdir(os.path.join(self._admin_path,'conf/repos')):
                match = Gitolite.REPO_CONF_PATTERN.match(f)
                if match:
                    self._load_repo(match.group('repo_name'))

    def _save_repos(self):
        if not os.path.isdir(os.path.join(self._admin_path,'conf/repos')):
            os.mkdir(os.path.join(self._admin_path,'conf/repos'))
        for r in self._repos.keys():
            self._save_repo(r)

    def _parse_rule_string(self, rule_string):
        match = Gitolite.REPO_RULE_PATTERN.match(rule_string)
        if not match:
            raise Exception("Invalid rule")
        match = match.groupdict()
        access = match['access']
        refs = match.get('refs',None)
        user_list = match['users'].split(' ')
        return (access, refs, user_list)

    def _load_repo(self,repo_name):
        conf = open(os.path.join(self._admin_path,'conf/repos/'+repo_name+'.conf'),'r').read()
        rules = []
        for ln in conf.split('\n'):
            try:
                rules.append(self._parse_rule_string(ln))
            except:
                pass
        self._repos[repo_name]=rules

    def _save_repo(self, repo_name):
        repo = self._repos[repo_name]
        with open(os.path.join(self._admin_path,'conf/repos/'+repo_name+'.conf'),'w') as conf:
            conf.write(Gitolite.WARNING_MESSAGE)
            conf.write("repo "+repo_name+"\n")
            for rule in self._repos[repo_name]:
                access, refs, user_list = rule
                conf.write('    ')
                conf.write(access)
                conf.write(' ')
                if refs is not None:
                    conf.write(refs)
                    conf.write(' ')
                conf.write(' = ')
                conf.write(' '.join(user_list))
                conf.write('\n')
        subprocess.check_call(["git", "add", "./conf/repos/"+repo_name+".conf"], cwd=self._admin_path)

    def create_repo(self, repo_name):
        if not Gitolite.REPO_NAME_PATTERN.match(repo_name):
            raise Exception("Invalid repo name")
        if repo_name in self._repos:
            raise Exception("Repo already exists")
        self._repos[repo_name]=[]
        self._actions.append("Create repo "+repo_name)

    def remove_repo(self, repo_name):
        if not repo_name in self._repos:
            raise Exception("Repo does not exist")
        subprocess.check_call(["git", "rm", "./conf/repos/"+repo_name+".conf"], cwd=self._admin_path)
        del self._repos[repo_name]
        self._actions.append("Remove repo "+repo_name)


    def add_rule_string(self, repo_name, rule_string):
        access,refs,user_list = self._parse_rule_string(rule_string)
        self.add_rule(repo_name,access,user_list,refs)

    def add_rule(self, repo_name, access, user_list, refs = None):
        if not repo_name in self._repos:
            raise Exception("Repo does not exist")
        self._actions.append("Add access rule to "+repo_name)
        self._repos[repo_name].append((access,refs,user_list))

    def get_rules(self,repo_name):
        if not repo_name in self._repos:
            raise Exception("Repo does not exist")
        return self._repos[repo_name]

    def get_repos(self):
        return self._repos.keys()

    def check_acl(self, repo, user, operation, ref=None):
        groups = self.get_user_groups(user)
        apply = []
        for rule in self._repos[repo]:
            access, refs, user_list = rule
            relevant = False
            for g in groups:
                if g in user_list:
                    relevant = True
                    break
            if not relevant:
                relevant = user in user_list
            if relevant:
                if refs is None or ref is None or re.match(refs,ref):
                    apply.append(rule)

        for rule in apply:
            access, refs, user_list = rule
            if access == '-':
                return False
            if operation in access:
                return True

    def remove_user(self, user):
        if not user in self._users:
            raise Exception("User does not exist")
        self._users.remove(user)
        os.remove(os.path.join(self._admin_path,'keydir/'+user+'.pub'))
        subprocess.check_call(["git", "rm", "./keydir/"+user+".pub"], cwd=self._admin_path)
        self._actions.append("Remove user "+user)

    def add_user(self, user, key):
        if not Gitolite.KEYFILE_PATTERN.match(user+'.pub'):
            raise Exception("Invalid user name")
        if user in self._users:
            raise Exception("User already exists")
        if os.path.isfile(key):
            key = open(key,'r').read()
        open(os.path.join(self._admin_path,'keydir/'+user+'.pub'),'w').write(key)
        subprocess.check_call(["git", "add", "./keydir/"+user+".pub"], cwd=self._admin_path)
        self._users.append(user)
        self._actions.append("Add user "+user)

    def users(self):
        return self._users

    def get_user_key(self,user):
        if user not in self._users:
            raise Exception("User does not exist")
        return open(os.path.join(self._admin_path,'keydir/'+user+'.pub'),'r').read()

    def get_user_groups(self, user):
        ret=[]
        for group,users in self._groups.items():
            if user in users:
                ret.append(group)
        return ret

    def groups(self):
        return self._groups.keys()

    def add_user_to_group(self, user, group):
        if not Gitolite.KEYFILE_PATTERN.match(user+'.pub'):
            raise Exception("Invalid user name")
        if not group in self._groups:
            raise Exception("Group does not exist")
        self._groups[group].append(user)
        self._actions.append("Add user "+user+" to group "+group)

    def remove_user_from_group(self, user, group):
        if not group in self._groups:
            raise Exception("Group does not exist")
        self._groups[group].remove(user)
        self._actions.append("Remove user "+user+" from group "+group)

    def add_group(self, group):
        if not Gitolite.GROUP_PATTERN.match(group):
            raise Exception("Invalid group name")
        if group in self._groups:
            raise Exception("Group already exists")
        self._groups[group]=[]
        self._actions.append("Add group "+group)

    def get_group(self, name):
        return self._groups[name]

    def remove_group(self,group):
        if group not in self._groups:
            raise Exception("Group does not exists")
        del self._groups[group]

    def save(self,message=None):
        if message is None:
            message = '\n'.join(self._actions)
        subprocess.check_call(["git", "pull"], cwd=self._admin_path)

        self._save_groups()
        self._save_repos()

        subprocess.check_call(["git", "commit", "-a", "-m", message], cwd=self._admin_path)
        subprocess.check_call(["git", "push"], cwd=self._admin_path)


