from dataclasses import dataclass, field

groups = []

def find_group(name):
    for group in groups:
        if group.name == name:
            return group
    return None

def find_user(group, name):
    for user in group.members:
        if user.name == name:
            return user
    return None

@dataclass
class Member:
    name: str
    cores: int
    threads: int

    requests_per_second: int = 0
    requests_total: int = 0

@dataclass
class Group:
    name: str
    target: str
    admin: str

    threads: int = 0
    members: list = field(default_factory=lambda: [])
    banned: list = field(default_factory=lambda: [])
    members_count: int = 0

    status: str = 'idle'

    requests_per_second: int = 0
    requests_total: int = 0

    def add_member(self, member: Member):
        self.members.append(member)
        self.threads += member.threads
        self.members_count += 1

    def rem_member(self, member: Member):
        self.members.remove(member)
        self.threads -= member.threads
        self.members_count -= 1

    def calc_reqs(self):
        reqs = 0
        per_s = 0
        for member in self.members:
            reqs += member.requests_total
            per_s += member.requests_per_second
        self.requests_per_second = per_s
        self.requests_total = reqs

groups.append(Group('local', 'http://127.0.0.1:8000/', 'admin'))
