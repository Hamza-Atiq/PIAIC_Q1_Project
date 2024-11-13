from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime 
from typing import List, Optional 
import json
from decimal import Decimal
from dataclasses import dataclass

# ------------------------------------- Data Storage ----------------------------------------------------------

class DataStorage(ABC):

    """
    Abstract base class for data storage operations.
    Provides an interface for loading and saving data.
    """

    def __init__(self , file_path : Path):

        """
        Initializes the data storage with a file path.
        
        Parameters:
        file_path (Path): Path to the storage file.
        """

        self.file_path = file_path  # Path to the file where data is stored.

    @abstractmethod
    def load_data(self) -> dict:

        """
        Load data from storage.
        
        Returns:
        dict: Loaded data.
        """
        pass

    @abstractmethod
    def save_data(self , data : dict) -> None:

        """
        Save data to storage.
        
        Parameters:
        data (dict): Data to be saved.
        """
        pass

# ------------------------------------ Data Storage in JSON --------------------------------------------------

class JSONStorage(DataStorage):

    """
    Concrete implementation of data storage using JSON files.
    This class manages data by reading from and writing to JSON files.
    """

    def load_data(self) -> dict:

        """
        Load user data (username and password) from the JSON file if it exists.
        Returns a dictionary with usernames as keys and user details as values.
        
        Returns:
        dict: Dictionary of loaded data, or empty if file is missing or corrupted.
        """

        if self.file_path.exists():  # Check if file exists before attempting to load data
            try:
                # Read the contents of the JSON file as text
                contents: str = self.file_path.read_text()

                # Parse the JSON content into a Python dictionary
                data: dict = json.loads(contents)
                return data  # Return the loaded data
            
            except json.JSONDecodeError:
                # Handle JSON decoding errors if the file is corrupted or empty
                print(f"Error reading {self.file_path.name}. Using empty data.")
                return {}
        
        # If the file does not exist, return an empty dictionary
        return {}
    
    def save_data(self , data : dict) -> None:

        """
        Save the entire user data dictionary to the JSON file.
        
        Parameters:
        data (dict): Data dictionary to save.
        """

        try:
            # Write JSON-formatted user data to the file with indentation for readability
            self.file_path.write_text(json.dumps(data, indent=4))
            print(f"User data saved successfully to {self.file_path.name}")
        except (PermissionError, IOError) as e:
            print(f"Failed to save data: {e}")

# ------------------------------- Transaction Item Class ------------------------------------------------------

@dataclass
class TransactionItem:

    """
    Class to represent an item in a transaction
    """

    product_id : str
    quantity : int
    unit_price : Decimal
    total_price : Decimal  # Total cost for this item (unit_price * quantity)

# -------------------------------------- Transaction Class -------------------------------------------------

class Transaction:

    """
    Class to handle individual transactions
    """
    
    def __init__(self , transaction_id : str , cashier : str):

        """
        Initializes a transaction with a unique ID and cashier.
        
        Parameters:
        transaction_id (str): Unique identifier for the transaction.
        cashier (str): Name or ID of the cashier handling the transaction.
        """

        self._transaction_id = transaction_id
        self._cashier = cashier
        self._items: List[TransactionItem] = []  # List to store items in the transaction
        self._timestamp = datetime.now()
        self._total_amount = Decimal('0.00')  # Accumulated cost of all items
        self._payment_received = Decimal('0.00')  # Payment received from customer
        self._change = Decimal('0.00')  # Change to return to the customer after payment
        
    def add_item(self , item : TransactionItem):

        """
        Adds an item to the transaction and updates the total amount.
        
        Parameters:
        item (TransactionItem): The item being added to the transaction.
        """

        self._items.append(item)
        self._total_amount += item.total_price  # Update total with item's total price
        
    def process_payment(self , amount_received : Decimal):

        """
        Process the payment by setting the amount received and calculating change.
        
        Parameters:
        amount_received (Decimal): The amount received from the customer.
        """

        if amount_received < self._total_amount:
            raise ValueError("Insufficient payment received.")
        
        self._payment_received = amount_received
        self._change = amount_received - self._total_amount  # Calculate the change
        
    def to_dict(self) -> dict:

        """
        Converts the transaction details into a dictionary format.
        
        Returns:
        dict: A dictionary representing the transaction.
        """

        return {
            "transaction_id" : self._transaction_id,
            "cashier" : self._cashier,
            "timestamp" : self._timestamp.isoformat(),
            "items" : [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "total_price": str(item.total_price)
                }
                for item in self._items
            ],
            "total_amount" : str(self._total_amount),
            "payment_received" : str(self._payment_received),
            "change" : str(self._change)
        }
    
