# Attendance-Manager-DBMS-Py

This is a ACID DBMS implemented in Python.
It is terminal based and comes with a dummy database upon first startup.

The base user is Admin and the password for testing is - Admin76$

It has mutliple features, you can check them out via running the codebase.

Execute the main.py file to run the software.

It is designed with a fixed memoery usage in mind and doesn't use recursion to ensure the callstack doesn't grow out of bounds.

I have shipped another user Peter with password - Peter76$

To create test DB, delete the attendance_data.txt
To create clean Users, delete the Users.json and UsersData.json files. Admin with the default password will be loaded by default.

# The Data

StudentID = 10 Digits,
CourseID = 3 Alphabets + 3 Digits,
DateID = DDMMYYYY

This makes a Composite Primary Key of = StudentID | CourseID | DateID
for each Attendance Record

The data is stored as a Sparce Matrix with only Absent records, as in any ideal situation Total Present > Total Absent, so storage is minimised.

# DataBase Queries (Admin Only)

A/D + ID

A = Add,
D = Delete

ID will be accoring to the datatypes and will be auto-detected

# Attendance Queries (All Users)

PRA/EXP + ID(s) + COUNT + P/A

PRA = Print to Terminal,
EXP = Export to Txt File

ID will be at least one of a single type, different types can be given with a space. Only 1 of each type is allowed at max

COUNT is a fixed keyword

P = Present,
A = Absent

# Safety (Hashing + Encryption)

We use Bcrypt to Hash the passwords and use a pepper Brute force approach to Stop Brute Force & Rainbow Table attacks.
This allows data to only be loaded if a successful login occurs.

We use ChaCha20-Poly1305 for Encryption to ensure no data is stored naked and thus succeptible to unauthorized access.

There are strict Access checks for all users. A user may only access a record if they have access to the full Key corresponding to it.
