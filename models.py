from dataclasses import dataclass
from typing import Optional

@dataclass
class Company:
    company_id: str
    brand: str
    phone: str
    address: str
    owner: Optional[str]
