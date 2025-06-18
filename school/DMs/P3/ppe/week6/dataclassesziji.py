from dataclasses import dataclass, field
from typing import List

@dataclass
class Article:
    id: str
    source: str
    title: str
    description: str
    date: str
    categories: List[str] = field(default_factory=list)
