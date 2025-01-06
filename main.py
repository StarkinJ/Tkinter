import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import bcrypt
import re
import webbrowser
from Scraper import scrape_offerUp
import threading
import time
from Scraper import Scoring
import random
from Scraper import Email
import pyautogui


class SleepPrevention:
    """Class to prevent sleep by simulating mouse movements."""
    def __init__(self):
        self.preventing_sleep = False
        self.thread = None

    def prevent_sleep(self):
        """Start simulating mouse movements to prevent sleep."""
        if not self.preventing_sleep:
            self.preventing_sleep = True
            self.thread = threading.Thread(target=self._simulate_mouse_movements, daemon=True)
            self.thread.start()
            print("Mouse movements started to prevent sleep.")

    def allow_sleep(self):
        """Stop simulating mouse movements, allowing the system to sleep."""
        if self.preventing_sleep:
            self.preventing_sleep = False
            if self.thread:
                self.thread.join()
            print("Mouse movements stopped, system can sleep.")

    def _simulate_mouse_movements(self):
        """Simulate small, imperceptible mouse movements."""
        while self.preventing_sleep:
            current_position = pyautogui.position()  # Get current mouse position
            pyautogui.moveTo(current_position.x + 1, current_position.y)  # Move right by 1 pixel
            pyautogui.moveTo(current_position.x, current_position.y)  # Move back to original position
            time.sleep(30)  # Perform every 30 seconds to avoid unnecessary activity

class CustomMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, buttons=None):
        """
        Initialize the CustomMessageBox.

        :param parent: The parent window.
        :param title: The title of the message box.
        :param message: The message to display.
        :param buttons: A list of tuples with (button_text, button_callback) for custom buttons.
                        If None, defaults to a single "OK" button.
        """
        super().__init__(parent)
        self.title(title)
        self.result = None  # Store the result if needed

        # Center the window on the screen
        self.geometry("300x150")
        self.center_window(300, 150)

        # Message Label
        label = ttk.Label(self, text=message, wraplength=250, justify="center", font=("Arial", 12))
        label.pack(pady=20)

        # Button Frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        # Add buttons dynamically
        if buttons:
            for idx, (text, callback) in enumerate(buttons):
                ttk.Button(button_frame, text=text, command=lambda cb=callback: self._handle_button(cb)).grid(row=0, column=idx, padx=10)
        else:
            # Default to "OK" button if no buttons are provided
            ttk.Button(button_frame, text="OK", command=self.destroy).pack()

        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def _handle_button(self, callback):
        """
        Handle button press and execute the callback if provided.

        :param callback: The callback function to execute.
        """
        if callback:
            callback()
        self.destroy()

    def center_window(self, width, height):
        """
        Center the window on the screen.

        :param width: Width of the window.
        :param height: Height of the window.
        """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scraper App")
        self.geometry("400x300")
        self.center_window(400, 300)  # Center the window with width=400 and height=300
        self.current_frame = None  # Keep track of the current frame

        # Show the login frame initially
        self.show_frame(LoginFrame)

    def center_window(self, width, height):
        """Center the window on the screen."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, frame_class):
        """Create and show a frame, destroying the previous one."""
        if self.current_frame is not None:
            self.current_frame.destroy()  # Remove the current frame

        # Create a new frame
        self.current_frame = frame_class(self)
        self.current_frame.pack(fill="both", expand=True)


class LoginFrame(ttk.Frame):
    def __init__(self, controller):
        super().__init__(controller, padding="10")
        self.controller = controller

        # Configure grid for the parent window (controller) to center the LoginFrame
        controller.grid_rowconfigure(0, weight=1)
        controller.grid_columnconfigure(0, weight=1)

        # Configure grid for LoginFrame
        self.grid_rowconfigure(0, weight=1)  # Title row
        self.grid_rowconfigure(1, weight=1)  # Form row
        self.grid_rowconfigure(2, weight=1)  # Buttons row
        self.grid_columnconfigure(0, weight=1)  # Single column for centering

        # Create the title label
        title_label = ttk.Label(self, text="Login Page", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, pady=20)

        # Create the username and password input fields
        form_frame = ttk.Frame(self, padding="10")
        form_frame.grid(row=1, column=0, sticky="nsew")

        form_frame.grid_rowconfigure(0, weight=1)  # Username row
        form_frame.grid_rowconfigure(1, weight=1)  # Password row
        form_frame.grid_columnconfigure(0, weight=1)  # Left alignment in form
        form_frame.grid_columnconfigure(1, weight=1)  # Right alignment in form

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Create the login and sign-up buttons
        button_frame = ttk.Frame(self, padding="10")
        button_frame.grid(row=2, column=0, sticky="nsew")

        button_frame.grid_rowconfigure(0, weight=1)  # Login button row
        button_frame.grid_rowconfigure(1, weight=1)  # Sign-up button row
        button_frame.grid_columnconfigure(0, weight=1)  # Center column in button frame

        login_button = ttk.Button(button_frame, text="Login", command=self.handle_login)
        login_button.grid(row=0, column=0, pady=5, padx=5)

        sign_up_button = ttk.Button(button_frame, text="Sign Up", command=self.handle_sign_up)
        sign_up_button.grid(row=1, column=0, pady=5, padx=5)

        # Bind the Enter key to the login button (simulates a button click)
        controller.bind("<Return>", lambda event: login_button.invoke())

        # Set focus to the username entry widget so that <Return> works
        self.username_entry.focus_set()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            CustomMessageBox(self, "Login Error", "Please enter both username and password.")
            return

        con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
        con.execute('PRAGMA journal_mode=WAL;')
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        con.close()

        if user:
            stored_hash = user[3]  # Assuming password is in the second column
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                CustomMessageBox(self, "Login Successful", f"Welcome, {username}!")
                self.controller.geometry("800x1000")  # Change window size for dashboard
                self.controller.show_frame(DashboardFrame)
            else:
                CustomMessageBox(self, "Login Error", "Invalid username or password.")
        else:
            CustomMessageBox(self, "Login Error", "Invalid username or password.")

    def handle_sign_up(self):
        self.controller.show_frame(SignUpPage)


class SignUpPage(ttk.Frame):
    def __init__(self, controller):
        super().__init__(controller, padding="10")
        self.controller = controller

        # Configure the grid for SignUpPage (self)
        self.grid_rowconfigure(0, weight=1)  # Title row
        self.grid_rowconfigure(1, weight=1)  # Form row
        self.grid_rowconfigure(2, weight=1)  # Button row
        self.grid_columnconfigure(0, weight=1)  # Single column for centering

        # Create the title label
        title_label = ttk.Label(self, text="Sign Up", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)  # Center the title label

        # Create the username and password input fields
        form_frame = ttk.Frame(self, padding="10")
        form_frame.grid(row=1, column=0, sticky="nsew")  # Center the form frame

        # Center the form contents
        form_frame.grid_rowconfigure(0, weight=1)
        form_frame.grid_rowconfigure(1, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)  # Space left of label
        form_frame.grid_columnconfigure(1, weight=1)  # Space right of entry

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Create the back button
        button_frame = ttk.Frame(self, padding="10")
        button_frame.grid(row=2, column=0, sticky="nsew")

        button_frame.grid_rowconfigure(0, weight=1)  # Button row
        button_frame.grid_columnconfigure(0, weight=1)  # Center column in button frame

        sign_up_button = ttk.Button(button_frame, text="Sign Up", command=self.handle_sign_up)
        sign_up_button.grid(row=0, column=0, pady=10)

        back_button = ttk.Button(button_frame, text="Back", command=self.back_to_login)
        back_button.grid(row=1, column=0, pady=5)

    def handle_sign_up(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()

        if not username or not password or not email:
            CustomMessageBox(self, "Sign Up Error", "Please fill in all fields.")
            return

        if not self.is_valid_email(email):
            CustomMessageBox(self, "Sign Up Error", "Invalid email format.")
            return

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
        con.execute('PRAGMA journal_mode=WAL;')
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password_hash))
        con.commit()
        con.close()

        CustomMessageBox(self, "Sign Up Successful", f"Account created for {username}!")
        self.controller.show_frame(LoginFrame)

    def is_valid_email(self, email):
        """Check if the email is valid using regex."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def back_to_login(self):
        self.controller.show_frame(LoginFrame)


