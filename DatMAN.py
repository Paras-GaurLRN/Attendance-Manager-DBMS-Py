import datetime
from typing import List, Set, cast
from DataTypes import *
from HashEncrypt import EncryptS, DecryptS, LOADADMINPASS

# 1. Validation Logic
def Validate_Date(date_str: str) -> bool:
    if len(date_str) != 8 or not date_str.isdigit(): return False
    try:
        datetime.date(int(date_str[4:8]), int(date_str[2:4]), int(date_str[0:2]))
        return True
    except ValueError: return False

def Validate_Course(course_str: str) -> bool:
    if len(course_str) != 6: return False
    if not course_str[:3].isalpha() or not course_str[3:].isdigit(): return False
    return True

def Validate_Student(student_str: str) -> bool:
    if len(student_str) != 10 or not student_str.isdigit(): return False
    return True

def Validate_Status(status: str) -> bool:
    return status in ['P', 'A', '-']

# 2. Record Definition
class AttendanceRecord:
    def __init__(self, date: str, course: str, student: str, status: str):
        if not Validate_Date(date): raise ValueError("Invalid Date format")
        if not Validate_Course(course): raise ValueError("Invalid Course format")
        if not Validate_Student(student): raise ValueError("Invalid Student format")
        if not Validate_Status(status): raise ValueError("Invalid Status format")
        
        self.date = date
        self.course = course
        self.student = student
        self.status = status

    def to_string(self) -> str:
        return f"{self.date}{self.course}{self.student}{self.status}"
        
    @staticmethod
    def from_string(data: str) -> 'AttendanceRecord':
        if len(data) != 25: raise ValueError("Data string must be exactly 25 characters.")
        return AttendanceRecord(data[0:8], data[8:14], data[14:24], data[24:25])

    @property
    def get_date_obj(self) -> datetime.date:
        return datetime.date(int(self.date[4:8]), int(self.date[2:4]), int(self.date[0:2]))

    def __repr__(self):
        return f"Record(Date={self.date}, Course={self.course}, Student={self.student}, Status={self.status})"

