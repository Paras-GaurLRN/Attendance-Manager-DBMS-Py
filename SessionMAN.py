'''
Whenever program loads, we present a login menu.
We can login into any valid user.
The user may access the database or change user configurations.
Settings that can be changed are- Auto Commit on Logout, Change Password, Delete User, Change UserCreation Password (if admin login).
From there, we can View Data, Add Data, Delete Data, Export Data, Import Data, all via a simple query.
In Case of a transaction failure, we signal failure. Else show successful completion.
The User can go back to the profile menu from both of the above places.
From there the user can access the other menus, or logout.
When loggedout, we bring up the userlogin menu, from which we can terminate the program.
'''

'''
Menu Hierarchy

LoginMenu
- Settings Menu (if admin login)
-- Change Admin Password (if admin login)
-- Create User (if admin login)
-- Delete User (if admin login)
-- Change User Password (if admin login)
- DataBase Menu
-- Query Panel + View of database
'''

# Menus
'''
Max size of table - 10 (StdID) + 10 (CID) + 10 (Date, DD/MM/YYYY) + 4*1 (| bar) + 6 (spaces around characters) = 40 characters in table
Menu size -> fixed ljust, pad till 40
'''

# from json import loads, dumps
from DataTypes import *
from HashEncrypt import *
from DatMAN import *
from os import system,name
from time import sleep as s
from pathlib import Path

def cls() -> None:
    system('cls' if name=='nt' else 'clear')

def __Query_Database_Menu(dm) -> None:
    while True:
        cls()
        print("--- Custom Database Query Engine ---")
        print("Format: PRA/EXP + [IDs...] + COUNT + P/A")
        print("Type 'return' to go back.")
        command = input("> ")
        
        if command.lower() == 'return':
            return
            
        print("Processing..."); s(1)
        dm.fetch_accessible_records()
        success, result = dm.execute_query(command)
        
        print("\n" + result)
        input("\nPress Enter to continue...")


def DataBaseMenu(curr_user : User) -> int:
    is_admin = (curr_user.UserName.lower() == "admin")
    
    dm = DataManager(curr_user)
    dm.fetch_accessible_records()

    if is_admin:
        null_recs = dm.get_null_records()
        if null_recs:
            cls()
            print(f"There are {len(null_recs)} null values. Do you want to update them? (y/n)")
            ans = input("> ").lower()
            modified_any = False
            if ans == 'y':
                for r in null_recs:
                    cls()
                    print(f"Resolving Null Record -> Date: {r.date} | Course: {r.course} | Student: {r.student}")
                    val = input("Enter Status [P/A] or press Enter to skip: ").upper()
                    if val in ['P', 'A']:
                        dm.update_status(r.date, r.course, r.student, val)
                        modified_any = True
                if modified_any:
                    cls()
                    print("--- Updated Attendance Matrices ---")
                    dm.print_attendance_matrix()
                    input("\nPress Enter to continue...")

    while True:
        cls()
        print(f"\n--- DataBase Menu ---")
        print(f"Welcome, {curr_user.UserName}. Session is active.")
        
        if is_admin:
            dates, courses, students = dm.get_distinct_ids()
            print("\n[--- Current ID Registry ---]")
            if dates: print(f"Dates    : {', '.join(sorted(list(dates)))}")
            if courses: print(f"Courses  : {', '.join(sorted(list(courses)))}")
            if students: print(f"Students : {', '.join(sorted(list(students)))}")
            print("-" * 27)
        s(1)
        
        print("Please Choose an action:")
        if is_admin:
            print("A) Write Command to Modify Database")
            print("B) View Database and Extract Analytics")
        else:
            print("A) View Database and Extract Analytics")
            
        print("Or, Type 'exit' to log out to MainMenu.")
        
        choice : str = input("> ")
        if choice.lower() == 'exit':
            print("Logging out..."); s(1)
            return 0
            
        if is_admin:
            if choice.lower() not in ['a', 'b']:
                print("Invalid Option"); s(1)
                continue
                
            if choice.lower() == 'a':
                while True:
                    cls()
                    print("--- Modify Database Matrix ---")
                    print("Format: A/D + ID (e.g. 'A 10022026' or 'D SEZ305')")
                    print("Type 'return' to go back")
                    cmd = input("> ")
                    if cmd.lower() == 'return': break
                    
                    print("Executing Modification..."); s(1)
                    success, msg = dm.admin_execute_modify(cmd)
                    print(msg)
                    if success:
                        print("\n--- Updated Attendance Matrices ---")
                        dm.print_attendance_matrix()
                    input("\nPress Enter to continue...")

            elif choice.lower() == 'b':
                __Query_Database_Menu(dm)
        else:
            if choice.lower() != 'a':
                print("Invalid Option"); s(1)
                continue
                
            __Query_Database_Menu(dm)


