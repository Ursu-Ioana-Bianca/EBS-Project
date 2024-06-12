from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Publication(_message.Message):
    __slots__ = ("company", "value", "drop", "variation", "date")
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DROP_FIELD_NUMBER: _ClassVar[int]
    VARIATION_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    company: str
    value: float
    drop: float
    variation: float
    date: str
    def __init__(self, company: _Optional[str] = ..., value: _Optional[float] = ..., drop: _Optional[float] = ..., variation: _Optional[float] = ..., date: _Optional[str] = ...) -> None: ...
