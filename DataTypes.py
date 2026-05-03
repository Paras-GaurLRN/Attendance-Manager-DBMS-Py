from typing import Optional,List,Tuple,Dict,cast,NewType
from dataclasses import dataclass
from datetime import date

# Hashing
HashedPassword = NewType("HashedPassword",bytes)

# Encryption
Nonce = NewType("Nonce",bytes)
Encrypted_Data = NewType("Encrypted_Data",bytes)
Hex = NewType("Hex",str)

# SessionMAN

PasswordHex = NewType("PasswordHex",Hex)
UserNameHex = NewType("UserNameHex",Hex)

# DatMAN

StudentListHex = NewType("StudentListHex",str)
CourseListHex = NewType("CourseListHex",str)
DirtyBit = NewType("DirtyBit",int)

@dataclass
class StudentID:
    def __init__(self,SID : int) -> None:
        self.__SID = SID

    @property
    def SID(self) -> int:
        return self.__SID
    
@dataclass
class CourseID:
    def __init__(self,CID : str) -> None:
        self.__CID = CID

    @property
    def CID(self) -> str:
        return self.__CID
    
@dataclass
class DateID:
    def __init__(self,Date : date) -> None:
        self.__Date = Date
    
    @property
    def Date(self) -> date:
        return self.__Date

@dataclass
class User:
    DirtyBit : int
    UserName : str
    PasswordHash : bytes
    Students : List[StudentID]
    Courses : List[CourseID]
    Dates : List[DateID]