def Settings_DataBaseMenu(curr_user : User) -> int:
    cls()
    if curr_user.UserName != "admin":
        return DataBaseMenu(curr_user)
    # Admin Login
    choice : str = "dummy"

    s(1); print("Welcome Admin, Please Choose A Menu:")
    s(1); print("# Type Settings for Settings")
    print("# Type Database for Database")
    print("Or, Type exit to Go to MainMenu")
    choice = input("> "); choice = choice.lower()

    if choice == 'exit': return 0
    while not (choice == cast(str,"settings") or choice == cast(str,"database")):
        print("Invalid Input, Please ReEnter"); s(2); cls()
        s(1); print("Welcome Admin, Please Choose A Menu:")
        s(1); print("# Type Settings for Settings")
        print("# Type Database for Database")
        choice = input("> "); choice = choice.lower()
        if choice == "exit": return 0
    
    if choice == cast(str,"database"):
        return DataBaseMenu(curr_user)
    
    del choice
    choice : str = "dummy"
    while True:
        print("Loading Settings",end=''); s(1);
        for _ in range(3): print('.',end=''); s(1)
        cls()
        s(1); print("Please Choose : ")
        s(1); print("A) Change Admin Password"); print("B) Create User")
        print("C) Delete User"); print("D) Change Existing User Password"); print("E) Grant/Revoke Data Access")
        print("Or, Type exit to Go to MainMenu")
        choice = input("> "); choice = choice.lower()
    
        if choice == "exit": return 0
        while not (choice == cast(str,'a') or choice == cast(str,'b') or choice == cast(str,'c') or choice == cast(str,'d') or choice == cast(str,'e')):
            print("Invalid Input, Please ReEnter"); s(2)
            cls()
            s(1); print("Please Choose : ")
            s(1); print("A) Change Admin Password"); print("B) Create User")
            print("C) Delete User"); print("D) Change Existing User Password"); print("E) Grant/Revoke Data Access")
            choice = input("> "); choice = choice.lower()
            if choice == "exit": return 0
    
        def __InnerMenu(choice : str) -> int:
            match (choice): # pyright: ignore[reportMatchNotExhaustive]
                case 'a':
                    # Change Admin Password
                    s(1)
                    NewPass_str : str = input("Enter New Password (or exit): ")
                    if NewPass_str.lower() == "exit": print("Exiting..."); s(1); return -1
                    cls()
                    HashedNewPassword : Optional[HashedPassword] = HashPassword(NewPass_str)
                    if HashedNewPassword is None:
                        print("Password Has Illegal Format"); s(2)
                        print("Please Refer to the Manual"); s(2)
                        return 0
                    
                    SafetyUsersFile : Dict[UserNameHex,PasswordHex] = {}
                    try:
                        Users : Dict[UserNameHex,PasswordHex] = {}
                        with open("Users.json",'r') as UsersFile:
                            Users = json.load(UsersFile)
                            
                        SafetyUsersFile = Users.copy()
                        UpdatedUsers : Dict[UserNameHex,PasswordHex] = {}
                        AdminRec : Tuple[UserNameHex,PasswordHex] = list(Users.items())[0]
                        old_admin_pass = cast(HashedPassword, bytes.fromhex(AdminRec[1]))
                        del Users[AdminRec[0]]
                        UpdatedUsers[cast(UserNameHex,EncryptS(HashedNewPassword,"admin"))] = cast(PasswordHex,HashedNewPassword.hex())
                        for user_rec in Users.items():
                            UpdatedUsers[user_rec[0]] = user_rec[1]
    
                        # CASCADE UPDATE FOR ATTENDANCE DB
                        DB_FILE = "attendance_data.txt"
                        db_cache = []
                        db_exists = False
                        from os.path import exists as CheckFileExist
                        try:
                            if CheckFileExist(DB_FILE):
                                db_exists = True
                                with open(DB_FILE, "r", encoding="utf-8") as f:
                                    for line in f:
                                        encrypted_str = cast(Hex, line.strip())
                                        if encrypted_str:
                                            dec = DecryptS(old_admin_pass, encrypted_str)
                                            db_cache.append(EncryptS(HashedNewPassword, dec) + "\n")
                        except Exception as e:
                            print(f"Warning: Failed to decrypt database during cascade: {e}")
                            db_exists = False

                        with open("Users.json",'w') as UsersFile:
                            json.dump(UpdatedUsers,UsersFile,indent=4,ensure_ascii=False)    
    
                        if db_exists:
                            try:
                                with open(DB_FILE, "w", encoding="utf-8") as f:
                                    f.writelines(db_cache)
                            except Exception as e:
                                print(f"Warning: Failed to write database during cascade: {e}")

                        s(1); print("Password Change was Succesful")
                    
                    except FileNotFoundError:
                        s(1); print("Users File Does Not Exist")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except json.JSONDecodeError:
                        s(1); print("Users File is Corrupted")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except OSError:
                        s(1); print("IO Blocked, Restored File")
                        if SafetyUsersFile != {}:
                            with open("Users.json",'w') as UsersFile:
                                json.dump(SafetyUsersFile,UsersFile,indent=4,ensure_ascii=False)
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
    
                case 'b':
                    # Create User
                    s(1)
                    UserToCreate : str = input("UserName for New User (or exit): ")
                    UserToCreate = UserToCreate.lower()
                    if UserToCreate == "exit": print("Exiting..."); s(1); return -1
                    if not Validate_UserName(UserToCreate):
                        print("UserName Has Illegal Format"); s(2)
                        print("Please Refer to the Manual"); s(2)
                        return 0
                    
                    SafetyUsersFile : Dict[UserNameHex,PasswordHex] = {}
                    SafetyUsersDataFile : Dict[UserNameHex,Dict[str,StudentListHex|CourseListHex|DirtyBit]] = {}
                    Users : Dict[UserNameHex,PasswordHex] = {}
                    UsersData : Dict[UserNameHex,Dict[str,StudentListHex|CourseListHex|DirtyBit]] = {}
                    try:
                        with open("Users.json",'r') as UsersFile:
                            Users = json.load(UsersFile)
                        SafetyUsersFile = Users.copy()
                    except FileNotFoundError:
                        s(1); print("Users File Does Not Exist")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except json.JSONDecodeError:
                        s(1); print("Users File is Corrupted")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except OSError:
                        s(1); print("IO Blocked, reading Users File")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
    
                    try:
                        with open("UsersData.json",'r') as UsersDataFile:
                            UsersData = json.load(UsersDataFile)
                        SafetyUsersDataFile = UsersData.copy()
                    except FileNotFoundError:
                        UsersData = {}
                        SafetyUsersDataFile = {}
                    except json.JSONDecodeError:
                        UsersData = {}
                        SafetyUsersDataFile = {}
                    except OSError:
                        s(1); print("IO Blocked, reading UsersData File")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
    
                    for user_rec in Users.items():
                        UserPass : HashedPassword = cast(HashedPassword,bytes.fromhex(user_rec[1]))
                        if UserToCreate == DecryptS(UserPass,user_rec[0]):
                            print("Such A User Already Exists"); s(1)
                            return 0
                    
                    NewPass_str : str = input("Enter New Password (or exit): ")
                    if NewPass_str.lower() == "exit": print("Exiting..."); s(1); return -1
                    cls()
                    HashedNewPassword : Optional[HashedPassword] = HashPassword(NewPass_str)
                    if HashedNewPassword is None:
                        print("Password Has Illegal Format"); s(2)
                        print("Please Refer to the Manual"); s(2)
                        return 0
                    
                    StudentListHexForm : List[str] = []
                    CourseListHexForm : List[str] = []
                    DateListHexForm : List[str] = []

                    UserNameHexForm : UserNameHex = cast(UserNameHex,EncryptS(HashedNewPassword,UserToCreate))
                    Users[UserNameHexForm] = cast(PasswordHex,HashedNewPassword.hex())
                    DirtyBit_val : DirtyBit = cast(DirtyBit,0)
    
                    UsersData[UserNameHexForm] = {
                        "DB" : DirtyBit_val,
                        "S" : StudentListHexForm,
                        "C" : CourseListHexForm,
                        "D" : DateListHexForm
                    }
    
                    try:
                        with open("Users.json", 'w') as UsersFile:
                            json.dump(Users, UsersFile, indent=4, ensure_ascii=False)
                        with open("UsersData.json", 'w') as UsersDataFile:
                            json.dump(UsersData, UsersDataFile, indent=4, ensure_ascii=False)
                        s(1); print("User Creation Was Successful")
                    except OSError:
                        s(1); print("IO Blocked, Restored Files")
                        if SafetyUsersFile != {}:
                            with open("Users.json", 'w') as UsersFile:
                                json.dump(SafetyUsersFile, UsersFile, indent=4, ensure_ascii=False)
                            with open("UsersData.json", 'w') as UsersDataFile:
                                json.dump(SafetyUsersDataFile, UsersDataFile, indent=4, ensure_ascii=False)
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
    
    
                case 'c':
                    # Delete User
                    s(1)
                    UserToDelete : str = input("UserName of User to Delete (or exit): ")
                    UserToDelete = UserToDelete.lower()
                    if UserToDelete == "exit": print("Exiting..."); s(1); return -1
                    if not Validate_UserName(UserToDelete):
                        print("UserName Has Illegal Format"); s(2)
                        print("Please Refer to the Manual"); s(2)
                        return 0
    
                    SafetyUsersFile : Dict[UserNameHex,PasswordHex] = {}
                    SafetyUsersDataFile : Dict[UserNameHex,Dict[str,StudentListHex|CourseListHex|DirtyBit]] = {}
                    Users : Dict[UserNameHex,PasswordHex] = {}
                    UsersData : Dict[UserNameHex,Dict[str,StudentListHex|CourseListHex|DirtyBit]] = {}
                    try:
                        with open("Users.json",'r') as UsersFile:
                            Users = json.load(UsersFile)
                        SafetyUsersFile = Users.copy()
                    except FileNotFoundError:
                        s(1); print("Users File Does Not Exist")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except json.JSONDecodeError:
                        s(1); print("Users File is Corrupted")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except OSError:
                        s(1); print("IO Blocked, reading Users File")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
    
                    try:
                        with open("UsersData.json",'r') as UsersDataFile:
                            UsersData = json.load(UsersDataFile)
                        SafetyUsersDataFile = UsersData.copy()
                    except FileNotFoundError:
                        UsersData = {}
                        SafetyUsersDataFile = {}
                    except json.JSONDecodeError:
                        UsersData = {}
                        SafetyUsersDataFile = {}
                    except OSError:
                        s(1); print("IO Blocked, reading UsersData File")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
    
                    try:
                        UserRec : Optional[Tuple[UserNameHex,PasswordHex]] = None
                        for user_rec in Users.items():
                            UserPass : HashedPassword = cast(HashedPassword,bytes.fromhex(user_rec[1]))
                            if UserToDelete == DecryptS(UserPass,user_rec[0]):
                                UserRec = user_rec
    
                        if UserRec is None:
                            raise ValueError
                        else:
                            Users.pop(UserRec[0], None)
                            UsersData.pop(UserRec[0], None)
                        
                        with open("Users.json",'w') as UsersFile:
                            json.dump(Users,UsersFile,indent=4,ensure_ascii=False)
                        
                        with open("UsersData.json",'w') as UsersDataFile:
                            json.dump(UsersData,UsersDataFile,indent=4,ensure_ascii=False)
                        
                        s(1); print("User Deletion Was Successful")
    
                    except ValueError:
                        print("Such A User Does Not Exist"); s(1)
                        return 0
                    except FileNotFoundError:
                        s(1); print("Users File Does Not Exist")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except OSError:
                        s(1); print("IO Blocked, Restored File")
                        if SafetyUsersFile != {}:
                            with open("Users.json",'w') as UsersFile:
                                json.dump(SafetyUsersFile,UsersFile,indent=4,ensure_ascii=False)
                            with open("UsersData.json",'w') as UsersDataFile:
                                json.dump(SafetyUsersDataFile,UsersDataFile,indent=4,ensure_ascii=False)
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
                    
                case 'd':
                    # Change Existing User Password
                    s(1)
                    UserToFind : str = input("Enter UserName (or exit): "); UserToFind = UserToFind.lower()
                    if UserToFind == "exit": print("Exiting..."); s(1); return -1
                    if not Validate_UserName(UserToFind): 
                        print("UserName Has Illegal Format"); s(2)
                        print("Please Refer to the Manual"); s(2)
                        return 0
    
                    SafetyUsersFile : Dict[UserNameHex,PasswordHex] = {}
                    try:
                        Users : Dict[UserNameHex,PasswordHex] = {}
                        with open("Users.json",'r') as UsersFile:
                            Users = json.load(UsersFile)
                        
                        SafetyUsersFile = Users.copy()
    
                    except FileNotFoundError:
                        s(1); print("Users File Does Not Exist")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except json.JSONDecodeError:
                        s(1); print("Users File is Corrupted")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except OSError:
                        s(1); print("IO Blocked, Restored File")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
                    
                    SafetyUsersDataFile : Dict[UserNameHex,Dict[str,StudentListHex|CourseListHex|DirtyBit]] = {}
                    UsersData : Dict[UserNameHex,Dict[str,StudentListHex|CourseListHex|DirtyBit]] = {}
                    try:
                        with open("UsersData.json",'r') as UsersDataFile:
                            UsersData = json.load(UsersDataFile)
                        SafetyUsersDataFile = UsersData.copy()
                    except FileNotFoundError:
                        pass
                    except json.JSONDecodeError:
                        pass
                    except OSError:
                        s(1); print("IO Blocked, reading UsersData File")
                        return 2
                    
                    NewPass_str : str = input("Enter New Password (or exit): ")
                    if NewPass_str.lower() == "exit": print("Exiting..."); s(1); return -1
                    cls()
                    HashedNewPassword : Optional[HashedPassword] = HashPassword(NewPass_str)
                    if HashedNewPassword is None:
                        print("Password Has Illegal Format"); s(2)
                        print("Please Refer to the Manual"); s(2)
                        return 0
                    
                    try: # Change
                        if SafetyUsersFile == {}:
                            raise FileNotFoundError
                        Users : Dict[UserNameHex,PasswordHex] = SafetyUsersFile.copy()
                        UpdatedUsers : Dict[UserNameHex,PasswordHex] = {}
                        UserRec : Optional[Tuple[UserNameHex,PasswordHex]] = None
                        for user_rec in Users.items():
                            UserPass : HashedPassword = cast(HashedPassword,bytes.fromhex(user_rec[1]))
                            if UserToFind == DecryptS(UserPass,user_rec[0]):
                                UserRec = user_rec
                        
                        if UserRec is None:
                            raise ValueError
                        else:
                            Users.pop(UserRec[0], None)
                        
                        AdminRec = list(Users.items())[0] if Users else None
                        if AdminRec:
                            UpdatedUsers[AdminRec[0]] = AdminRec[1]
                            Users.pop(AdminRec[0], None)
    
                        new_user_hex = cast(UserNameHex,EncryptS(HashedNewPassword,UserToFind))
                        UpdatedUsers[new_user_hex] = cast(PasswordHex,HashedNewPassword.hex())
                        for user_rec in Users.items():
                            UpdatedUsers[user_rec[0]] = user_rec[1]
                            
                        if UserRec[0] in UsersData:
                            curr_data = UsersData.pop(UserRec[0])
                            UsersData[new_user_hex] = curr_data
    
                        with open("Users.json",'w') as UsersFile:
                            json.dump(UpdatedUsers,UsersFile,indent=4,ensure_ascii=False)    
                            
                        with open("UsersData.json",'w') as UsersDataFile:
                            json.dump(UsersData,UsersDataFile,indent=4,ensure_ascii=False)
    
                        s(1); print("Password Change was Succesful")
                    
                    except ValueError:
                        print("Such A User Does Not Exist"); s(1)
                        return 0
                    except FileNotFoundError:
                        s(1); print("Users File Does Not Exist")
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 1
                    except OSError:
                        s(1); print("IO Blocked, Restored File")
                        if SafetyUsersFile != {}:
                            with open("Users.json",'w') as UsersFile:
                                json.dump(SafetyUsersFile,UsersFile,indent=4,ensure_ascii=False)
                        if SafetyUsersDataFile != {}:
                            with open("UsersData.json",'w') as UsersDataFile:
                                json.dump(SafetyUsersDataFile,UsersDataFile,indent=4,ensure_ascii=False)
                        s(1); print("Aborting Procedure, Returning to Settings")
                        return 2
                
                case 'e':
                    # Grant/Revoke Data Access
                    s(1)
                    UserToFind : str = input("Enter UserName to Modify Access (or exit): "); UserToFind = UserToFind.lower()
                    if UserToFind == "exit": print("Exiting..."); s(1); return -1
                    if not Validate_UserName(UserToFind): 
                        print("UserName Has Illegal Format"); s(2)
                        return 0
                    
                    try:
                        with open("Users.json", 'r') as uf:
                            all_users = json.load(uf)
                        with open("UsersData.json", 'r') as udf:
                            all_users_data = json.load(udf)
                    except:
                        print("Failed to load user files."); s(1); return 2
                    
                    admin_pass = LOADADMINPASS()
                    if not admin_pass: return 0

                    user_hex_key = None
                    for uk, uv in all_users.items():
                        try:
                            dec_name = DecryptS(bytes.fromhex(uv), cast(Hex, uk))
                            if dec_name == UserToFind:
                                user_hex_key = uk
                                break
                        except: pass
                        
                    if not user_hex_key or user_hex_key not in all_users_data:
                        print("User not found or user data missing."); s(1); return 0
                        
                    user_data_ref = all_users_data[user_hex_key]
                    
                    # Ensure properly format in case it is old schema
                    if "S" not in user_data_ref or isinstance(user_data_ref["S"], str): user_data_ref["S"] = []
                    if "C" not in user_data_ref or isinstance(user_data_ref["C"], str): user_data_ref["C"] = []
                    if "D" not in user_data_ref or isinstance(user_data_ref["D"], str): user_data_ref["D"] = []
                    
                    while True:
                        dec_s, dec_c, dec_d = [], [], []
                        for x in user_data_ref["S"]:
                            try: dec_s.append(DecryptS(admin_pass, cast(Hex, x)))
                            except: pass
                        for x in user_data_ref["C"]:
                            try: dec_c.append(DecryptS(admin_pass, cast(Hex, x)))
                            except: pass
                        for x in user_data_ref["D"]:
                            try: dec_d.append(DecryptS(admin_pass, cast(Hex, x)))
                            except: pass

                        dm = DataManager(User(0, "admin", b"", [], [], []))
                        dm.fetch_accessible_records()
                        all_dates, all_courses, all_students = dm.get_distinct_ids()
                        
                        cls()
                        print(f"--- Modifying Permissions for: {UserToFind} ---")
                        print("\n[Global Database IDs]")
                        print(f"Student IDs : {', '.join(sorted(list(all_students)))}")
                        print(f"Course IDs  : {', '.join(sorted(list(all_courses)))}")
                        print(f"Date IDs    : {', '.join(sorted(list(all_dates)))}")
                        
                        print("\n[Current User Accessible IDs]")
                        print(f"Student IDs : {', '.join(dec_s)}")
                        print(f"Course IDs  : {', '.join(dec_c)}")
                        print(f"Date IDs    : {', '.join(dec_d)}")
                        
                        print("\nChoose an option:")
                        print("1) Grant Access to ID")
                        print("2) Revoke Access from ID")
                        print("3) Revoke All Access")
                        print("4) Grant All Access")
                        print("Or type 'exit' to return")
                        opt = input("> ").strip().lower()
                        if opt == 'exit': break
                        
                        if opt == '3':
                            user_data_ref["S"] = []
                            user_data_ref["C"] = []
                            user_data_ref["D"] = []
                            with open("UsersData.json", 'w') as f: json.dump(all_users_data, f, indent=4)
                            print("Revoked all access successfully."); s(1)
                            continue
                            
                        if opt == '4':
                            user_data_ref["S"] = [EncryptS(admin_pass, cast(str, x)) for x in all_students]
                            user_data_ref["C"] = [EncryptS(admin_pass, cast(str, x)) for x in all_courses]
                            user_data_ref["D"] = [EncryptS(admin_pass, cast(str, x)) for x in all_dates]
                            with open("UsersData.json", 'w') as f: json.dump(all_users_data, f, indent=4)
                            print("Granted all access successfully."); s(1)
                            continue
                            
                        if opt in ['1', '2']:
                            print("Enter exact ID (Student, Course, Date):")
                            tgt_id = input("> ").strip()
                            if not tgt_id: continue
                            
                            is_s, is_c, is_d = False, False, False
                            if len(tgt_id) == 10 and tgt_id.isdigit(): is_s = True
                            elif len(tgt_id) == 6 and tgt_id[:3].isalpha() and tgt_id[3:].isdigit(): is_c = True
                            elif len(tgt_id) == 8 and tgt_id.isdigit(): is_d = True
                            else:
                                print("Invalid ID Format"); s(1); continue
                                
                            arr_key, curr_dec_arr = None, None
                            valid_exists = False
                            
                            if is_s:
                                arr_key = "S"; curr_dec_arr = dec_s
                                if tgt_id in all_students: valid_exists = True
                            elif is_c:
                                arr_key = "C"; curr_dec_arr = dec_c
                                if tgt_id in all_courses: valid_exists = True
                            elif is_d:
                                arr_key = "D"; curr_dec_arr = dec_d
                                if tgt_id in all_dates: valid_exists = True
                                
                            if opt == '1':
                                if tgt_id in curr_dec_arr:
                                    print("User already has access"); s(1)
                                elif not valid_exists:
                                    print("ID does not exist in Database"); s(1)
                                else:
                                    enc_val = EncryptS(admin_pass, tgt_id)
                                    user_data_ref[arr_key].append(enc_val)
                                    with open("UsersData.json", 'w') as f: json.dump(all_users_data, f, indent=4)
                                    print("Access successfully granted"); s(1)
                            
                            elif opt == '2':
                                if tgt_id not in curr_dec_arr:
                                    print("User does not have access to this ID"); s(1)
                                else:
                                    new_enc_arr = []
                                    for x in user_data_ref[arr_key]:
                                        try:
                                            dec_val = DecryptS(admin_pass, cast(Hex, x))
                                            if dec_val != tgt_id: new_enc_arr.append(x)
                                        except: new_enc_arr.append(x)
                                    user_data_ref[arr_key] = new_enc_arr
                                    with open("UsersData.json", 'w') as f: json.dump(all_users_data, f, indent=4)
                                    print("Access successfully revoked"); s(1)

                    return 0
    
            s(1); print("Returning to Settings"); s(1)
            return -1
    
        while not (__InnerMenu(choice)):
            cls()
            print("Restarting Current Menu"); s(2)
            print("Type Exit in Terminal to Exit"); s(2)
    
        pass