# ------------------------------- Transaction Manager Class ------------------------------------------------

class TransactionManager: 

    """
    Class to manage all transactions
    """
    
    def __init__(self): 

        """
        Initializes the transaction manager with a storage backend.
        
        Parameters:
        storage_path (Path): Path to the JSON file for storing transaction data.
        """

        self._storage = JSONStorage(Path(r'D:\AI in 2024\PIAIC\quarter 1\Project\transactions.json'))  # JSON storage for transactions
        
    def save_transaction(self, transaction : Transaction):

        """
        Save a transaction to storage.
        
        Parameters:
        transaction (Transaction): The transaction to save.
        """

        transactions = self._storage.load_data()
        transactions[transaction._transaction_id] = transaction.to_dict()
        self._storage.save_data(transactions)
        
    def get_daily_sales_report(self , date : datetime) -> dict:

        """
        Generate daily sales report for the given date.
        
        Parameters:
        date (datetime): Date for which to generate the sales report.
        
        Returns:
        dict: Report including total sales, transactions count, and items sold.
        """

        transactions = self._storage.load_data()
        daily_transactions = {
            k : v for k , v in transactions.items()
            if datetime.fromisoformat(v["timestamp"]).date() == date.date()
        }
        
        total_sales = sum(Decimal(t["total_amount"]) for t in daily_transactions.values())
        total_items = sum(
            sum(item["quantity"] for item in t["items"])
            for t in daily_transactions.values()
        )
        
        return {
            "date": date.date().isoformat(),
            "total_sales": str(total_sales),
            "total_transactions": len(daily_transactions),
            "total_items_sold": total_items,
            "transactions": daily_transactions
        }
        
    def get_monthly_sales_report(self , year : int , month : int) -> dict:

        """
        Generate monthly sales report for a given year and month.
        
        Parameters:
        year (int): Year for the report.
        month (int): Month for the report.
        
        Returns:
        dict: Report including total sales, transaction counts, and daily totals.
        """

        transactions = self._storage.load_data()

        monthly_transactions = {
            k : v for k, v in transactions.items()
            if datetime.fromisoformat(v["timestamp"]).year == year
            and datetime.fromisoformat(v["timestamp"]).month == month
        }
        
        daily_totals = {}
        for t in monthly_transactions.values():
            date = datetime.fromisoformat(t["timestamp"]).date()
            if date not in daily_totals:
                daily_totals[date] = Decimal('0.00')
            daily_totals[date] += Decimal(t["total_amount"])
            
        return {
            "year": year,
            "month": month,
            "total_sales": str(sum(daily_totals.values())),
            "total_transactions" : len(monthly_transactions),
            "daily_totals": {str(k): str(v) for k, v in daily_totals.items()}
        }

# ------------------------------------ User Management --------------------------------------------------------
 
