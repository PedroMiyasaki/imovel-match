from pydantic import BaseModel
from typing import Optional, Literal, List

class PropertyCriteria(BaseModel):
    property_type: Literal["house", "apartment"]
    budget: float
    location: str
    rooms: Optional[int]
    size: Optional[float]
    parking_spots: Optional[int]
    amenities: List[str]