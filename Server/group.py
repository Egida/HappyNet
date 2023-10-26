from dataclasses import dataclass, field


@dataclass
class Member:
    name: str
    cores: int
    threads: int

@dataclass
class Group:
    name: str
    target: str
    admin: str

    threads: int = 0
    members: list = field(default_factory=lambda: [])
    banned: list = field(default_factory=lambda: [])
    members_count: int = 0

    def add_member(self, member: Member):
        self.members.append(member)
        self.threads += member.threads
        self.members_count += 1

    def rem_member(self, member: Member):
        self.members.remove(member)
        self.threads -= member.threads
        self.members_count -= 1
