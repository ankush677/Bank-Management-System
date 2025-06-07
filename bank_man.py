import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="deepalu**15",  
        database="bank_man"
    )

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("USE bank_man")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        cus_id INT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(15)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        acc_no INT PRIMARY KEY,
        cust_id INT,
        balance DECIMAL(10,2),
        FOREIGN KEY (cust_id) REFERENCES customers(cus_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        trac_id INT PRIMARY KEY,
        acc_no INT,
        trans_type ENUM('deposit', 'withdrawal'),
        amount DECIMAL(10,2),
        FOREIGN KEY (acc_no) REFERENCES accounts(acc_no)
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created successfully.")

def add_customers():
    conn = connect_db()
    cursor = conn.cursor()

    cus_id = int(input("Enter Customer ID: "))
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")

    insert_query = "INSERT INTO customers (cus_id, name, email, phone) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_query, (cus_id, name, email, phone))

    conn.commit()
    print(f"Customer added with ID {cus_id}")

    cursor.close()
    conn.close()

def create_accounts():
    conn = connect_db()
    cursor = conn.cursor()

    acc_no = int(input("Enter Account Number: "))
    cust_id = int(input("Enter Customer ID: "))
    balance = float(input("Enter Balance: "))

    cursor.execute("SELECT * FROM customers WHERE cus_id = %s", (cust_id,))
    customer = cursor.fetchone()

    if not customer:
        print("Customer ID does not exist.")
        cursor.close()
        conn.close()
        return

    insert_query = "INSERT INTO accounts (acc_no, cust_id, balance) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (acc_no, cust_id, balance))

    conn.commit()
    print(f"Account created with acc_no {acc_no}")

    cursor.close()
    conn.close()

import decimal

def add_transactions():
    conn = connect_db()
    cursor = conn.cursor()

    trac_id = int(input("Enter transaction ID (trac_id): "))
    acc_no = int(input("Enter Account Number (acc_no): "))

    while True:
        trans_type = input("Enter transaction type (deposit/withdrawal): ").lower()
        if trans_type in ('deposit', 'withdrawal'):
            break
        else:
            print("Invalid transaction type. Please enter 'deposit' or 'withdrawal'.")

    amount = float(input("Enter amount: "))
    amount = decimal.Decimal(str(amount))

   
    cursor.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
    account = cursor.fetchone()

    if not account:
        print("Account does not exist.")
        cursor.close()
        conn.close()
        return

    current_balance = account[0]  # balance is Decimal

    if trans_type == 'deposit':
        new_balance = current_balance + amount
    elif trans_type == 'withdrawal':
        if amount > current_balance:
            print("Insufficient balance for withdrawal.")
            cursor.close()
            conn.close()
            return
        new_balance = current_balance - amount

    cursor.execute("UPDATE accounts SET balance = %s WHERE acc_no = %s", (new_balance, acc_no))

    insert_query = "INSERT INTO transactions (trac_id, acc_no, trans_type, amount) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_query, (trac_id, acc_no, trans_type, amount))

    conn.commit()
    print(f"Transaction added with ID {trac_id}")

    cursor.close()
    conn.close()

def view_account_details():
    conn = connect_db()
    cursor = conn.cursor()

    acc_no = int(input("Enter Account Number to view details: "))

    acc_query = """
    SELECT c.name, c.email, c.phone, a.acc_no, a.balance 
    FROM customers c 
    JOIN accounts a ON c.cus_id = a.cust_id 
    WHERE a.acc_no = %s
    """

    cursor.execute(acc_query, (acc_no,))
    account = cursor.fetchone()

    if account:
        print(f"Customer Name: {account[0]}")
        print(f"Email: {account[1]}")
        print(f"Phone: {account[2]}")
        print(f"Account Number: {account[3]}")
        print(f"Balance: {account[4]}")
    else:
        print("Account not found!")
        cursor.close()
        conn.close()
        return

    transaction_query = """
    SELECT trac_id, acc_no, trans_type, amount 
    FROM transactions 
    WHERE acc_no = %s 
    ORDER BY trac_id DESC
    """

    cursor.execute(transaction_query, (acc_no,))
    transactions = cursor.fetchall()

    if transactions:
        print("\nTransaction History:")
        for tr in transactions:
            print(f"Transaction ID: {tr[0]}, Account: {tr[1]}, Type: {tr[2]}, Amount: {tr[3]}")
    else:
        print("No transactions found for this account.")

    cursor.close()

def update_customers_details():
    conn = connect_db()
    cursor = conn.cursor()

    cus_id = int(input("Enter here cus_id: "))
    new_name = input("Enter your new name: ")
    new_email = input("Enter your new new email: ")
    new_phone = input("Enter your new phone number: ")

    cursor.execute("update customers set name = %s , email = %s, phone = %s where cus_id = %s",(new_name,new_email,new_phone,cus_id))

    conn.commit()
    print("Customer details updated successfully.")
    cursor.close()
    conn.close()

def delete_account():
    conn = connect_db()
    cursor = conn.cursor()

    acc_no = int(input("Enter here acc_no: "))
    
    
    cursor.execute("delete from transactions where acc_no = %s",(acc_no,))
    cursor.execute("delete from accounts where acc_no = %s",(acc_no,))
    conn.commit()
    print("Accounts deleted  successfully.")
    cursor.close()
    conn.close()


def search_customers():
    conn = connect_db()
    cursor = conn.cursor()

    search_term = input("Enter Customer ID or Name to search: ")

    
    if search_term.isdigit():
        query = "SELECT cus_id, name, email, phone FROM customers WHERE cus_id = %s"
        cursor.execute(query, (int(search_term),))
    else:
        query = "SELECT cus_id, name, email, phone FROM customers WHERE name LIKE %s"
        cursor.execute(query, ('%' + search_term + '%',))

    results = cursor.fetchall()

    if results:
        print(f"Found {len(results)} customer(s):")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Phone: {row[3]}")
    else:
        print("No customers found.")

    cursor.close()
    conn.close()

def main_menu():
    while True:
        print("\n======= BANK MANAGEMENT SYSTEM  =======")
        print("1. Add Customer")
        print("2. Create Account")
        print("3. Add Transaction")
        print("4. View Account Details")
        print("5. update customers detaisl")
        print("6. delete accounts")
        print("7. search customers")
        print("8. Exit")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            add_customers()
        elif choice == 2:
            create_accounts()
        elif choice == 3:
            add_transactions()
        elif choice == 4:
            view_account_details()
        elif choice == 5:
            update_customers_details()
        elif choice == 6:
            delete_account()
        elif choice == 7:
            search_customers()
        elif choice == 8:
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

main_menu()