class User:

    """
    Base class for user management.
    Manages user roles, authentication, and registration.
    """

    def __init__(self, username: str, password: str):

        """
        Initialize a user with a username and password, assigns role based on username.
        
        Parameters:
        username (str): The user's unique username.
        password (str): The user's password.
        """

        # Initialize username and password
        self._username = username
        self._password = password

        # Set role based on username, 'Admin' for 'admin' username, otherwise 'Salesman'
        self._role = self._determine_role()

        # Path to store user data in a JSON file
        self._storage = JSONStorage(Path(r"D:\AI in 2024\PIAIC\quarter 1\Project\userdata.json"))

    @property
    def username(self) -> str:

        """
        Provides read-only access to the username.
        """

        return self._username
    
    @property
    def role(self) -> str:

        """
        Provides read-only access to the user role.
        """

        return self._role
    
    def _determine_role(self) -> str:

        """
        Assigns 'Admin' role to 'admin' username, otherwise assigns 'Salesman'.
        """

        return "Admin" if self._username == "admin" else "salesman"

    def authenticate(self) -> bool:

        """
        Authenticate existing users or create a new one if the username doesn't exist.
        
        Returns:
        bool: True if the user is successfully authenticated or created, False otherwise.
        """

        user_data: dict = self._storage.load_data()  # Load existing user data from storage

        # First-time setup: If no user data exists and username is 'admin', create admin
        if not user_data and self.username == "admin":
            user_data[self._username] = {
                "password": self._password, 
                "role": "Admin"
            }
            self._storage.save_data(user_data)  # Save new admin user data
            print(f"Welcome, {self._username}! Your account has been created as an Admin.")
            return True

        # Check if username exists and verify password
        if self._username in user_data:
            stored_password: str = user_data[self._username]["password"]
            if stored_password == self._password:
                # Authentication successful
                print(f"Welcome back, {self._username}!")
                self._role = user_data[self._username]['role']  # Update user role
                return True
        
        print("Authentication failed. Incorrect username or password.")
        return False
    
    def register(self) -> bool:

        """
        Registers a new user if username is not already taken.
        
        Returns:
        bool: True if registration is successful, False otherwise.
        """

        # Prevent creation of additional 'Admin' users
        if self._username.lower() == 'admin':
            print('Admin user already exists. Cannot create another admin.')
            return False
        
        user_data: dict = self._storage.load_data()  # Load existing user data

        if self._username in user_data:
            print("Username already exists.")
            return False

        # Create a new 'Salesman' user
        user_data[self._username] = {
            "password": self._password,
            "role": "salesman"
        }

        self._storage.save_data(user_data)  # Save the new user data
        print(f'Welcome, {self._username}! Your account has been created as a Salesman.')
        return True

class Product:

    """
    Class representing a product in the inventory.
    """

    def __init__(self, product_id: str, name: str, category: str, price: Decimal, 
                 quantity: int, expiry_date: str):
        
        """
        Initialize a product with basic attributes.
        
        Parameters:
        product_id (str): Unique identifier for the product.
        name (str): Name of the product.
        category (str): Product category (e.g., "Food", "Beverage").
        price (Decimal): Unit price of the product.
        quantity (int): Quantity of product in stock.
        expiry_date (str): Expiry date for the product (if applicable).
        """

        self._product_id = product_id
        self._name = name
        self._category = category
        self._price = price  # Using Decimal for monetary values is recommended
        self._quantity = quantity
        self._expiry_date = expiry_date  # Date should ideally be validated as 'YYYY-MM-DD'

    @property
    def to_dict(self) -> dict:

        """
        Converts product details to a dictionary format for JSON serialization or storage.
        
        Returns:
        dict: A dictionary containing product details.
        """

        return {
            "product_id": self._product_id,
            "name": self._name,
            "category": self._category,
            "price": str(self._price),  # Convert Decimal to string for JSON compatibility
            "quantity": self._quantity,
            "expiry_date": self._expiry_date
        }

# ------------------------------ Billing class --------------------------------------------------------------

