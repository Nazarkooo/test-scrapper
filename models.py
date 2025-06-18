from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Company:
    company_id: str
    category: str
    brand: str
    phone: Optional[List[str]]
    address: str
    city: str
    state: str
    postalCode: int
    reportUrl: str
    owner: Optional[str]
