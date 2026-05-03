import SessionMAN

'''
0 > Restart Menu
-1 > Successful Exit
(others) > UnSuccessful Exit due to Core Process Failure
... Listed Below-
1 > FileNotFoundError
2 > OSError
3 > Value error
'''

'''
Core Proceses:
401 > LOAD_ADMINPASS()

'''

def main():
    exit_code : int = 0
    while(not exit_code):
        exit_code = SessionMAN.MainMenu()
        if exit_code > 400:
            ... # Use logging to log errors

if __name__ == "__main__" :
    main()