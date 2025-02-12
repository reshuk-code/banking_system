from connect import connect_db
import random
from send_mail import send_account_creation_email, send_login_notification_email, send_transaction_email

# Connect to the database
db = connect_db()
accounts = db["accounts"]
deposit_requests = db["deposit_requests"]

# Predefined admin account
ADMIN_ACCOUNT = {
    "first_name": "admin",
    "last_name": "admin",
    "email": "admin@bank.com",
    "password": "admin1230",
    "account_type": "admin",
    "balance": 0,  # Admin's balance starts at 0
    "account_number": 1000000000000000  # Admin's account number
}

# Ensure the admin account exists
if not accounts.find_one({"account_number": ADMIN_ACCOUNT["account_number"]}):
    accounts.insert_one(ADMIN_ACCOUNT)

def generate_account_number():
    """Generate a unique 16-digit account number."""
    while True:
        account_number = random.randint(10**15, (10**16) - 1)  # Generate a 16-digit number
        if not accounts.find_one({"account_number": account_number}):  # Ensure uniqueness
            return account_number

def create_account():
    print("\nCreating account")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    account_type = input("Enter account type (savings/current): ")
    balance = float(input("Enter initial balance: ") or 0)  # Default balance to 0 if not provided
    
    account_number = generate_account_number()
    
    account = {
        "account_number": account_number,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "account_type": account_type,
        "balance": balance,
        "haveCard": False,
    }
    
    # Deduct the initial balance from the admin account
    admin_account = accounts.find_one({"account_number": ADMIN_ACCOUNT["account_number"]})
    admin_account["balance"] += balance
    accounts.update_one({"account_number": ADMIN_ACCOUNT["account_number"]}, {"$set": {"balance": admin_account["balance"]}})
    
    accounts.insert_one(account)
    print("\nAccount created successfully!")
    print("Your account number is:", account_number)
    send_account_creation_email(email, first_name, account_number)

def login():
    print("\nLogin to your account")
    account_number = input("Enter your 16-digit account number: ")
    password = input("Enter your password: ")
    
    account = accounts.find_one(
        {"account_number": int(account_number), "password": password},
        {"account_number": 1, "email": 1, "first_name": 1, "account_type": 1, "balance": 1}
    )
    
    if account:
        print("\nLogin successful!")
        if account["account_type"] == "admin":
            admin_menu(account)
        else:
            user_menu(account)
        
        # Send login notification email
        send_login_notification_email(account["email"], account["first_name"])
    else:
        print("\nInvalid account number or password.")

def admin_menu(admin_account):
    while True:
        print("\nAdmin Menu")
        print("1. Deposit Money to User")
        print("2. View All Accounts")
        print("3. Process Deposit Requests")
        print("4. Logout")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            deposit_to_user(admin_account)
        elif choice == "2":
            view_all_accounts()
        elif choice == "3":
            process_deposit_requests(admin_account)
        elif choice == "4":
            print("\nLogging out...")
            break
        else:
            print("\nInvalid choice.")

def deposit_to_user(admin_account):
    user_account_number = input("Enter the user's 16-digit account number: ")
    amount = float(input("Enter the amount to deposit: "))
    
    user_account = accounts.find_one({"account_number": int(user_account_number)})
    
    if user_account and amount > 0:
        user_account["balance"] += amount
        admin_account["balance"] -= amount
        accounts.update_one({"account_number": user_account["account_number"]}, {"$set": {"balance": user_account["balance"]}})
        accounts.update_one({"account_number": ADMIN_ACCOUNT["account_number"]}, {"$set": {"balance": admin_account["balance"]}})
        print(f"\n${amount:.2f} deposited to user {user_account['first_name']} {user_account['last_name']}.")
        send_transaction_email(user_account["email"], user_account["first_name"], amount, "yourself")
    else:
        print("\nInvalid account number or amount.")

def view_all_accounts():
    print("\nAll Accounts:")
    for account in accounts.find():
        print(f"Account Number: {account['account_number']}, Name: {account['first_name']} {account['last_name']}, Balance: RS {account['balance']:.2f}")

