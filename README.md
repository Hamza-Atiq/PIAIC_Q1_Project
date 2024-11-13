# Inventory Management System (IMS)

The Inventory Management System (IMS) is a console-based application that allows businesses to manage their inventory, process sales, and generate comprehensive sales reports. This system is designed to handle user authentication, role-based access control, and various inventory operations.

## Features

1. **User Authentication and Role Management**:
   - Supports different user roles: "Admin" and "Salesman"
   - Admins can add, edit, and delete products, while Salesmen can only view inventory details and process sales
   - Implements a login system with username and password validation

2. **Product Management**:
   - Allows creating, updating, and deleting products
   - Tracks product details such as ID, name, category, price, and stock quantity
   - Provides methods for viewing all products, searching by name or category, and filtering by stock levels

3. **Inventory Operations**:
   - Tracks stock levels and prompts for restocking when stock reaches a low threshold
   - Allows adjusting stock quantities (restock or sale)
   - Generates daily purchase reports based on stock adjustments

4. **Billing and Sales Tracking**:
   - Enables Salesmen to create new bills by scanning products and processing payments
   - Automatically updates inventory stock levels during sales
   - Generates detailed transaction receipts
   - Tracks all sales transactions and provides reporting capabilities

5. **Reporting**:
   - Generates daily sales reports, including total sales, number of transactions, items sold, and individual transaction details
   - Generates monthly sales reports, providing an overview with daily breakdowns and total sales figures

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ims.git
   ```

2. Navigate to the project directory:
   ```
   cd ims
   ```

3. Ensure you have Python 3.7 or higher installed on your system.

4. Run the application:
   ```
   python Inventory_management_system.py
   ```

## Usage

1. **First-time Setup**:
   - When running the application for the first time, create an "admin" user account.

2. **User Management**:
   - Regular users can register as "Salesman" accounts.
   - Admins have access to the full menu, while Salesmen have a limited menu.

3. **Inventory Management**:
   - Admins can add, update, and delete products.
   - All users can view the product inventory, search by name or category, and filter by low stock.
   - Salesmen can adjust stock quantities during sales.

4. **Billing and Sales**:
   - Salesmen can create new bills by scanning products and processing payments.
   - The system automatically updates the inventory and generates a detailed transaction receipt.

5. **Reporting**:
   - Salesmen can view the daily sales report for a specific date.
   - Admins can view the monthly sales report for a given year and month.


