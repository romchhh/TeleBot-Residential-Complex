from pydantic import BaseModel
from typing import Union

class RequestData(BaseModel):
    user_id: str
    name: str
    dataCreate: int
    phone: Union[str, None] = None
    car: Union[str, None] = None
    street: str
    house: Union[str, None] = None
    apartment: Union[str, None] = None
    typeReq: str
    pcsQuests: Union[str, None] = None
    timeQuests: Union[str, None] = None
    status: str

class RequestUpdate(BaseModel):
    user_id: str
    name: str
    dataCreate: int
    status: str