def process_deposit_requests(admin_account):
    print("\nPending Deposit Requests:")
    for request in deposit_requests.find({"status": "pending"}):
        print(f"Request ID: {request['_id']}, Amount: RS {request['amount']:.2f}, From: {request['from_account_number']}, To: {request['to_account_number']}")
    
    request_id = input("Enter the request ID to process (or 'cancel' to go back): ")
    if request_id.lower() == "cancel":
        return
    
    try:
        # Convert request_id to ObjectId if necessary
        from bson import ObjectId
        request_id = ObjectId(request_id)
    except Exception as e:
        print("\nInvalid request ID format.")
        return
    
    request = deposit_requests.find_one({"_id": request_id, "status": "pending"})
    if request:
        from_account = accounts.find_one({"account_number": request["from_account_number"]})
        to_account = accounts.find_one({"account_number": request["to_account_number"]})
        
        if from_account and to_account:
            if to_account["balance"] >= request["amount"]:
                to_account["balance"] -= request["amount"]
                from_account["balance"] += request["amount"]
                
                accounts.update_one({"account_number": from_account["account_number"]}, {"$set": {"balance": from_account["balance"]}})
                accounts.update_one({"account_number": to_account["account_number"]}, {"$set": {"balance": to_account["balance"]}})
                
                deposit_requests.update_one({"_id": request_id}, {"$set": {"status": "completed"}})
                print("\nDeposit request processed successfully!")
            else:
                print("\nInsufficient balance in the recipient's account.")
        else:
            print("\nInvalid accounts in the request.")
    else:
        print("\nInvalid request ID.")

def user_menu(user_account):
    while True:
        print("\nUser Menu")
        print("1. Check Balance")
        print("2. Send Money")
        print("3. Request Deposit")
        print("4. Logout")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            print(f"\nYour current balance is: ${user_account['balance']:.2f}")
        elif choice == "2":
            send_money(user_account)
        elif choice == "3":
            request_deposit(user_account)
        elif choice == "4":
            print("\nLogging out...")
            break
        else:
            print("\nInvalid choice.")

def send_money(user_account):
    recipient_account_number = input("Enter the recipient's 16-digit account number: ")
    amount = float(input("Enter the amount to send: "))
    
    recipient_account = accounts.find_one({"account_number": int(recipient_account_number)})
    
    if recipient_account and amount > 0 and user_account["balance"] >= amount:
        user_account["balance"] -= amount
        recipient_account["balance"] += amount
        
        accounts.update_one({"account_number": user_account["account_number"]}, {"$set": {"balance": user_account["balance"]}})
        accounts.update_one({"account_number": recipient_account["account_number"]}, {"$set": {"balance": recipient_account["balance"]}})
        
        print(f"\n${amount:.2f} sent to {recipient_account['first_name']} {recipient_account['last_name']}.")
        send_transaction_email(user_account["email"], user_account["first_name"], amount, f"{recipient_account['first_name']} {recipient_account['last_name']}")
    else:
        print("\nInvalid account number, amount, or insufficient balance.")

def request_deposit(user_account):
    from_account_number = input("Enter the account number to request money from: ")
    amount = float(input("Enter the amount to request: "))
    
    from_account = accounts.find_one({"account_number": int(from_account_number)})
    
    if from_account and amount > 0:
        deposit_requests.insert_one({
            "from_account_number": from_account["account_number"],
            "to_account_number": user_account["account_number"],
            "amount": amount,
            "status": "pending"
        })
        print("\nDeposit request submitted. Waiting for admin approval.")
    else:
        print("\nInvalid account number or amount.")

def ask_choice():
    user_choice = input("\n1. Create Account\n2. Login\n3. Exit\nEnter your choice: ")
    if user_choice == "1":
        create_account()
    elif user_choice == "2":
        login()
    elif user_choice == "3" or user_choice.lower() == "/exit":
        return False  # Exit the loop
    else:
        print("\nInvalid choice.")
    return True  # Continue the loop

# Main loop
print("Welcome to Bank of Congroo.aus")
while True:
    if not ask_choice():
        print("\nThank you for using Bank of Congroo.aus. Goodbye!")
        break