class Billing:

    """
    Class to handle billing operations including creating bills, processing payments,
    and printing receipts.
    """

    def __init__(self, inventory: 'Inventory', transaction_manager: TransactionManager):

        """
        Initializes the Billing instance with inventory and transaction management.

        Parameters:
        inventory (Inventory): The inventory system to retrieve product details.
        transaction_manager (TransactionManager): The manager to save and retrieve transactions.
        """

        self._inventory = inventory
        self._transaction_manager = transaction_manager
        
    def create_bill(self, cashier: str) -> Optional[Transaction]:

        """
        Create a new bill for a customer.

        Parameters:
        cashier (str): Name of the cashier processing the transaction.

        Returns:
        Optional[Transaction]: The completed Transaction object if successful, None if no items.
        """

        # Generate a unique transaction ID
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        transaction = Transaction(transaction_id, cashier)
        
        while True:
            product_id = input("Enter Product ID (or 'done' to finish): ")
            if product_id.lower() == 'done':
                break

            try:
                # Input validation for quantity
                quantity = int(input("Enter quantity: "))
                if quantity <= 0:
                    print("Quantity must be positive.")
                    continue

                # Retrieve product details from inventory
                inventory = self._inventory._storage.load_data()
                if product_id not in inventory:
                    print("Product not found.")
                    continue

                product = inventory[product_id]
                if int(product["quantity"]) < quantity:
                    print("Insufficient stock.")
                    continue

                # Calculate item total
                unit_price = Decimal(str(product["price"]))
                total_price = unit_price * Decimal(str(quantity))

                # Add item to transaction
                item = TransactionItem(product_id, quantity, unit_price, total_price)
                transaction.add_item(item)

                # Update inventory to reflect sale
                self._inventory.adjust_stock(product_id, -quantity)
                
                print(f"Added {quantity} x {product['name']}")
                print(f"Current total: {transaction._total_amount} Rs")

            except ValueError:
                print("Invalid input. Please enter a valid number for quantity.")
                continue
        
        if not transaction._items:
            print("No items in bill.")
            return None

        # Process payment
        while True:
            try:
                payment = Decimal(input(f"Total amount: {transaction._total_amount} Rs\nEnter payment amount: Rs"))
                if payment < transaction._total_amount:
                    print("Insufficient payment.")
                    continue
                transaction.process_payment(payment)
                break
            except ValueError:
                print("Invalid payment amount. Please enter a valid number.")

        # Save the transaction
        self._transaction_manager.save_transaction(transaction)

        # Print the receipt
        self._print_receipt(transaction)

        return transaction
        
    def _print_receipt(self, transaction: Transaction):

        """
        Print the transaction receipt.

        Parameters:
        transaction (Transaction): The completed transaction to print.
        """

        print("\n" + "="*40)
        print(f"Receipt #{transaction._transaction_id}")
        print(f"Date: {transaction._timestamp}")
        print(f"Cashier: {transaction._cashier}")
        print("-"*40)
        
        inventory = self._inventory._storage.load_data()

        # Print details of each item in the transaction
        for item in transaction._items:
            product = inventory[item.product_id]
            print(f"{product['name']}")
            print(f"{item.quantity} x {item.unit_price} = {item.total_price} Rs")
        
        print("-"*40)
        print(f"Total Amount: {transaction._total_amount} Rs")
        print(f"Payment Received: {transaction._payment_received} Rs")
        print(f"Change: {transaction._change} Rs")
        print("="*40 + "\n")


# ----------------------------- Inventory Class -------------------------------------------------------------

class Inventory:

    """
    Class managing product inventory operations
    """

    def __init__(self):

        self._storage = JSONStorage(Path("D:\AI in 2024\PIAIC\quarter 1\Project\inventory.json"))
        self._low_stock_threshold = 5

    def add_product(self , product : Product ) -> bool:

        inventory : dict = self._storage.load_data()

        if product._product_id in inventory:

            # If the product ID already exists, print message
            print(f"Product with ID {product._product_id} already exists in inventory.")
            return False
        
        inventory[product._product_id] = product.to_dict
        self._storage.save_data(inventory)
        return True
    
    def update_prodcut(self , product_id : str , **updates) -> bool:

        """
        Update product attributes (e.g., price, quantity) based on provided keyword arguments.
        """
        inventory = self._storage.load_data()

        if product_id not in inventory:
            print(f"Prodcut ID {product_id} not found.")
            return False
        
        inventory[product_id].update(updates)
        self._storage.save_data(inventory)
        return True
    
    def delete_product(self , product_id : str) -> bool:

        inventory = self._storage.load_data()

        if product_id not in inventory:
            print(f"Prodcut Id {product_id} not found.")
            return False
        
        del inventory[product_id]
        self._storage.save_data(inventory)
        return True
    
    def adjust_stock(self , product_id : str , quantity_change : int) -> bool:

        """
        Adjust the stock quantity for a specific product by a given amount (positive for restock, negative for sale).
        If stock is low after adjustment, print a low stock warning.
        """
        inventory = self._storage.load_data()

        if product_id not in inventory:
            print(f"Prodcut Id {product_id} not found.")
            return False

        new_quantity = int(inventory[product_id]["quantity"]) + quantity_change

        if new_quantity < 0:
            print("Cannot reduce stock below 0.")
            return False
        
        inventory[product_id]["quantity"] = new_quantity

        if new_quantity <= self._low_stock_threshold:
            print(f"Low stock alert for {inventory[product_id]["name"]} !")

        self._storage.save_data(inventory)
        return True
    
    def search_products(self , criteria : str  , value : str) -> List[dict]:

        inventory = self._storage.load_data()

        items = [product for product in inventory.values() 
                 if str(product.get(criteria , "")).lower() == value.lower()]
        return items
    
    def get_low_stock_products(self) -> List[dict]:

        inventory = self._storage.load_data()

        items = [product for product in inventory.values() 
                 if product["quantity"] <= self._low_stock_threshold]
        return items
    
    def get_expiring_products(self , days : int = 30) -> List[dict]:

        inventory = self._storage.load_data()
        today = datetime.now()

        items = [product for product in inventory.values()
                 if (datetime.strptime(product["expiry_date"] , "%Y-%m-%d") - today).days <= days]
        
        return items
    
    def get_daily_purchase_report(self, date: datetime) -> List[dict]:

        """
        Generate daily purchase report based on stock adjustments.
        
        Parameters:
            date (datetime): The date for which to generate the report.
        
        Returns:
            List[dict]: A list of dictionaries, each representing a purchase or restocking event.
        """

        inventory = self._storage.load_data()
        purchase_events = []

        # Loop through each product in the inventory to check for restocking events
        for product_id, product_data in inventory.items():
            
            # Assuming product_data has a 'restocking_history' key with a list of restocking events
            # Example: product_data["restocking_history"] = [{'date': '2024-11-10', 'quantity': 10, 'price': 50.0}]
            if "restocking_history" in product_data:
                
                # Filter restocking events for the specified date
                for event in product_data["restocking_history"]:
                    restock_date = datetime.strptime(event['date'], "%Y-%m-%d")
                    
                    # Check if this restock event happened on the specified date
                    if restock_date.date() == date.date():
                        purchase_event = {
                            "product_id": product_id,
                            "product_name": product_data["name"],
                            "quantity_restocked": event["quantity"],
                            "price_per_unit": event["price"],
                            "total_cost": event["quantity"] * event["price"],
                            "date": event["date"]
                        }
                        purchase_events.append(purchase_event)

        return purchase_events
    
