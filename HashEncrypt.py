import bcrypt
from secrets import choice, token_bytes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from DataTypes import *
'''
Thus the idea is

Data (str) 
<-encode/decode-> 
bytes 
<-hex/fromhex-> 
Safely Storeable and Encrypted data now in string form converted from bytes, but expressed in Hex format
'''

'''Hashing'''

def __HashPassword_Base(ToHash : str) -> bytes :
    '''
    Docstring for __HashPassword_Base
    
    :param: ToHash
    :type: str
    :defaults: -
    :rtype: bytes
    Time ~ O(n * 2 ^ r) ; r = 15 (cost factor)
    
    Used to generate the hash for the passwords
    '''
    salt : bytes = bcrypt.gensalt(rounds=15,prefix=b"2b")
    pepper : str = choice("QWE098RTYPO7IULKASJDHFGZ56MXNCBV1234")
    ToHash_bytes : bytes = (pepper + ToHash).encode()
    HashPass : bytes = bcrypt.hashpw(ToHash_bytes,salt)
    return HashPass
    
def __Validate_Password(ToCheck : str) -> bool :
    '''
    Docstring for __Validate_Password

    :param: ToCheck
    :type: str
    :defaults: -
    :rtype: bool
    Time ~ O(n)

    Used to Validate Password
    Password must have:
    8 <= len <= 15
    1 <= lower char, upper char, number
    1 special character from {'!','@','#','$','%'}
    '''
    if(not(8 <= len(ToCheck) <= 15)) : return False
    if(not any(char.isdigit() for char in ToCheck)) : return False
    if(not any(char.islower() for char in ToCheck)) : return False
    if(not any(char.isupper() for char in ToCheck)) : return False
    if(not any(char in {'!','@','#','$','%'} for char in ToCheck)) : return False
    return True

def HashPassword(ToHash : str) -> Optional[HashedPassword] :
    '''
    Docstring for HashPassword
    
    :param: ToHash
    :type: str
    :defaults: -
    :rtype: bytes | None
    Time ~ O(n)

    Used to enforce password validation logic, then generate and return the Hash
    '''
    if __Validate_Password(ToHash):
        return cast(HashedPassword,__HashPassword_Base(ToHash))
    else:
        return None

def CheckPassword(ToCheck : str, SavedPass : HashedPassword) -> bool :
    '''
    Docstring for CheckPassword
    
    :param: ToHash, SavedPass
    :type: str, bytes
    :defaults: -, -
    :rtype: bool | None
    Time ~ O(36n * 2 ^ r) ; r = 15 (cost factor), 36 (Total Possible Peppers)
    
    Used to verify passwords

    SavedPass is passed from User data class
    '''
    if(not __Validate_Password(ToCheck)) : return False
    pepper : str
    for pepper in "123AB456CDEFGHIJK789LMNOPQRSTUV0WXYZ" :
        ToHash_bytes : bytes = (pepper + ToCheck).encode()
        if bcrypt.checkpw(ToHash_bytes,SavedPass) : return True
    return False

'''Encryption'''

def Encrypt(UserPasswordHash : HashedPassword, DataToEncrypt : str) -> Tuple[Nonce,Encrypted_Data]:
    key : bytes = UserPasswordHash.ljust(32,b'P')[:32]
    cipher : ChaCha20Poly1305 = ChaCha20Poly1305(key)
    nonce : bytes = token_bytes(12)
    DataToEncrypt_bytes : bytes = DataToEncrypt.encode()
    encrypted_data : bytes = cipher.encrypt(nonce=nonce,data=DataToEncrypt_bytes,associated_data=None)
    return (cast(Nonce,nonce),cast(Encrypted_Data,encrypted_data))

def Decrypt(UserPasswordHash : HashedPassword, Nonce : Nonce, encrypted_data : Encrypted_Data) -> str:
    key : bytes = UserPasswordHash.ljust(32,b'P')[:32]
    cipher : ChaCha20Poly1305 = ChaCha20Poly1305(key)
    return cipher.decrypt(nonce=Nonce,data=encrypted_data,associated_data=None).decode()

def __Encrypt_To_Single_Merged_String(UserPasswordHash : HashedPassword, DataToEncrypt : str) -> Hex:
    nonce : Nonce; encrypted_data : Encrypted_Data
    nonce,encrypted_data = Encrypt(UserPasswordHash,DataToEncrypt)
    combined : bytes = nonce+encrypted_data
    return cast(Hex,combined.hex())

def EncryptS(UserPasswordHash : HashedPassword, DataToEncrypt : str) -> Hex:
    return __Encrypt_To_Single_Merged_String(UserPasswordHash,DataToEncrypt)

def __Decrypt_From_Single_Merged_String(UserPasswordHash : HashedPassword, SingleEncryptedDataString : Hex) -> str:
    combined : bytes = bytes.fromhex(cast(str,SingleEncryptedDataString))
    nonce : Nonce; encrypted_data : Encrypted_Data
    nonce,encrypted_data = cast(Nonce,combined[:12]),cast(Encrypted_Data,combined[12:])
    return Decrypt(UserPasswordHash,nonce,encrypted_data)

def DecryptS(UserPasswordHash : HashedPassword, SingleEncryptedDataString : Hex) -> str:
    return __Decrypt_From_Single_Merged_String(UserPasswordHash,SingleEncryptedDataString)

import json

def LOADADMINPASS() -> Optional[HashedPassword]:
    ADMINPASS : HashedPassword
    try:
        with open("Users.json",'r') as UsersFile:
            AdminUser : Hex = list((json.load(UsersFile)).items())[0][1]
            ADMINPASS = cast(HashedPassword,bytes.fromhex(AdminUser)) # pyright: ignore[reportConstantRedefinition]
    except FileNotFoundError:
        ADMINPASS = cast(HashedPassword,b'$2b$15$N6/Kci.UFFHm9BM64xeeWOGZbz934Q7hF/5aSDfm1Uih9pn1upHqS') # pyright: ignore[reportConstantRedefinition]
    except OSError:
        print("WARNING: UNABLE TO DETECT UPDATES IN ADMINPASS")
        print("CORE PROCESS FAILURE, FORCED EXITING")
        print("CONTACT ADMIN TO FIX THE ISSUE")
        return None
    return ADMINPASS

# "Admin76$"
