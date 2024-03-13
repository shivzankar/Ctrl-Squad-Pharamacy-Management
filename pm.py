import tkinter as tk
from tkinter import ttk
import mysql.connector
import tkinter.messagebox as messagebox

def create_database_if_not_exists():
    # Connect to MySQL server without specifying a database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
    )

    cursor = connection.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS pharmacy_db")

    # Use the pharmacy_db
    cursor.execute("USE pharmacy_db")

    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price FLOAT NOT NULL
        )
    """)

    # Modify the "sales" table creation query to include a "phone_number" field
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(255) NOT NULL,
            phone_number VARCHAR(15),  # Add a new field for phone number
            medicine_id INT NOT NULL,
            quantity INT NOT NULL,
            total_price FLOAT NOT NULL,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    # Commit changes and close the cursor and connection
    connection.commit()
    cursor.close()
    connection.close()

# Call the function to create the database and tables if not exist
create_database_if_not_exists()

# Connect to the pharmacy database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="pharmacy_db"
)

# Create a cursor
cursor = db.cursor()

class PharmacyManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")

        # Create tabs
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill=tk.BOTH, expand=True)

        # Create tabs for different functionalities
        self.create_medicine_tab()
        self.create_sales_tab()

        # Initialize a variable to store temporary sales
        self.sales_list = []

    def create_medicine_tab(self):
        # Medicine Tab
        medicine_tab = ttk.Frame(self.tabs)
        self.tabs.add(medicine_tab, text="Medicine")

        # Create widgets for the Medicine tab
        ttk.Label(medicine_tab, text="Medicine Management").pack(pady=10)
        ttk.Button(medicine_tab, text="Add Medicine", command=self.add_medicine).pack(pady=5)
        ttk.Button(medicine_tab, text="View Medicines", command=self.view_medicines).pack(pady=5)

    def create_sales_tab(self):
        # Sales Tab
        sales_tab = ttk.Frame(self.tabs)
        self.tabs.add(sales_tab, text="Sales")

        # Create widgets for the Sales tab
        ttk.Label(sales_tab, text="Sales Management").pack(pady=10)
        ttk.Button(sales_tab, text="Make Sale", command=self.make_sale).pack(pady=5)
        ttk.Button(sales_tab, text="View Temporary Sales", command=self.view_temporary_sales).pack(pady=5)

    def add_medicine(self):
        # Function to add medicine to the database
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Medicine")

        # Create entry widgets
        ttk.Label(add_window, text="Medicine Name:").grid(row=0, column=0, padx=10, pady=5)
        medicine_name_entry = ttk.Entry(add_window)
        medicine_name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Price:").grid(row=1, column=0, padx=10, pady=5)
        price_entry = ttk.Entry(add_window)
        price_entry.grid(row=1, column=1, padx=10, pady=5)

        # Function to save medicine to the database
        def save_medicine():
            name = medicine_name_entry.get()
            price = float(price_entry.get())

            # Insert into the database
            try:
                cursor.execute("INSERT INTO medicines (name, price) VALUES (%s, %s)", (name, price))
                db.commit()
                messagebox.showinfo("Success", "Medicine added successfully")
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")

        # Create Save button
        ttk.Button(add_window, text="Save", command=save_medicine).grid(row=2, column=0, columnspan=2, pady=10)

    def view_medicines(self):
        # Function to view medicines from the database
        view_window = tk.Toplevel(self.root)
        view_window.title("View Medicines")

        # Create Treeview widget
        tree = ttk.Treeview(view_window, columns=("Medicine ID", "Name", "Price"))
        tree.heading("#0", text="Medicine ID")
        tree.heading("#1", text="Name")
        tree.heading("#2", text="Price")

        # Fetch medicines from the database
        cursor.execute("SELECT * FROM medicines")
        medicines = cursor.fetchall()

        # Insert data into Treeview
        for medicine in medicines:
            tree.insert("", "end", values=medicine)

        tree.pack(padx=10, pady=10)

    def make_sale(self):
        # Function to make a sale and update the temporary sales list
        make_sale_window = tk.Toplevel(self.root)
        make_sale_window.title("Make Sale")

        # Create entry widgets
        ttk.Label(make_sale_window, text="Customer Name:").grid(row=0, column=0, padx=10, pady=5)
        customer_name_entry = ttk.Entry(make_sale_window)
        customer_name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(make_sale_window, text="Phone Number:").grid(row=1, column=0, padx=10, pady=5)
        phone_number_entry = ttk.Entry(make_sale_window)
        phone_number_entry.grid(row=1, column=1, padx=10, pady=5)

        # Fetch medicine names from the database
        cursor.execute("SELECT id, name FROM medicines")
        medicine_data = cursor.fetchall()
        medicine_names = [med[1] for med in medicine_data]
        medicine_ids = [med[0] for med in medicine_data]

        ttk.Label(make_sale_window, text="Medicine Name:").grid(row=2, column=0, padx=10, pady=5)
        medicine_name_combo = ttk.Combobox(make_sale_window, values=medicine_names)
        medicine_name_combo.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(make_sale_window, text="Quantity:").grid(row=3, column=0, padx=10, pady=5)
        quantity_entry = ttk.Entry(make_sale_window)
        quantity_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(make_sale_window, text="Total Price:").grid(row=4, column=0, padx=10, pady=5)
        total_price_label = ttk.Label(make_sale_window, text="")
        total_price_label.grid(row=4, column=1, padx=10, pady=5)

        # Function to calculate total price
        def calculate_total_price():
            medicine_name = medicine_name_combo.get()
            quantity = int(quantity_entry.get())

            # Find the corresponding medicine_id
            selected_index = medicine_names.index(medicine_name)
            medicine_id = medicine_ids[selected_index]

            # Fetch medicine details
            cursor.execute("SELECT * FROM medicines WHERE id = %s", (medicine_id,))
            medicine = cursor.fetchone()

            if medicine:
                total_price = quantity * medicine[2]  # Assuming the price is at index 2
                total_price_label.config(text=f"${total_price:.2f}")
            else:
                messagebox.showerror("Error", "Medicine not found")

        # Function to save sale to the temporary list
        def save_sale_to_list():
            customer_name = customer_name_entry.get()
            phone_number = phone_number_entry.get()
            medicine_name = medicine_name_combo.get()
            quantity = int(quantity_entry.get())

            # Find the corresponding medicine_id
            selected_index = medicine_names.index(medicine_name)
            medicine_id = medicine_ids[selected_index]

            # Fetch medicine details
            cursor.execute("SELECT * FROM medicines WHERE id = %s", (medicine_id,))
            medicine = cursor.fetchone()

            if medicine:
                total_price = quantity * medicine[2]  # Assuming the price is at index 2
                sale_details = (None, customer_name, phone_number, medicine_id, quantity, total_price)
                self.sales_list.append(sale_details)
                messagebox.showinfo("Success", "Sale added to temporary list")

                # Generate and display the bill
                self.generate_bill(sale_details)

                make_sale_window.destroy()
            else:
                messagebox.showerror("Error", "Medicine not found")

        # Create Calculate button
        ttk.Button(make_sale_window, text="Calculate Total Price", command=calculate_total_price).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(make_sale_window, text="Save Sale to List", command=save_sale_to_list).grid(row=6, column=0, columnspan=2, pady=10)

    def view_temporary_sales(self):
        # Function to view the temporary sales list
        view_temp_sales_window = tk.Toplevel(self.root)
        view_temp_sales_window.title("View Temporary Sales")

        # Create entry widget for searching by phone number
        ttk.Label(view_temp_sales_window, text="Search by Phone Number:").pack(pady=5)
        search_entry = ttk.Entry(view_temp_sales_window)
        search_entry.pack(pady=5)

        # Create Search button
        ttk.Button(view_temp_sales_window, text="Search", command=lambda: self.search_temporary_sales(search_entry.get(), tree)).pack(pady=5)

        # Create Treeview widget
        tree = ttk.Treeview(view_temp_sales_window, columns=("ID", "Customer Name", "Phone Number", "Medicine ID", "Quantity", "Total Price"))
        tree.heading("#0", text="ID")
        tree.heading("#1", text="Customer Name")
        tree.heading("#2", text="Phone Number")
        tree.heading("#3", text="Medicine ID")
        tree.heading("#4", text="Quantity")
        tree.heading("#5", text="Total Price")

        # Fetch sales from the temporary list
        for sale in self.sales_list:
            tree.insert("", "end", values=sale)

        tree.pack(padx=10, pady=10)

    # Add a new method to perform the search
    def search_temporary_sales(self, phone_number, tree):
        # Function to search temporary sales by phone number
        results = []
        for sale in self.sales_list:
            if phone_number.lower() in sale[2].lower():  # Index 2 corresponds to phone number
                results.append(sale)

        # Clear existing items in the Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Insert search results into Treeview
        for result in results:
            tree.insert("", "end", values=result)

    def generate_bill(self, sale_details):
        # Function to generate and display the bill
        bill_window = tk.Toplevel(self.root)
        bill_window.title("Bill")

        ttk.Label(bill_window, text="Bill Details", font=("bold", 14)).pack(pady=10)

        ttk.Label(bill_window, text=f"Customer Name: {sale_details[1]}").pack()
        ttk.Label(bill_window, text=f"Phone Number: {sale_details[2]}").pack()
        ttk.Label(bill_window, text="Medicine Details:").pack(pady=5)

        # Fetch medicine details
        cursor.execute("SELECT * FROM medicines WHERE id = %s", (sale_details[3],))
        medicine = cursor.fetchone()

        if medicine:
            ttk.Label(bill_window, text=f"Medicine Name: {medicine[1]}").pack()
            ttk.Label(bill_window, text=f"Quantity: {sale_details[4]}").pack()
            ttk.Label(bill_window, text=f"Total Price: ${sale_details[5]:.2f}").pack()
        else:
            ttk.Label(bill_window, text="Medicine not found").pack()

# Create the main window
root = tk.Tk()
app = PharmacyManagementApp(root)
root.geometry("800x600")
root.mainloop()
