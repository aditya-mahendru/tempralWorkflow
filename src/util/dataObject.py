from dataclasses import dataclass
# from datetime import datetime

@dataclass
class OrderObject:
    id: str
    data: dict
    created_at: str
    updated_at: str
    payment_id: str
    shipping_address: str