"""Repository data models"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class CodeChange:
    """Represents a code change in a repository"""
    file_path: str
    change_type: str
    additions: int
    deletions: int
    diff: str
    affected_functions: List[str] = field(default_factory=list)

@dataclass
class Commit:
    """Represents a Git commit"""
    hash: str
    author: str
    timestamp: datetime
    message: str
    changes: List[CodeChange]
    repository: str

@dataclass
class Repository:
    """Represents a repository in the ecosystem"""
    name: str
    url: str
    language: str
    components: List[str]
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    latest_commit: Optional[Commit] = None

