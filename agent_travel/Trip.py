import re
from pydantic import BaseModel, Field, validator
from typing import Optional

class Trip(BaseModel):
    """A Pydantic model to represent a trip record from a CSV file."""
    day: Optional[int] = Field(None, alias='Day')
    date: Optional[str] = Field(None, alias='Date')
    activity: Optional[str] = Field(None, alias='Activity')
    description: Optional[str] = Field(None, alias='Description')
    location: Optional[str] = Field(None, alias='Location')
    cost: Optional[str] = Field(None, alias='Cost')
    travel_distance: Optional[str] = Field(None, alias='Travel Distance')