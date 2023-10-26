from dataclasses import dataclass, field

@dataclass
class Group:
    name: str
    target: str
    admin: str

    threads: int = 0
    members: list = field(default_factory=lambda: [])
    members_count: int = 0

@dataclass
class Member:
    name: str
    cores: int
    threads: int