def MainMenu() -> int:
    ADMINPASS : Optional[HashedPassword]
    try:
        ADMINPASS = LOADADMINPASS() # pyright: ignore[reportConstantRedefinition]
        if ADMINPASS is None:
            raise OSError
    except OSError:
        return 401
    cls()
    print("Welcome to Attendance Management System\n")
    print("Please enter USERNAME to continue")
    print("Or, type exit to exit")
    choice : str = input("Input > ")
    choice = choice.lower()

    if choice == "exit":
        s(1); print("Exiting",end='')
        for _ in range(3): s(1); print('.',end='')
        s(1)
        return -1
    
    print(f"\nSearching For User : {choice}\n")
    try:
        with open("Users.json",'x') as UsersFile:
            s(1); print("\nNote: Users file was missing")
            s(1); print("      Creating file with admin user\n")

            adminRecord : Dict[UserNameHex,PasswordHex] = {
                cast(UserNameHex,EncryptS(ADMINPASS,"admin")):cast(PasswordHex,ADMINPASS.hex())
                } # Make Admin Data
            json.dump(adminRecord,UsersFile,indent=4,ensure_ascii=False)
            
        with open("UsersData.json", 'a') as UsersDataFile:
            pass # just touch the file so it exists

        s(1); print("Success In File Creation")
    except FileExistsError:
        pass
    except OSError:
        s(1); print("Failure In File Creation")
        Path("Users.json").unlink(missing_ok=True)
        Path("UsersData.json").unlink(missing_ok=True)
        s(1); print("Restarting Menu"); s(1)
        return 2*0
    
    Users : Dict[UserNameHex,PasswordHex] = {}
    UserPass : HashedPassword = cast(HashedPassword,b'')
    try:
        with open("Users.json",'r') as UsersFile:
            Users = json.load(UsersFile)
            for UserRecord in Users.items():
                UserPass = cast(HashedPassword,bytes.fromhex(UserRecord[1]))
                if choice.lower() == DecryptS(UserPass,UserRecord[0]):
                    raise StopIteration
            raise ValueError
    except StopIteration:
        # User Found
        s(1); pass_str : str = input("User Found, Enter Password: ")
        cls()
        s(1); print("Checking, Please Wait..."); s(2)
        if CheckPassword(pass_str,UserPass):
            s(1); print("Loading User Data...\n"); s(2)
            Loaded_User : User = Load_User_Data(choice)
            return Settings_DataBaseMenu(Loaded_User)
        else:
            s(1); print("Invalid Password, Restarting Menu"); s(1)
    except ValueError:
        # User Absent
        s(1); print("Invalid User, Restarting Menu\n"); s(1)
        return 3*0
    except json.JSONDecodeError:
        s(1); print("Failure In File Reading (Corrupted File)")
        s(1); print("Restarting Menu"); s(1)
        return 2*0
    except OSError:
        s(1); print("Failure In File Reading")
        s(1); print("Restarting Menu"); s(1)
        return 2*0
    return 0