# 3. Data Manager Class
class DataManager:
    DB_FILE = "attendance_data.txt"

    def __init__(self, user: User):
        self.user = user
        self.is_admin = (user.UserName.lower() == "admin")
        
        self.allowed_students: Set[int] = {s.SID for s in user.Students}
        self.allowed_courses: Set[str] = {c.CID for c in user.Courses}
        self.allowed_dates: Set[datetime.date] = {d.Date for d in user.Dates}

        self.records: List[AttendanceRecord] = []
        self.admin_pass = LOADADMINPASS()
        if self.admin_pass is None:
            print("CRITICAL: UNAUTHORIZED TO LOAD DB WITHOUT ADMINPASS")

    def _has_access(self, record: AttendanceRecord) -> bool:
        if self.is_admin: return True
        if int(record.student) not in self.allowed_students: return False
        if record.course not in self.allowed_courses: return False
        if record.get_date_obj not in self.allowed_dates: return False
        return True

    def initialize_first_run(self):
        if not self.admin_pass: return
        import random
        dt_list = ["10022026", "11022026", "12022026"]
        c_list = ["SEZ305", "CSY101", "MTH202"]
        s_list = ["1111111111", "2222222222", "3333333333"]
        
        for d in dt_list:
            for c in c_list:
                for s in s_list:
                    stat = random.choice(['P', 'A'])
                    rec = AttendanceRecord(d, c, s, stat)
                    self.records.append(rec)
        self._rewrite_file()
        
    def get_distinct_ids(self) -> tuple:
        dates, courses, students = set(), set(), set()
        for r in self.records:
            dates.add(r.date)
            courses.add(r.course)
            students.add(r.student)
        return dates, courses, students
        
    def get_null_records(self) -> list:
        return [r for r in self.records if r.status == '-']

    def update_status(self, date: str, course: str, student: str, new_status: str) -> bool:
        if not self.admin_pass or not self.is_admin: return False
        if new_status not in ['P', 'A', '-']: return False
        for r in self.records:
            if r.date == date and r.course == course and r.student == student:
                r.status = new_status
                self._rewrite_file()
                return True
        return False
        
    def print_attendance_matrix(self) -> None:
        if not self.records:
            print("Database is currently empty.")
            return
            
        dates, courses, students = self.get_distinct_ids()
        sorted_dates = sorted(list(dates))
        sorted_courses = sorted(list(courses))
        sorted_students = sorted(list(students))
        
        record_map = {(r.date, r.course, r.student): r.status for r in self.records}
        
        for d in sorted_dates:
            print(f"\n{'='*15} DATE: {d} {'='*15}")
            
            header = "STUDENT ID".ljust(12) + " | "
            for c in sorted_courses:
                header += c.ljust(8)
            print(header)
            print("-" * len(header))
            
            for s in sorted_students:
                row_str = s.ljust(12) + " | "
                for c in sorted_courses:
                    status = record_map.get((d, c, s), ' ')
                    row_str += status.center(6).ljust(8)
                print(row_str)
        print()

    def admin_execute_modify(self, command: str) -> tuple:
        if not self.is_admin: return False, "Unauthorized."
        
        tokens = command.strip().upper().split()
        if len(tokens) != 2:
            return False, "Error: Command must be formatted as 'A/D + ID'"
            
        action = tokens[0]
        target_id = tokens[1]
        
        if action not in ['A', 'D']:
            return False, "Error: Unknown action. Use A or D."
            
        is_date = Validate_Date(target_id)
        is_course = Validate_Course(target_id)
        is_student = Validate_Student(target_id)
        
        if not (is_date or is_course or is_student):
            return False, "Error: The ID provided does not match 8-char Date, 6-char Course, or 10-char Student schema."
            
        dates, courses, students = self.get_distinct_ids()
        
        if action == 'D':
            if is_date and len(dates) <= 1 and target_id in dates:
                return False, "Cannot delete: Date counts cannot fall below 1."
            if is_course and len(courses) <= 1 and target_id in courses:
                return False, "Cannot delete: Course counts cannot fall below 1."
            if is_student and len(students) <= 1 and target_id in students:
                return False, "Cannot delete: Student counts cannot fall below 1."
                
            before_len = len(self.records)
            self.records = [r for r in self.records if not (
                (is_date and r.date == target_id) or 
                (is_course and r.course == target_id) or 
                (is_student and r.student == target_id)
            )]
            deleted = before_len - len(self.records)
            if deleted > 0:
                self._rewrite_file()
                return True, f"Successfully removed {deleted} intersecting records."
            return False, "No records found matching that ID."
            
        if action == 'A':
            if is_date and target_id in dates: return False, "Date already exists in database."
            if is_course and target_id in courses: return False, "Course already exists in database."
            if is_student and target_id in students: return False, "Student already exists in database."
            
            added = 0
            if is_date:
                for c in (courses or {'SEZ305'}):
                    for s in (students or {'1111111111'}):
                        self.records.append(AttendanceRecord(target_id, c, s, '-'))
                        added += 1
            elif is_course:
                for d in (dates or {'10022026'}):
                    for s in (students or {'1111111111'}):
                        self.records.append(AttendanceRecord(d, target_id, s, '-'))
                        added += 1
            elif is_student:
                for d in (dates or {'10022026'}):
                    for c in (courses or {'SEZ305'}):
                        self.records.append(AttendanceRecord(d, c, target_id, '-'))
                        added += 1
                        
            if added > 0:
                self._rewrite_file()
                return True, f"Successfully mapped and added {added} new combination records as Null ('-')."
            else:
                return False, "Failed to map new records (Missing axes)."

    def fetch_accessible_records(self) -> None:
        if not self.admin_pass: return
        self.records.clear()
        try:
            with open(self.DB_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            if self.is_admin:
                self.initialize_first_run()
                return self.fetch_accessible_records()
            return

        for line in lines:
            encrypted_str = cast(Hex, line.strip())
            if not encrypted_str: continue
            try:
                decrypted_data = DecryptS(self.admin_pass, encrypted_str)
                record = AttendanceRecord.from_string(decrypted_data)
                if self._has_access(record):
                    self.records.append(record)
            except Exception:
                pass

    def _rewrite_file(self):
        if not self.admin_pass: return
        with open(self.DB_FILE, "w", encoding="utf-8") as f:
            for r in self.records:
                enc = EncryptS(self.admin_pass, r.to_string())
                f.write(enc + "\n")

    def add_record(self, date: str, course: str, student: str, status: str = '-') -> bool:
        """Adds or updates a record."""
        if not self.admin_pass: return False
        try:
            record = AttendanceRecord(date, course, student, status)
        except ValueError as e:
            print(f"Validation Error: {e}"); return False
        
        if not self._has_access(record):
            print("Access Denied: Current user lacks permission to modify this data subset.")
            return False
            
        self.remove_record(date, course, student)
        self.records.append(record)
        self._rewrite_file()
        return True

    def remove_record(self, date: str, course: str, student: str) -> bool:
        """Removes a record from memory and rewrites the file inline."""
        if not self.admin_pass: return False
        found = None
        for r in self.records:
            if r.date == date and r.course == course and r.student == student:
                found = r; break
        if not found: return False
        if not self._has_access(found): return False
        
        self.records.remove(found)
        self._rewrite_file()
        return True

    def execute_query(self, command: str) -> tuple:
        """
        Parses custom query language: PRA/EXP + CourseID/StudentID/DateID + COUNT + A/P
        Returns (success: bool, response_string: str)
        """
        tokens = command.strip().upper().split()
        if len(tokens) < 4:
            return False, "Error: Incomplete command syntax."
            
        action = tokens[0]
        if action not in ['PRA', 'EXP']:
            return False, f"Error: Unknown action '{action}'. Must be PRA or EXP."
            
        if tokens[-2] != 'COUNT':
            return False, "Error: Missing 'COUNT' keyword before the target status."
            
        target_status = tokens[-1]
        if target_status not in ['P', 'A']:
            return False, f"Error: Unknown target status '{target_status}'. Must be P or A."
            
        filter_date = None
        filter_course = None
        filter_student = None
        
        middle_tokens = tokens[1:-2]
        if not middle_tokens:
            return False, "Error: At least one ID filter must be provided."
            
        for t in middle_tokens:
            if Validate_Date(t): filter_date = t
            elif Validate_Student(t): filter_student = t
            elif Validate_Course(t): filter_course = t
            else: return False, f"Error: Unrecognized ID token '{t}'."
            
        matched_records = []
        count = 0
        for r in self.records:
            if filter_date and r.date != filter_date: continue
            if filter_course and r.course != filter_course: continue
            if filter_student and r.student != filter_student: continue
            
            if r.status == target_status:
                matched_records.append(r)
                count += 1
                
        out_lines = []
        out_lines.append("--- QUERY EXECUTION RESULTS ---")
        out_lines.append(f"Filters Applied -> Date: {filter_date or 'ALL'}, Course: {filter_course or 'ALL'}, Student: {filter_student or 'ALL'}")
        out_lines.append(f"Targeting: {'PRESENT' if target_status == 'P' else 'ABSENT'}")
        out_lines.append(f"Matching Records Found: {count}")
        out_lines.append("-" * 30)
        
        for m in matched_records:
            out_lines.append(f"Date: {m.date} | Course: {m.course} | Student: {m.student} | Status: {m.status}")
            
        final_str = "\n".join(out_lines)
        
        if action == 'EXP':
            filename = f"Export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(final_str)
                return True, f"Success: Query exported to {filename}\nMatched Records: {count}"
            except Exception as e:
                return False, f"Error exporting to file: {e}"
                
        return True, final_str

def Load_User_Data(UserName : str) -> User:
    import json
    import datetime
    from HashEncrypt import DecryptS, LOADADMINPASS
    from DataTypes import User, StudentID, CourseID, DateID, Hex
    from typing import cast

    admin_pass = LOADADMINPASS()
    if not admin_pass:
        return User(0, UserName, b"", [], [], [])

    try:
        with open("Users.json", 'r') as uf:
            all_users = json.load(uf)
        with open("UsersData.json", 'r') as udf:
            all_users_data = json.load(udf)
    except:
        return User(0, UserName, b"", [], [], [])
        
    user_hex_key = None
    user_pass_hex = None
    for uk, up in all_users.items():
        try:
            user_pass = bytes.fromhex(up)
            if DecryptS(user_pass, cast(Hex, uk)) == UserName:
                user_hex_key = uk
                user_pass_hex = up
                break
        except: pass
        
    if not user_hex_key or user_hex_key not in all_users_data:
        return User(0, UserName, b"", [], [], [])
        
    user_data = all_users_data[user_hex_key]
    
    dirty_bit = user_data.get("DB", 0)
    
    s_list, c_list, d_list = [], [], []
    
    if "S" in user_data and isinstance(user_data["S"], list):
        for x in user_data["S"]:
            try: s_list.append(StudentID(int(DecryptS(admin_pass, cast(Hex, x)))))
            except: pass
            
    if "C" in user_data and isinstance(user_data["C"], list):
        for x in user_data["C"]:
            try: c_list.append(CourseID(DecryptS(admin_pass, cast(Hex, x))))
            except: pass
            
    if "D" in user_data and isinstance(user_data["D"], list):
        for x in user_data["D"]:
            try:
                dec_d = DecryptS(admin_pass, cast(Hex, x))
                d_obj = datetime.date(int(dec_d[4:8]), int(dec_d[2:4]), int(dec_d[0:2]))
                d_list.append(DateID(d_obj))
            except: pass

    return User(dirty_bit, UserName, bytes.fromhex(user_pass_hex), s_list, c_list, d_list)

def Validate_UserName(UserName : str) -> bool:
    if(UserName.lower() == "exit"): return False
    if(not(1 <= len(UserName) <= 15)) : return False
    if(not UserName.isalpha()) : return False
    return True