class DashboardFrame(ttk.Frame):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller

        # Flag to control the scraper thread
        self.scraping_event = threading.Event()

        # For not sleeping
        self.sleep_prevention = SleepPrevention()

        # Create a Notebook widget (tab manager)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Create Tab 1 for items
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Items")

        # Create Tab 2 for cars (similar setup)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Cars")

        # Add a logout button at the bottom of the dashboard
        logout_button = ttk.Button(self, text="Log Out", command=self.log_out)
        logout_button.pack(side="bottom", pady=10)

        # Call the method to create the Items tab
        self.create_items_tab()
        self.create_cars_tab()

        # Bind tab change to stop scraping when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)



    def check_for_scraping_in_items(self):
        """Check if scraping is in progress in the Items tab, and stop it."""
        if self.scraping_event.is_set():
            self.stop_car_scrape()

    def on_tab_change(self, event):
        """Handle tab change. Warn the user and prevent tab switch if scraping is active."""
        if self.scraping_event.is_set():  # Check if scraping is active
            # Prevent the tab change by resetting the tab selection back to the current tab
            event.widget.select(self.previous_tab)  # `self.previous_tab` should store the current tab index

            # Show a warning message to the user
            CustomMessageBox(
                self,
                "Warning: Scraping in Progress",
                "Scraping is currently active. Please stop the scraping process before switching tabs.",
                buttons=[("OK", lambda: None)]  # Close the message box when OK is clicked
            )
        else:
            # Update the previous tab index to the newly selected tab
            self.previous_tab = event.widget.index("current")

    def create_items_tab(self):

        # Scrape Items section
        scrape_label = ttk.Label(self.tab1, text="Scrape Items", font=("Arial", 14, "bold"))
        scrape_label.pack(pady=10)

        # Scrape entry and buttons
        scrape_frame = ttk.Frame(self.tab1)
        scrape_frame.pack(pady=10, fill="x", padx=10)

        ttk.Label(scrape_frame, text="Scrape:").grid(row=0, column=0, sticky="w", padx=5)
        self.scrape_entry = ttk.Entry(scrape_frame, width=25)
        self.scrape_entry.grid(row=0, column=1, sticky="w", padx=5)

        self.scrape_entry.bind("<FocusIn>", self.show_scraping_warning)

        self.start_button = ttk.Button(scrape_frame, text="Start Scrape", command=self.start_scrape)
        self.start_button.grid(row=0, column=2, padx=5)

        stop_button = ttk.Button(scrape_frame, text="Stop Scrape", command=self.stop_scrape)
        stop_button.grid(row=0, column=3, padx=5)

        # Line separator
        ttk.Separator(self.tab1, orient="horizontal").pack(fill="x", pady=20)

        # Create the Search Items section
        search_label = ttk.Label(self.tab1, text="Search Items", font=("Arial", 16))
        search_label.pack(pady=10)

        form_frame = ttk.Frame(self.tab1, padding="10")
        form_frame.pack(pady=10, fill="x", padx=10)

        ttk.Label(form_frame, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.item_name_entry = ttk.Entry(form_frame, width=25)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Max Price:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.max_price_entry = ttk.Entry(form_frame, width=25)
        self.max_price_entry.grid(row=1, column=1, padx=5, pady=5)

        search_button = ttk.Button(form_frame, text="Search", command=self.search_items)
        search_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Create a Canvas for scrollable results
        self.canvas1 = tk.Canvas(self.tab1)
        self.canvas1.pack(pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.tab1, orient="vertical", command=self.canvas1.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas1.configure(yscrollcommand=scrollbar.set)

        self.item_results_frame = ttk.Frame(self.canvas1)
        self.canvas1.create_window((0, 0), window=self.item_results_frame, anchor="nw")

        self.item_results_frame.bind(
            "<Configure>",
            lambda e: self.canvas1.configure(scrollregion=self.canvas1.bbox("all"))
        )
        self.canvas1.bind_all("<MouseWheel>", self._on_mousewheel)


    def start_scrape(self):
        """Start the scraper thread."""
        if not self.scraping_event.is_set():

            item = self.scrape_entry.get().split()[0] if " " in self.scrape_entry.get() \
                else self.scrape_entry.get()

            con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
            con.execute('PRAGMA journal_mode=WAL;')
            cur = con.cursor()

            try:
                cur.execute("SELECT id FROM items_in_categories WHERE name = ?", (item,))
                brand_entry = cur.fetchone()

                if brand_entry:
                    print(f"Brand '{item}' exists in the database.")
                else:
                    print(f"Brand '{item}' does not exist in the database.")
                    self.show_add_item_form(item)
                    return

            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return
            finally:
                con.close()

            self.scraping_event.set()
            self.scraper_thread = threading.Thread(target=self.scrape_items, daemon=True)
            self.scraper_thread.start()

            # Update button text and color to indicate it's running
            self.start_button.config(text="Scraping...", state="disabled", style="StartButtonRunning.TButton")
            print("Scraping started!")


    def stop_scrape(self):
        """Stop the scraper thread."""
        if self.scraping_event.is_set():
            self.scraping_event.clear()

            # Revert the button text and color to original when stopped
            self.start_button.config(text="Start Scrape", state="normal", style="StartButton.TButton")
            print("Scraping stopped.")


    def scrape_items(self):
        """Scrape items in a loop while the event is set."""
        item_to_scrape = self.scrape_entry.get()
        if not item_to_scrape.strip():
            print("Error: No item entered.")
            return

        while self.scraping_event.is_set():
            try:
                print(f"Starting to scrape for item: {item_to_scrape}")

                # Simulate the actual scraping process here, for example, by calling your scraper function
                # Replace the line below with your actual scraping function
                scrape_offerUp.initialization(item_to_scrape)

                # Email most recent items if there is a good deal

                time.sleep(10)  # Simulate scraping delay

                # After scraping, wait for a random time between 20 and 40 minutes (1200 to 2400 seconds)
                random_delay = random.randint(1200, 2400)
                print(f"Scraping completed. Waiting for {random_delay // 60} minutes before the next scrape.")

                # Pause for the random delay
                time.sleep(random_delay)

            except Exception as e:
                print(f"Error during scraping: {e}")
                break


    def show_scraping_warning(self, event):
        """Show a warning if the scraping process is active when the entry box is focused."""
        if self.scraping_event.is_set() and self.notebook.index(self.notebook.select()) == 0:  # Items tab
            def stop_scraping():
                """Stop the scraping process."""
                self.stop_scrape()
                print("User stopped the scraping process.")  # Debugging

            def do_nothing():
                """Do nothing and close the message box."""
                print("User chose not to stop the scraping process.")  # Debugging

            # Show the custom warning message box
            CustomMessageBox(
                self,
                "Scraping in Progress",
                "A scraping process is currently running. Would you like to stop it before entering a new item?",
                buttons=[
                    ("Stop Scraping", stop_scraping),
                    ("Cancel", do_nothing)
                ]
            )

    def search_items(self):
        """Handle the Search functionality in Tab 1."""
        item_name = self.item_name_entry.get()
        max_price = self.max_price_entry.get()

        # Check if item_name is empty
        if not item_name:
            print("Please provide an item name.")
            return

        try:
            max_price = float(max_price) if max_price else None
        except ValueError:
            print("Max Price must be a valid number.")
            return

        # Connect to the database
        con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
        con.execute('PRAGMA journal_mode=WAL;')
        cur = con.cursor()

        # Query setup
        query = """
               SELECT Items.name, ItemDetails.price, Items.Link
               FROM ItemDetails
               JOIN Items ON ItemDetails.item_id = Items.item_id
               WHERE Items.name LIKE '%' || ? || '%' COLLATE NOCASE
           """
        params = [item_name]

        # Add price filter if provided
        if max_price is not None:
            query += " AND ItemDetails.price <= ?"
            params.append(max_price)

        # Execute query
        cur.execute(query, params)
        results = cur.fetchall()
        con.close()

        # Clear previous search results
        for widget in self.item_results_frame.winfo_children():
            widget.destroy()

        # Check if results exist
        if results:
            for idx, row in enumerate(results):
                # Debugging: Print results
                # print(f"Found item: {row[0]} with price {row[1]}")

                # Add labels for each result
                ttk.Label(self.item_results_frame, text=f"Name: {row[0]}", wraplength=400, justify="left").grid(row=idx,
                                                                                                           column=0,
                                                                                                           sticky="w",
                                                                                                           padx=5)
                ttk.Label(self.item_results_frame, text=f"Price: {row[1]}").grid(row=idx, column=1, sticky="w", padx=5)

                # Add clickable link
                link_label = tk.Label(self.item_results_frame, text="Open Link", foreground="blue", cursor="hand2")
                link_label.grid(row=idx, column=2, sticky="w", padx=5)
                link_label.bind("<Button-1>", lambda e, url=row[2]: webbrowser.open(url))

            # Update the scroll region of the canvas
            self.item_results_frame.update_idletasks()  # Ensure widgets are packed before recalculating
            self.canvas1.configure(scrollregion=self.canvas1.bbox("all"))
        else:
            # If no results, display message
            print("No items found matching the criteria.")
            ttk.Label(self.item_results_frame, text="No items found matching the criteria.").pack(pady=10)

    def log_out(self):
        self.controller.geometry("400x300")
        self.controller.show_frame(LoginFrame)

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.canvas1.yview_scroll(-1, "units")
        else:
            self.canvas1.yview_scroll(1, "units")

    def _on_mousewheel_cars(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    def create_cars_tab(self):
        """Create and populate the Items tab."""
        # Create a label at the top
        cars_label = ttk.Label(self.tab2, text="Cars", font=("Arial", 14, "bold"))
        cars_label.pack(pady=10)

        # Create a frame for the Scrape section
        scrape_frame = ttk.Frame(self.tab2)
        scrape_frame.pack(pady=10, fill="x", padx=10)

        ttk.Label(scrape_frame, text="Scrape:").grid(row=0, column=0, sticky="w", padx=5)
        self.car_scrape_entry = ttk.Entry(scrape_frame, width=25)
        self.car_scrape_entry.grid(row=0, column=1, sticky="w", padx=5)

        self.start_car_button = ttk.Button(scrape_frame, text="Start Scrape", command=self.start_car_scrape)
        self.start_car_button.grid(row=0, column=2, padx=5)

        stop_car_button = ttk.Button(scrape_frame, text="Stop Scrape", command=self.stop_car_scrape)
        stop_car_button.grid(row=0, column=3, padx=5)

        # Importance Section
        importance_label = ttk.Label(self.tab2, text="Importance", font=("Arial", 12, "bold"))
        importance_label.pack(pady=10)

        importance_frame = ttk.Frame(self.tab2)
        importance_frame.pack(pady=10, fill="x", padx=10)

        # Mileage Importance
        ttk.Label(importance_frame, text="Mileage (1-10):").grid(row=0, column=0, sticky="e", padx=5)
        self.mileage_importance_entry = ttk.Entry(importance_frame, width=5)
        self.mileage_importance_entry.grid(row=0, column=1, sticky="w", padx=5)

        # Year Importance
        ttk.Label(importance_frame, text="Year (1-10):").grid(row=1, column=0, sticky="e", padx=5)
        self.year_importance_entry = ttk.Entry(importance_frame, width=5)
        self.year_importance_entry.grid(row=1, column=1, sticky="w", padx=5)

        # Price Importance
        ttk.Label(importance_frame, text="Price (1-10):").grid(row=2, column=0, sticky="e", padx=5)
        self.price_importance_entry = ttk.Entry(importance_frame, width=5)
        self.price_importance_entry.grid(row=2, column=1, sticky="w", padx=5)

        # Centering the columns equally
        importance_frame.grid_columnconfigure(0, weight=1, uniform="equal")  # For label column
        importance_frame.grid_columnconfigure(1, weight=1, uniform="equal")  # For entry column

        # Slider Section
        ttk.Label(importance_frame, text="Slider (0 - 100):").grid(row=3, column=0, sticky="e", padx=5, pady=5)

        # Slider widget
        self.slider = ttk.Scale(importance_frame, from_=0, to=100, orient="horizontal",
                                command=self.update_slider_label)
        self.slider.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Label to display the value of the slider right next to the slider
        self.slider_value_label = ttk.Label(importance_frame, text="0.0")
        self.slider_value_label.grid(row=3, column=2, padx=5, pady=5, sticky="w")  # Place the label next to the slider

        # Tooltip Label (hidden initially)
        self.slider_tooltip = tk.Label(self.tab2, text="", font=("Arial", 10), bg="black", bd=1, relief="solid")
        self.slider_tooltip.place_forget()  # Start hidden

        # Bind slider events to tooltip
        self.slider.bind("<Enter>", self.show_slider_tooltip)
        self.slider.bind("<Motion>", self.update_tooltip_position)
        self.slider.bind("<Leave>", self.hide_slider_tooltip)
        # Validation Note
        validation_note = ttk.Label(self.tab2, text="* Values must be between 1 and 10.", font=("Arial", 10, "italic"),
                                    foreground="red")
        validation_note.pack(pady=5)

        separator = ttk.Separator(self.tab2, orient="horizontal")
        separator.pack(fill="x", pady=20)

        # Create a frame for the entry fields below the "Search" label
        search_frame = ttk.Frame(self.tab2)
        search_frame.pack(pady=10, fill="x", padx=10)

        # Brand Entry (right-aligned)
        ttk.Label(search_frame, text="Brand:").grid(row=0, column=0, sticky="e", padx=5)
        self.brand_entry = ttk.Entry(search_frame, width=25)
        self.brand_entry.grid(row=0, column=1, padx=5)

        # Extra Box for Brand with Name
        self.search_mileage_importance_entry = ttk.Entry(search_frame, width=5)
        self.search_mileage_importance_entry.grid(row=0, column=3, padx=5)
        ttk.Label(search_frame, text="Mileage (1-10):").grid(row=0, column=2, sticky="w", padx=5)

        # Model Entry (right-aligned)
        ttk.Label(search_frame, text="Model:").grid(row=1, column=0, sticky="e", padx=5)
        self.model_entry = ttk.Entry(search_frame, width=25)
        self.model_entry.grid(row=1, column=1, padx=5)

        # Extra Box for Model with Name
        self.search_year_importance_entry = ttk.Entry(search_frame, width=5)
        self.search_year_importance_entry.grid(row=1, column=3, padx=5)
        ttk.Label(search_frame, text="Year (1-10):").grid(row=1, column=2, sticky="w", padx=5)

        # Year Range Entry (right-aligned)
        ttk.Label(search_frame, text="Year Range:").grid(row=2, column=0, sticky="e", padx=5)
        self.year_range_entry_ = ttk.Entry(search_frame, width=25)
        self.year_range_entry_.grid(row=2, column=1, padx=5)

        # Extra Box for Year Range with Name
        self.search_price_importance_entry = ttk.Entry(search_frame, width=5)
        self.search_price_importance_entry.grid(row=2, column=3, padx=5)
        ttk.Label(search_frame, text="Price (1-10):").grid(row=2, column=2, sticky="w", padx=5)

        # Max Price Entry (right-aligned)
        ttk.Label(search_frame, text="Max Price:").grid(row=3, column=0, sticky="e", padx=5)
        self.max_price_entry = ttk.Entry(search_frame, width=25)
        self.max_price_entry.grid(row=3, column=1, padx=5)

        # Adjusting the Search Button Placement
        search_button = ttk.Button(search_frame, text="Search", command=self.search_cars)
        search_button.grid(row=4, column=1, columnspan=2, pady=10)

        # Create a Canvas for scrollable results
        self.canvas = tk.Canvas(self.tab2)
        self.canvas.pack(pady=10, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.tab2, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.results_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        self.results_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_cars)


    def show_value_on_hover(self, event):
        """Display the slider value when the mouse hovers over it."""
        self.update_slider_label(event)

    def update_slider_label(self, event=None):
        """Update the label with the current slider value."""
        value = round(self.slider.get(), 2)  # Get the current value of the slider
        self.slider_value_label.config(text=f"{value:.2f}")  # Update the label with the slider value

    def scrape_cars(self):
        """Simulate car scraping in a loop while the event is set."""
        car_to_scrape = self.car_scrape_entry.get()

        if not car_to_scrape.strip():
            print("Error: No car entered.")
            return

        def scraping_task():
            try:
                lowest_score = self.slider_value_label.cget("text")
                mileage_importance = int(self.mileage_importance_entry.get() or 1)
                price_importance = int(self.price_importance_entry.get() or 1)
                year_importance = int(self.year_importance_entry.get() or 1)
                print(f"Starting to scrape for car: {car_to_scrape}")
                print(f"Will email items with score higher than {lowest_score}")

                # Simulate the actual car scraping process
                scrape_offerUp.initialization(car_to_scrape)
                print('Scrape finished, email starting')

                Email.fetch_recent_highscore(lowest_score, car_to_scrape, price_importance, mileage_importance,
                                             year_importance)
                print('Emailing ended')

                # Instead of a long sleep, use periodic checks
                total_sleep_time = random.randint(1200, 2400)  # Total delay in seconds (20 to 40 minutes)
                start_time = time.time()
                while time.time() - start_time < total_sleep_time:
                    if not self.scraping_event.is_set():
                        print("Scraping stopped during sleep.")
                        return
                    time.sleep(5)  # Sleep in small increments so that the program is responsive

            except Exception as e:
                print(f"Error during scraping: {e}")

        # Start the scraping task in a background thread
        threading.Thread(target=scraping_task, daemon=True).start()

    def start_car_scrape(self):
        """Start the scraper thread for cars."""
        if not self.scraping_event.is_set():
            brand = self.car_scrape_entry.get().split()[0] if " " in self.car_scrape_entry.get() \
                else self.car_scrape_entry.get()

            con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
            con.execute('PRAGMA journal_mode=WAL;')
            cur = con.cursor()
            brand_lowered = brand.lower()

            try:
                cur.execute("SELECT id FROM items_in_categories WHERE name = ?", (brand_lowered,))
                brand_entry = cur.fetchone()

                if brand_entry:
                    print(f"Brand '{brand}' exists in the database.")
                else:
                    print(f"Brand '{brand}' does not exist in the database.")
                    self.show_add_item_form(brand_lowered)
                    return

            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return
            finally:
                con.close()

            self.scraping_event.set()

            self.sleep_prevention.prevent_sleep()

            self.car_scraper_thread = threading.Thread(target=self.scrape_cars, daemon=True)
            self.car_scraper_thread.start()

            # Update button text and color to indicate it's running
            self.start_car_button.config(text="Scraping...", state="disabled", style="StartButtonRunning.TButton")
            print("Car scraping started!")

    def show_add_item_form(self, brand):
        """Display a form to add a new item and category if needed."""
        form = tk.Toplevel(self.master)
        form.title("Add New Item")

        tk.Label(form, text=f"Item '{brand}' not found. Add to database.").pack(pady=10)

        tk.Label(form, text="Item Name:").pack(anchor="w")
        item_name_entry = tk.Entry(form)
        item_name_entry.insert(0, brand)
        item_name_entry.pack(fill="x", padx=10)

        tk.Label(form, text="Category:").pack(anchor="w")
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(form, textvariable=category_var)
        category_dropdown.pack(fill="x", padx=10)

        # Populate dropdown with existing categories
        con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
        con.execute('PRAGMA journal_mode=WAL;')
        cur = con.cursor()
        cur.execute("SELECT name FROM categories")
        categories = [row[0] for row in cur.fetchall()]
        con.close()

        category_dropdown["values"] = categories

        tk.Label(form, text="New Category (if applicable):").pack(anchor="w")
        new_category_entry = tk.Entry(form)
        new_category_entry.pack(fill="x", padx=10)

        def submit_item():
            item_name = item_name_entry.get().strip()
            selected_category = category_var.get()
            new_category = new_category_entry.get().strip()

            if not item_name:
                print("Item name is required.")
                return

            # Add new category if provided
            if new_category and new_category not in categories:
                try:
                    con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
                    con.execute('PRAGMA journal_mode=WAL;')
                    cur = con.cursor()
                    cur.execute("INSERT INTO categories (name) VALUES (?)", (new_category,))
                    con.commit()
                    print(f"New category '{new_category}' added.")
                    selected_category = new_category  # Use the new category
                except sqlite3.Error as e:
                    print(f"Database error: {e}")
                    return
                finally:
                    con.close()

            # Add item to the database
            try:
                con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
                con.execute('PRAGMA journal_mode=WAL;')
                cur = con.cursor()
                cur.execute("SELECT id FROM categories WHERE name = ?", (selected_category,))
                category_id = cur.fetchone()
                if not category_id:
                    print("Error: Selected category not found.")
                    return
                cur.execute("INSERT INTO items_in_categories (name, category_id) VALUES (?, ?)",
                            (item_name, category_id[0]))
                con.commit()
                print(f"Item '{item_name}' added to category '{selected_category}'.")
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            finally:
                con.close()
                form.destroy()

        tk.Button(form, text="Add Item", command=submit_item).pack(pady=10)
        tk.Button(form, text="Cancel", command=form.destroy).pack()

    def stop_car_scrape(self):
        """Stop the scraper thread for cars."""
        if self.scraping_event.is_set():
            self.scraping_event.clear()
            print("Stopping car scraping...")

            # Allow the sleep prevention to stop
            self.sleep_prevention.allow_sleep()

            # Wait for the scraper thread to terminate in a non-blocking way
            if self.car_scraper_thread.is_alive():
                self.master.after(100, self.check_scraper_thread)

            # Revert the button text and color
            self.start_car_button.config(text="Start Scrape", state="normal", style="StartButton.TButton")

    def check_scraper_thread(self):
        """Periodically check if the scraper thread has terminated."""
        if self.car_scraper_thread.is_alive():
            self.master.after(100, self.check_scraper_thread)
        else:
            print("Car scraping stopped successfully.")

    def show_slider_tooltip(self, event):
        if hasattr(self, "tooltip_show_id"):  # Cancel any scheduled tooltip
            self.tab2.after_cancel(self.tooltip_show_id)

        # Schedule the tooltip to show after a short delay
        self.tooltip_show_id = self.tab2.after(200, lambda: self.display_tooltip(event))

    def display_tooltip(self, event):
        """Display the tooltip near the mouse pointer."""
        # Dynamically get the root window
        root = self.winfo_toplevel()

        # Calculate tooltip position based on mouse pointer
        x = root.winfo_pointerx() - root.winfo_rootx() + 0  # Offset slightly to the right
        y = root.winfo_pointery() - root.winfo_rooty() + 1  # Offset slightly below

        # Update tooltip content and position
        value = round(self.slider.get(), 2)
        self.slider_tooltip.config(text=f"{value:.2f}")
        self.slider_tooltip.place(x=x, y=y)

    def update_tooltip_position(self, event):
        """Update the tooltip position near the mouse pointer."""
        # Dynamically get the root window
        root = self.winfo_toplevel()

        # Calculate new tooltip position based on mouse pointer
        x = root.winfo_pointerx() - root.winfo_rootx() - 10  # Offset slightly to the right
        y = root.winfo_pointery() - root.winfo_rooty() - 30  # Offset slightly below

        # Update tooltip content
        value = round(self.slider.get(), 2)
        self.slider_tooltip.config(text=f"{value:.2f}")

        # Move the tooltip to the new position
        self.slider_tooltip.place(x=x, y=y)

    def hide_slider_tooltip(self, event):
        self.slider_tooltip.place_forget()
        if hasattr(self, "tooltip_update_id"):
            self.tab2.after_cancel(self.tooltip_update_id)
        if hasattr(self, "tooltip_show_id"):
            self.tab2.after_cancel(self.tooltip_show_id)

    def search_cars(self):
        """Handle the Search functionality in Tab 2."""
        brand_name = self.brand_entry.get()
        model_name = self.model_entry.get()
        year_range = self.year_range_entry_.get()
        max_price = self.max_price_entry.get()

        print(f"Mileage Importance Entry: {self.search_mileage_importance_entry.get()}")
        print(f"Year Importance Entry: {self.search_year_importance_entry.get()}")
        print(f"Price Importance Entry: {self.search_price_importance_entry.get()}")

        try:
            search_mileage_importance = int(
                self.search_mileage_importance_entry.get().strip()) \
                if self.search_mileage_importance_entry.get().strip() else 1

            if not 0 < search_mileage_importance < 11:
                CustomMessageBox(self, "Mileage importance out of range", "Please enter a number between 1-10")
                return
            print(f'search mileage importance: {search_mileage_importance}')
        except ValueError:
            print('Value Error')
            CustomMessageBox(self, "Invalid mileage importance", "Please enter a number between 1-10.\n"
                                                                 "Can't be a decimal")
            return

        try:
            search_year_importance = int(
                self.search_year_importance_entry.get().strip()) if self.search_year_importance_entry.get().strip() \
                else 1

            if not 0 < search_year_importance < 11:
                CustomMessageBox(self, "Year importance out of range", "Please enter a number between 1-10")
                return
            print(f'search year importance: {search_year_importance}')
        except ValueError:
            print('Value Error')
            CustomMessageBox(self, "Invalid year importance", "Please enter a number between 1-10.\n"
                                                              "Can't be a decimal")
            return

        try:
            search_price_importance = int(
                self.search_price_importance_entry.get().strip()) if self.search_price_importance_entry.get().strip() \
                else 1

            if not 0 < search_price_importance < 11:
                CustomMessageBox(self, "Price importance out of range", "Please enter a number between 1-10")
                return

            print(f'search price importance: {search_price_importance}')

        except ValueError:
            print('Value Error')
            CustomMessageBox(self, "Invalid price importance", "Please enter a number between 1-10.\n"
                                                               "Can't be a decimal")
            return

        print(str(search_year_importance) + " " + str(search_price_importance) + " " + str(search_mileage_importance))
        print(str(search_price_importance) + ": price importance")
        print(str(search_mileage_importance) + ": mileage importance")
        print(str(search_year_importance) + ": year importance")


        # Process year range input
        if '-' in year_range:
            try:
                year_range_list = list(map(int, year_range.split('-')))
            except ValueError:
                print("Invalid year range format. Please provide numbers.")
                CustomMessageBox(self, "Invalid Year", "Invalid year or year range. "
                                                       "Please input valid entry")
                return
        elif year_range.strip():  # Check if year_range is not empty
            try:
                year_range_list = [int(year_range)]
            except ValueError:
                print("Invalid year format. Please provide a valid number.")
                CustomMessageBox(self, "Invalid Year", "Invalid year or year range. "
                                                       "Please input valid entry")
                return
        else:
            year_range_list = []

        print(year_range_list)

        item_info_for_search = [brand_name, model_name, year_range_list, max_price]
        print(f'{search_price_importance}price_importance')
        mode = 'search'
        scraping_car = None
        scoring_result = Scoring.fetch_car_data_with_scores(mode, item_info_for_search, search_price_importance,
                                                            search_mileage_importance, search_year_importance,
                                                            scraping_car)
        for i in scoring_result:
            print(i)
        print('done')
        print(item_info_for_search)
        # Check if item_name is empty
        if not brand_name:
            print("Please provide a brand name.")
            return

        try:
            max_price = float(max_price) if max_price else None
        except ValueError:
            print("Max Price must be a valid number.")
            return

        # Connect to the database
        con = sqlite3.connect("/Users/josephstaroverov/PycharmProjects/RunWebScraper/Scraper.db")
        con.execute('PRAGMA journal_mode=WAL;')
        cur = con.cursor()

        # Query setup
        query = """
            SELECT Items.name, CarDetails.price, CarDetails.miles, Items.Link
            FROM CarDetails
            JOIN Items ON CarDetails.item_id = Items.item_id
            WHERE Items.name LIKE '%' || ? || '%' COLLATE NOCASE
        """
        params = [(brand_name + " " + model_name)]
        car_name = (brand_name + " " + model_name)

        # Add price filter if provided
        if max_price is not None:
            query += " AND CarDetails.price <= ?"
            params.append(max_price)

        # Execute query
        cur.execute(query, params)
        results = cur.fetchall()
        con.close()

        # Clear previous search results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Check if results exist
        if results:
            for idx, row in enumerate(scoring_result):
                print(f'row: {row}')
                # Debugging: Print results
                # print(f"Found item: {row[0]} with price {row[1]}")

                # Add labels for each result
                ttk.Label(self.results_frame, text=f"Name: {row['name']}", wraplength=400, justify="left").grid(row=idx,
                                                                                                           column=0,
                                                                                                           sticky="w",
                                                                                                           padx=5)
                ttk.Label(self.results_frame, text=f"Price: {row['price']}").grid(row=idx, column=1, sticky="w", padx=5)
                ttk.Label(self.results_frame, text=f"Mileage: {row['miles']}").grid(row=idx, column=2, sticky="w", padx=5)
                # Add clickable link
                link_label = tk.Label(self.results_frame, text="Open Link", foreground="blue", cursor="hand2")
                link_label.grid(row=idx, column=3, sticky="w", padx=5)
                link_label.bind("<Button-1>", lambda e, url=row['link']: webbrowser.open(url))

                ttk.Label(self.results_frame, text=f"Score: {row['score']}").grid(row=idx, column=4, sticky='w', padx=5)

            # Update the scroll region of the canvas
            self.results_frame.update_idletasks()  # Ensure widgets are packed before recalculating
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        else:
            # If no results, display message
            print("No items found matching the criteria.")
            ttk.Label(self.results_frame, text="No items found matching the criteria.").pack(pady=10)


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('your_database.db')
        self.cursor = self.conn.cursor()

    def check_item_exists(self, item_name):
        """Check if the item exists in the items_in_categories table."""
        self.cursor.execute("SELECT * FROM items_in_categories WHERE name = ?", (item_name,))
        return self.cursor.fetchone() is not None

    def get_categories(self):
        """Fetch all categories from the categories table."""
        self.cursor.execute("SELECT id, name FROM categories")
        return self.cursor.fetchall()

    def add_category(self, category_name):
        """Add a new category to the categories table."""
        self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
        self.conn.commit()

    def add_item_to_category(self, item_name, category_id):
        """Add an item to the items_in_categories table."""
        self.cursor.execute("INSERT INTO items_in_categories (name, category_id) VALUES (?, ?)",
                            (item_name, category_id))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()


class ItemForm:
    def __init__(self, root, item_name, database_manager):
        self.root = root
        self.item_name = item_name
        self.db_manager = database_manager

        self.root.title("Add Item to Category")

        self.item_label = tk.Label(root, text=f"Item: {item_name}")
        self.item_label.pack()

        self.category_label = tk.Label(root, text="Select Category:")
        self.category_label.pack()

        # Dropdown for existing categories
        self.category_combobox = ttk.Combobox(root)
        categories = self.db_manager.get_categories()
        self.category_combobox['values'] = [cat[1] for cat in categories]  # Get category names
        self.category_combobox.pack()

        # Add button to confirm selection
        self.add_button = ttk.Button(root, text="Add Item", command=self.add_item)
        self.add_button.pack(pady=10)

        # Option to add new category
        self.new_category_button = ttk.Button(root, text="Add New Category", command=self.create_new_category)
        self.new_category_button.pack(pady=5)

    def add_item(self):
        category_name = self.category_combobox.get()
        category_id = self.get_category_id(category_name)

        if category_id is not None:
            # Add item to existing category
            self.db_manager.add_item_to_category(self.item_name, category_id)
            messagebox.showinfo("Success", f"Item '{self.item_name}' added to category '{category_name}'")
            self.root.destroy()
        else:
            messagebox.showwarning("Error", "Please select a valid category.")

    def create_new_category(self):
        new_category_name = self.category_combobox.get()

        if new_category_name:
            # Ask user if they want to create a new category
            confirm = messagebox.askyesno("Confirm", f"Do you want to create a new category '{new_category_name}'?")
            if confirm:
                self.db_manager.add_category(new_category_name)
                category_id = self.get_category_id(new_category_name)
                if category_id is not None:
                    self.db_manager.add_item_to_category(self.item_name, category_id)
                    messagebox.showinfo("Success",
                                        f"Item '{self.item_name}' added under the new category '{new_category_name}'")
                    self.root.destroy()
                else:
                    messagebox.showwarning("Error", "Failed to create new category.")
            else:
                messagebox.showinfo("Cancelled", "Category creation cancelled.")

    def get_category_id(self, category_name):
        """Get the category ID from the database by category name."""
        self.db_manager.cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = self.db_manager.cursor.fetchone()
        return result[0] if result else None


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()



# Email regex, "^[A-Za-z0-9]+([._-][A-Za-z0-9]+)*@[A-Za-z0-9-]+\.[A-Za-z]{2,}$"




# root = tk.Tk()
# style = ttk.Style()
# style.theme_use("default")  # Use the default theme
# style.configure("TFrame", background="white")
# insertion = tk.StringVar()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# entry = ttk.Entry(frm, textvariable=insertion, font=('calibre', 10, 'normal'))
# entry.grid(column=0, row=2)
# root.mainloop()