# ----------------------------- Main Inventory Management system Class --------------------------------------

class InventoryManagementSystem:

    """
    Main system class coordinating user interaction and inventory operations
    """

    def __init__(self):

        self._inventory = Inventory()
        self._transaction_manager = TransactionManager()
        self._billing = Billing(self._inventory, self._transaction_manager)
        self._current_user: Optional[User] = None

    def login(self , username : str , password : str) -> bool:

        user = User(username , password)

        if user.authenticate():
            self._current_user = user
            print(f"Welcome , {username} !")
            return True
        return False
    
    def register(self , username : str , password : str ) -> bool:

        user = User(username , password)
        return user.register()
    
    def run(self):
        while True:
            print("\n=== Inventory Management System ===")
            print("1. Login")
            print("2. Register")
            print("3. Exit")

            choice = input("Enter you choice (1 , 2 , 3) : ")

            if choice == "1":
                username = input("Username: ")
                password = input("Password: ")

                if self.login(username, password):
                    self._show_menu()

            elif choice == "2":
                username = input("New username: ")
                password = input("New password: ")

                self.register(username, password)

            elif choice == "3":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")    

    def _show_menu(self):

        if self._current_user.role == "Admin":
            self._show_admin_menu()

        else:
            self._show_salesman_menu()

    def _show_admin_menu(self):

        while True:
            print("\n=== Admin Menu ===")
            print("1. Add Product")
            print("2. Update Product")
            print("3. Delete Product")
            print("4. View All Products")
            print("5. Search Products")
            print("6. View Low Stock")
            print("7. View Expiring Products")
            print("8. Logout")

            choice = input("Enter your choice (1 - 8) : ")

            if choice == "8":
                self._current_user = None
                break

            self._handle_admin_choice(choice)

    def _show_salesman_menu(self):
        while True:
            print("\n=== Salesman Menu ===")
            print("1. Create New Bill")
            print("2. View All Products")
            print("3. Search Products")
            print("4. Adjust Stock")
            print("5. View Low Stock")
            print("6. View Daily Sales Report")
            print("7. Logout")
            
            choice = input("Enter your choice (1-7): ")
            
            if choice == "7":
                self._current_user = None
                break
            
            self._handle_salesman_choice(choice)

    def _handle_admin_choice(self , choice : str):

        if choice == "1":
            self._add_product()
        elif choice == "2":
            self._update_product()
        elif choice == "3":
            self._delete_product()
        elif choice == "4":
            self._view_all_products()
        elif choice == "5":
            self._search_products()
        elif choice == "6":
            self._view_low_stock()
        elif choice == "7":
            self._view_expiring_products()
        else:
            print("Invalid choice.")

    def _handle_salesman_choice(self, choice: str):
        if choice == "1":
            self._create_bill()
        elif choice == "2":
            self._view_all_products()
        elif choice == "3":
            self._search_products()
        elif choice == "4":
            self._adjust_stock()
        elif choice == "5":
            self._view_low_stock()
        elif choice == "6":
            self._view_daily_sales_report()
        else:
            print("Invalid choice.")

    def _add_product(self):

        product_id = input("Product ID : ")
        name = input("Name : ")
        category = input("Category : ")
        price = float(input("Price : "))
        quantity = int(input("Quantity : "))
        expiry_date = input("Expiry Date (YYYY-MM-DD) : ")

        product = Product(product_id , name , category , price , quantity , expiry_date)

        if self._inventory.add_product(product):
            print("Product added Successfully")

    def _update_product(self):

        product_id = input("Enter Product ID to update : ")
        updates = {}
        fields = ["name" , "category" , "price" , "quantity" , "expiry_date"]

        for field in fields:
            value = input(f"New {field} (press Enter to skip) : ")

            if value:
                updates[field] = value

        if self._inventory.update_prodcut(product_id , **updates):
            print("Produt updated successfully.")

    
    def _delete_product(self):

        product_id = input("Enter Product ID to delete : ")

        if self._inventory.delete_product(product_id):
            print("Product deleted successfully.")

    def _adjust_stock(self):

        product_id = input("Product ID : ")
        quantity_change = int(input("Quantity change (positive for addition, negative for reduction) : "))
        
        if self._inventory.adjust_stock(product_id, quantity_change):
            print("Stock adjusted successfully.")

    def _search_products(self):

        print("Search by: ")
        print("1. Name")
        print("2. Category")

        choice = input("Enter choice (1 - 2) : ")
        
        if choice == "1":
            name = input("Enter product name: ")
            results = self._inventory.search_products("name", name)

        elif choice == "2":
            category = input("Enter category: ")
            results = self._inventory.search_products("category", category)

        else:
            print("Invalid choice.")
            return
        
        self._display_products(results)    

    def _view_low_stock(self):

        products = self._inventory.get_low_stock_products()
        self._display_products(products)

    def _view_expiring_products(self):

        products = self._inventory.get_expiring_products()
        self._display_products(products)

    def _view_all_products(self):

        inventory = self._inventory._storage.load_data()
        self._display_products(inventory.values())

    def _display_products(self , products : List[dict]):

        if not products:
            print("No products found.")
            return
        
        for product in products:
            print("\n-------------------")
            for key, value in product.items():
                print(f"{key}: {value}")

    def _create_bill(self):

        """
        Handle the bill creation process
        """

        if not self._current_user:
            print("Please log in first")
            return
            
        transaction = self._billing.create_bill(self._current_user.username)
        
        if transaction:
            print("Bill created successfully")

    def _view_daily_sales_report(self):

        """
        View daily sales report
        """

        date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ")

        try:
            if date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                date = datetime.now()
                
            report = self._transaction_manager.get_daily_sales_report(date)
            
            print("\n=== Daily Sales Report ===")
            print(f"Date: {report['date']}")
            print(f"Total Sales: {report['total_sales']}Rs")
            print(f"Total Transactions: {report['total_transactions']}")
            print(f"Total Items Sold: {report['total_items_sold']}")
            
        except ValueError:
            print("Invalid date format")

    def _view_monthly_sales_report(self):

        """
        View monthly sales report
        """

        try:
            year = int(input("Enter year (YYYY): "))
            month = int(input("Enter month (1-12): "))
            
            report = self._transaction_manager.get_monthly_sales_report(year, month)
            
            print("\n=== Monthly Sales Report ===")
            print(f"Year: {report['year']}")
            print(f"Month: {report['month']}")
            print(f"Total Sales: {report['total_sales']}Rs")
            print(f"Total Transactions: {report['total_transactions']}")
            
            print("\nDaily Totals:")
            for date, total in report['daily_totals'].items():
                print(f"{date}: {total}Rs")
                
        except ValueError:
            print("Invalid input format")

# -------------------------------------- Calling Main class -------------------------------------------------

if __name__ == "__main__":
    ims = InventoryManagementSystem()
    ims.run()
