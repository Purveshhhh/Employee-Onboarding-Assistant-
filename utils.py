import json
import os
import datetime
import hashlib

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ── AUTH SYSTEM ──────────────────────────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    path = os.path.join(DATA_DIR, "users.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_users(users):
    path = os.path.join(DATA_DIR, "users.json")
    with open(path, "w") as f:
        json.dump(users, f, indent=2)

def register_user(username, password, full_name, email, role="Employee"):
    users = load_users()
    if username in users:
        return False, "Username already exists. Please choose a different username."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if not username.strip():
        return False, "Username cannot be empty."
    users[username] = {
        "password":   hash_password(password),
        "full_name":  full_name,
        "email":      email,
        "role":       role,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_users(users)
    return True, "Account created successfully!"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found. Please sign up first."
    if users[username]["password"] != hash_password(password):
        return False, "Incorrect password. Please try again."
    return True, users[username]

# ── EMPLOYEE DATA ────────────────────────────────────────────────────────────

def save_employee(username, data):
    path = os.path.join(DATA_DIR, "employees.json")
    employees = load_employees()
    employees[username] = data
    with open(path, "w") as f:
        json.dump(employees, f, indent=2)

def load_employees():
    path = os.path.join(DATA_DIR, "employees.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

# ── TASK PROGRESS ────────────────────────────────────────────────────────────

def save_task_progress(username, tasks):
    path = os.path.join(DATA_DIR, f"tasks_{username}.json")
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)

def load_task_progress(username):
    path = os.path.join(DATA_DIR, f"tasks_{username}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

# ── TRAINING PROGRESS ────────────────────────────────────────────────────────

def save_training_progress(username, data):
    path = os.path.join(DATA_DIR, f"training_{username}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_training_progress(username):
    path = os.path.join(DATA_DIR, f"training_{username}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

# ── DOCUMENT GENERATION ──────────────────────────────────────────────────────

def generate_offer_letter(emp, annual_ctc):
    monthly = annual_ctc // 12
    basic   = int(monthly * 0.4)
    hra     = int(monthly * 0.2)
    special = int(monthly * 0.3)
    pf      = int(monthly * 0.1)
    today   = datetime.date.today().strftime("%d %B %Y")

    return f"""
HCL TECHNOLOGIES LIMITED
Registered Office: 806, Siddharth, 96 Nehru Place, New Delhi - 110019
CIN: L74140DL1976PLC008503

Date: {today}

OFFER LETTER

To,
{emp.get('full_name', '____________________')}
{emp.get('address', '____________________')}
{emp.get('city', '')}, {emp.get('state', '')} - {emp.get('pincode', '')}

Dear {emp.get('full_name', 'Candidate')},

Subject: Offer of Employment — {emp.get('designation', '____________________')}

We are pleased to inform you that you have been selected for the position of
{emp.get('designation', '____________________')} in the {emp.get('department', '____________________')} 
department at HCL Technologies Limited.

TERMS AND CONDITIONS OF EMPLOYMENT:
────────────────────────────────────────────────────────────
Employee ID        : {emp.get('emp_id', '____________________')}
Designation        : {emp.get('designation', '____________________')}
Department         : {emp.get('department', '____________________')}
Date of Joining    : {emp.get('joining_date', '____________________')}
Work Location      : HCL Technologies, Indore
Employment Type    : Full-Time, Permanent

COMPENSATION DETAILS (Annual CTC: ₹{annual_ctc:,}):
────────────────────────────────────────────────────────────
Component                Monthly (₹)     Annual (₹)
Basic Salary             {basic:>10,}     {basic*12:>10,}
House Rent Allowance     {hra:>10,}     {hra*12:>10,}
Special Allowance        {special:>10,}     {special*12:>10,}
Provident Fund           {pf:>10,}     {pf*12:>10,}
─────────────────────────────────────────────────────
Total                    {monthly:>10,}     {annual_ctc:>10,}

OTHER BENEFITS:
────────────────────────────────────────────────────────────
• Mediclaim Insurance: ₹5,00,000 per year (self + family)
• Life Insurance: ₹50,00,000 term cover
• Annual Performance Bonus: Based on appraisal rating
• 18 Days Paid Leave + 7 Days Sick Leave per year
• Meal Card: ₹2,200 per month
• Learning & Development Budget: ₹20,000 per year

CONDITIONS:
────────────────────────────────────────────────────────────
1. This offer is subject to successful completion of background verification.
2. You are required to submit all original documents on the date of joining.
3. The probation period shall be 6 months from the date of joining.
4. During probation, either party may terminate employment with 2 weeks notice.
5. Post-confirmation, notice period shall be 3 months.

Please sign and return a copy of this letter as acceptance of the offer.

Congratulations and welcome to the HCL family!

Yours sincerely,

________________________________
[HR Manager Name]
HR Department
HCL Technologies Limited
hr@hcltech.com | 1800-425-3300

────────────────────────────────────────────────────────────
ACCEPTANCE

I, {emp.get('full_name', '____________________')}, accept the above offer of employment.

Signature: ____________________    Date: ____________________
"""

def generate_joining_form(emp):
    today = datetime.date.today().strftime("%d %B %Y")
    return f"""
HCL TECHNOLOGIES LIMITED
EMPLOYEE JOINING FORM

Date: {today}
────────────────────────────────────────────────────────────

SECTION A — PERSONAL DETAILS
────────────────────────────────────────────────────────────
Full Name            : {emp.get('full_name', '')}
Employee ID          : {emp.get('emp_id', '')}
Date of Birth        : {emp.get('dob', '')}
Gender               : {emp.get('gender', '')}
Mobile Number        : {emp.get('phone', '')}
Personal Email       : {emp.get('email', '')}
Company Email        : {emp.get('company_email', '')}

SECTION B — EMPLOYMENT DETAILS
────────────────────────────────────────────────────────────
Department           : {emp.get('department', '')}
Designation          : {emp.get('designation', '')}
Date of Joining      : {emp.get('joining_date', '')}
Work Location        : HCL Technologies, Indore

SECTION C — ADDRESS DETAILS
────────────────────────────────────────────────────────────
Permanent Address    : {emp.get('address', '')}
City                 : {emp.get('city', '')}
State                : {emp.get('state', '')}
PIN Code             : {emp.get('pincode', '')}
Country              : {emp.get('country', 'India')}

SECTION D — BANK DETAILS
────────────────────────────────────────────────────────────
Bank Name            : {emp.get('bank_name', '')}
Account Type         : {emp.get('account_type', '')}
IFSC Code            : {emp.get('ifsc', '')}
Branch               : {emp.get('branch', '')}

SECTION E — TAX & STATUTORY DETAILS
────────────────────────────────────────────────────────────
PAN Number           : {emp.get('pan_number', '')}
Aadhaar (last 4)     : XXXX XXXX {emp.get('aadhar', '____')}
PF Number            : {emp.get('pf_number', 'Will be assigned')}
UAN Number           : {emp.get('uan_number', 'Will be assigned')}

SECTION F — EMERGENCY CONTACT
────────────────────────────────────────────────────────────
Contact Name         : {emp.get('emergency_name', '')}
Relationship         : {emp.get('emergency_rel', '')}
Contact Phone        : {emp.get('emergency_phone', '')}

SECTION G — DECLARATION
────────────────────────────────────────────────────────────
I hereby declare that all the information provided above is true and correct 
to the best of my knowledge. I understand that any false information may 
result in termination of employment.

Signature: ____________________    Date: ____________________

FOR HR USE ONLY:
────────────────────────────────────────────────────────────
Documents Verified By : ____________________
Date                  : ____________________
HR Signature          : ____________________
"""
