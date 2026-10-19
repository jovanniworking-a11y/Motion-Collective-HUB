import datetime

def make_patient(pid, first, last, dob, phone, today=None):
    today = today or datetime.date.today()
    ...

def age(dob, today):
    ...
