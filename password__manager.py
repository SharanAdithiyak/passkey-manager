from tkinter import CENTER, Tk, Label, Button, Entry, Frame, END, Toplevel, messagebox
from tkinter import ttk
from typing import List, Dict, Any, Optional
import re
import random
import string
from db_operations import DbOperations

class RootWindow:
    """Main window class for the Password Manager application.
    
    This class handles the GUI and interactions for the password manager,
    including CRUD operations and password management functionality.
    """

    def __init__(self, root: Tk, db: DbOperations) -> None:
        """Initialize the main window of the password manager.
        
        Args:
            root: The main Tkinter window
            db: Database operations instance
        """
        self.db = db
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("900x700+40+40")  # Made window taller
        
        # Initialize UI elements
        self.entry_boxes: List[Entry] = []
        self.records_tree: Optional[ttk.Treeview] = None
        self.search_entry: Optional[Entry] = None
        self.crud_frame: Optional[Frame] = None
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        # Setup keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_record())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<Control-g>', lambda e: self.generate_password())
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the main UI components."""
        # Create header with gradient effect
        header_frame = Frame(self.root, bg='#2c3e50', height=60)
        header_frame.grid(columnspan=4, sticky='ew')
        header_frame.grid_propagate(False)
        
        Label(
            header_frame,
            text="Password Manager",
            font=("Arial", 24, "bold"),
            fg="white",
            bg='#2c3e50',
            pady=10
        ).pack()

        # Main content area
        main_frame = Frame(self.root, pady=20)
        main_frame.grid(row=1, column=0, sticky='nsew')
        
        # CRUD Frame
        self.crud_frame = Frame(
            main_frame,
            highlightbackground="#34495e",
            highlightthickness=1,
            padx=20,
            pady=20
        )
        self.crud_frame.pack(fill='x', padx=20)
        
        self.create_entry_labels()
        self.create_entry_boxes()
        self.create_crud_buttons()
        
        # Search Frame
        search_frame = Frame(main_frame, pady=10)
        search_frame.pack(fill='x', padx=20)
        
        Label(
            search_frame,
            text="Search:",
            font=("Arial", 12)
        ).pack(side='left', padx=5)
        
        self.search_entry = Entry(
            search_frame,
            width=30,
            font=("Arial", 12),
            background="white"
        )
        self.search_entry.pack(side='left', padx=5)
        
        ttk.Button(
            search_frame,
            text="Search",
            command=self.search_record,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        # Create TreeView
        self.create_records_tree()
        
        # Status bar
        self.status_bar = Label(
            self.root,
            text="Ready",
            bd=1,
            relief='sunken',
            anchor='w'
        )
        self.status_bar.grid(row=2, column=0, sticky='ew', columnspan=4)

    def create_entry_labels(self) -> None:
        """Create labels for entry fields."""
        self.col_no, self.row_no = 0, 0
        labels_info = ('ID', 'Website', 'Username', 'Password')
        
        for label_text in labels_info:
            Label(
                self.crud_frame,
                text=label_text,
                width=10,
                fg="white",
                bg="#34495e",
                font=("Arial", 12),
                padx=5,
                pady=2
            ).grid(row=self.row_no, column=self.col_no, padx=5, pady=2)
            self.col_no += 1

    def create_crud_buttons(self) -> None:
        """Create CRUD operation buttons."""
        self.row_no += 1
        self.col_no = 0
        
        button_info = [
            ('Save (Ctrl+S)', 'green', self.save_record),
            ('Delete', 'red', self.delete_record),
            ('Update', 'orange', self.update_record),
            ('Copy Password', 'blue', self.copy_password),
            ('Generate Password (Ctrl+G)', 'purple', self.generate_password)
        ]
        
        for btn_text, color, command in button_info:
            Button(
                self.crud_frame,
                text=btn_text,
                fg="white",
                bg=color,
                font=("Arial", 11),
                padx=5,
                pady=2,
                width=20,
                command=command
            ).grid(row=self.row_no, column=self.col_no, padx=5, pady=10)
            self.col_no += 1
            
            if btn_text == 'Copy Password':
                self.row_no += 1
                self.col_no = 0

    def create_entry_boxes(self):
        self.row_no += 1
        self.entry_boxes = []
        self.col_no = 0
        for i in range(4):
            show = ""
            if i == 3:
                show = "*" 
            entry_box = Entry(self.crud_frame, width=20, font=("Arial", 13), background="white", show=show)
            entry_box.grid(row=self.row_no, column=self.col_no, padx=5, pady=2)
            self.col_no += 1
            self.entry_boxes.append(entry_box)

    def validate_input(self) -> tuple[bool, str]:
        """Validate user input before saving or updating.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        website = self.entry_boxes[1].get().strip()
        username = self.entry_boxes[2].get().strip()
        password = self.entry_boxes[3].get().strip()
        
        if not all([website, username, password]):
            return False, "All fields must be filled"
            
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
            
        # Basic password strength check
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$", password):
            return False, "Password must contain letters and numbers"
            
        return True, ""

    def save_record(self) -> None:
        """Save a new password record after validation."""
        is_valid, error_msg = self.validate_input()
        if not is_valid:
            self.showmessage("Error", error_msg)
            return
            
        website = self.entry_boxes[1].get().strip()
        username = self.entry_boxes[2].get().strip()
        password = self.entry_boxes[3].get().strip()
        
        try:
            data = {'website': website, 'username': username, 'password': password}
            self.db.create_record(data)
            self.show_records()
            self.clear_entries()
            self.showmessage("Success", "Record saved successfully")
        except Exception as e:
            self.showmessage("Error", f"Failed to save record: {str(e)}")

    def clear_entries(self) -> None:
        """Clear all entry boxes."""
        for entry in self.entry_boxes:
            entry.delete(0, END)

    def update_record(self): 
        ID = self.entry_boxes[0].get()
        website = self.entry_boxes[1].get()
        username = self.entry_boxes[2].get()
        password = self.entry_boxes[3].get()  
        data = {'ID': ID, 'website': website, 'username': username, 'password': password}
        self.db.update_records(data)
        self.show_records()

    def delete_record(self) -> None:
        """Delete the selected record after confirmation."""
        ID = self.entry_boxes[0].get()
        if not ID:
            self.showmessage("Error", "Please select a record to delete")
            return
            
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            return
            
        try:
            self.db.delete_records(ID)
            self.show_records()
            self.clear_entries()
            self.showmessage("Success", "Record deleted successfully")
        except Exception as e:
            self.showmessage("Error", f"Failed to delete record: {str(e)}")

    def show_records(self):
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        records_list = self.db.show_records()
        for record in records_list:
            self.records_tree.insert('', END, values=(record[0], record[3], record[4], record[5]))

    def create_records_tree(self):
        columns = ('ID', 'website', 'username', 'password')
        self.records_tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.records_tree.heading('ID', text='ID')
        self.records_tree.heading('website', text='website Name')
        self.records_tree.heading('username', text=' User Name')
        self.records_tree.heading('password', text='Password')
        self.records_tree['displaycolumns'] = ('website', 'username')

        def item_selected(event):
            for seleceted_item in self.records_tree.selection():
                item = self.records_tree.item(seleceted_item)
                records = item['values']
                for entry_box, item in zip(self.entry_boxes, records):
                    entry_box.delete(0, END)
                    entry_box.insert(0, item)
    
        self.records_tree.bind('<<TreeviewSelect>>', item_selected)

        self.records_tree.grid()

    def search_record(self) -> None:
        """Search for records matching the search term."""
        search_term = self.search_entry.get().strip()
    
        if not search_term:
            self.showmessage("Error", "Enter a search term!")
            return

        try:
            results = self.db.search_records(search_term)
            
            # Clear existing data in Treeview
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)

            # Insert search results
            for record in results:
                self.records_tree.insert('', END, values=(record[0], record[3], record[4], record[5]))

            if not results:
                self.showmessage("Info", "No matching records found.")
        except Exception as e:
            self.showmessage("Error", f"Search failed: {str(e)}")

    #copy to clipboard
    def copy_password(self):
       self.root.clipboard_clear()
       self.root.clipboard_append(self.entry_boxes[3].get())
       message = "password copied"
       title = "Copy"
       if self.entry_boxes[3].get() == "":
           message = "Box is empty"
           title = "Error"
       self.showmessage(title, message)
       
    def generate_password(self, length: int = 16) -> None:
        """Generate a strong random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Ensure password meets requirements
        while not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$", password):
            password = ''.join(random.choice(characters) for _ in range(length))
        
        self.entry_boxes[3].delete(0, END)
        self.entry_boxes[3].insert(0, password)
        self.showmessage("Success", "Generated new password")

    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_bar.config(text=message)
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))

    def showmessage(self, title_box: str = None, message: str = None) -> None:
        """Show a temporary message popup."""
        TIME_TO_WAIT = 1500  # Reduced time to 1.5 seconds
        root = Toplevel(self.root)
        background = '#2ecc71' if title_box != "Error" else '#e74c3c'
        
        # Position popup relative to main window
        x = self.root.winfo_x() + self.root.winfo_width()//2 - 150
        y = self.root.winfo_y() + self.root.winfo_height()//2 - 15
        root.geometry(f'300x30+{x}+{y}')
        
        root.overrideredirect(True)  # Remove window decorations
        root.title(title_box)
        
        Label(
            root,
            text=message,
            background=background,
            font=("Arial", 12),
            fg='white'
        ).pack(fill='both', expand=True)
        
        self.update_status(message)
        
        try:
            root.after(TIME_TO_WAIT, root.destroy)
        except Exception as e:
            print("Error occurred:", e)


if __name__ == "__main__":

    db_class = DbOperations()
    db_class.create_table()

    root = Tk()
    root_class = RootWindow(root, db_class)
    root.mainloop()

    