from tkinter import ttk, constants, OptionMenu, StringVar, messagebox, END, VERTICAL
from services.login_service import login_service
from repositories.expense_repository import ExpenseRepository
from services.expense_service import ExpenseService, InvalidInputError
from entities.category import Category
from entities.expense import Expense


class ExpenseOverview:
    """This class manages the UI view of the expense tracker, where the user can view tables of their
    entered expenses, and edit their expenses and categories
    """

    def __init__(self, root, expense_tracker, expense_graph, expense_creation, expense_overview):
        """Class constructor, creates the 'expense overview' view

        Args:
            root (Tkinter frame): The Tkinter frame within which the login view resides
            expense_tracker: Callable value, called when the user chooses to return to the expense tracker home screen
            expense_graph: Callable value, called when the user clicks the "View Expenses as Graph" button
        """
        self._root = root
        self._handle_return_to_homescreen = expense_tracker
        self._expense_graph_view = expense_graph
        self._handle_create_expense = expense_creation
        self._expense_overview = expense_overview

        self._frame = None
        self._style = None

        self.user = login_service.find_logged_in_user()
        self.expense_service = ExpenseService(ExpenseRepository(), self.user)

        self._expense_name = None
        self._expense_amount = None
        self._expense_date = None
        self._expense_category = None

        self._selected_category = None
        self._selected_table_category = None
        self._expense_table = None

        self._display_total = None
        self._display_category_total = None

        self._selected_expense_editable = None
        self._expense_user_change = None

        self._selected_category_editable = None
        self._category_user_change = None
        self._edit_categories_dropdown = None

        self._initialize()

    def configure(self):
        """Shows the expense overview view
        """
        self._frame.pack(fill=constants.X)
        self._root.configure(background="#AFE4DE")

    def destroy(self):
        """Destroys the expense overview view
        """
        self._frame.destroy()

    def _initialize(self):
        self._frame = ttk.Frame(master=self._root)

        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_columnconfigure(1, weight=1)
        self._frame.grid_columnconfigure(2, weight=1)
        self._frame.grid_columnconfigure(3, weight=1)
        self._frame.grid_columnconfigure(4, weight=1)
        for row in range(self._frame.grid_size()[1]):
            self._frame.grid_rowconfigure(row, weight=1)

        self._style = ttk.Style()
        self._style.configure("TFrame", background="#AFE4DE")

        self._initialize_start_view()

    def _initialize_window_size(self):
        self._root.geometry("")
        window_width = self._root.winfo_screenwidth()//2
        window_height = self._root.winfo_screenheight()//4
        screen_width = (self._root.winfo_screenwidth() // 2) - \
            (window_width//2)
        screen_height = (self._root.winfo_screenheight() //
                         2) - (window_height//2)

        self._root.geometry(
            f"{int(window_width)}x{int(window_height)}+{int(screen_width)}+{int(screen_height)}")

    def _initialize_start_view(self):
        header_label = ttk.Label(
            master=self._frame, text="Your Expenses", background="#AFE4DE")

        home_button = ttk.Button(
            master=self._frame, text="Home", command=self._handle_return_to_homescreen)

        create_expenses_button = ttk.Button(
            master=self._frame, text="Create Expenses", command=self._handle_create_expense)

        graph_view_button = ttk.Button(
            master=self._frame, text="View expenses as graph", command=self._expense_graph_view)

        header_label.grid(row=0, column=0, sticky=(
            constants.NW), padx=5, pady=5)
        home_button.grid(row=0, column=3, sticky=(
            constants.NE), padx=5, pady=5)
        create_expenses_button.grid(row=0, column=2, sticky=(
            constants.NE), padx=5, pady=5)
        graph_view_button.grid(row=0, column=1, padx=5,
                               pady=5, sticky=(constants.NE))

        self._initialize_view_expense_total()
        self._initialize_view_expense_tables()

    def _initialize_view_expense_total(self):
        total = self.expense_service.get_total_all_expenses_by_user()
        self._display_total = ttk.Label(
            master=self._frame, text=f"Total amount spent: {total} €", background="#AFE4DE")

        self._display_total.grid(row=1, sticky=(
            constants.W), padx=5, pady=5)

    def _initialize_view_category_total(self, category):
        if self._display_total:
            self._display_total.destroy()
        total = self.expense_service.get_total_by_category_and_user(category)
        self._display_category_total = ttk.Label(
            master=self._frame, text=f"Total spending in the {category.name} category: {total} €", background="#AFE4DE")

        self._display_category_total.grid(row=1,
                                          sticky=(constants.W), padx=5, pady=5)

    def _initialize_view_expense_tables(self):
        table_view_all_button = ttk.Button(
            master=self._frame, text="View all expenses as table", command=self._get_expense_table)
        table_view_by_category_button = ttk.Button(
            master=self._frame, text="View expenses by category as table", command=self._get_expense_category_table)

        table_view_all_button.grid(row=2, column=0, padx=5, pady=5, sticky=(
            constants.W))
        table_view_by_category_button.grid(row=2, column=1, padx=5, pady=5)

        self._get_expense_table()
        self._get_category_dropdown()

        expense_list = self.expense_service.list_all_expenses()
        if expense_list:
            self._root.geometry("")
            self._root.geometry("+105+105")
            self._initialize_edit_expenses()
            self._initialize_edit_categories()
        else:
            self._initialize_window_size()

    def _get_expense_table(self):
        if self._expense_table:
            self._delete_table()

        if self._display_category_total:
            self._display_category_total.destroy()

        self._initialize_view_expense_total()

        expense_list = self.expense_service.list_all_expenses()

        if expense_list:
            column_names = ["Expense Name", "Amount", "Date", "Category"]
            self._expense_table = ttk.Treeview(
                master=self._frame, columns=column_names, show="headings", selectmode="browse")
            self._style.configure("Treeview.Heading", background="#AFE4DE")
            for column in column_names:
                self._expense_table.heading(column, text=column)
            for expense in expense_list:
                self._expense_table.insert("", END, values=expense)
            self._expense_table.grid(
                row=4, columnspan=2, sticky=(constants.NSEW), padx=5, pady=5)
            self._insert_table_scrollbar(self._expense_table)

        else:
            note = ttk.Label(
                master=self._frame, text="You do not currently have any recorded expenses", background="#AFE4DE")
            note.grid(row=4, padx=5, pady=5, sticky=(constants.NSEW))

    def _get_expense_category_table(self):
        if self._expense_table:
            self._delete_table()

        if self._display_category_total:
            self._display_category_total.destroy()

        category = self._selected_table_category.get()

        if category:
            expense_list = self.expense_service.list_expenses_by_category(
                Category(category))

            self._initialize_view_category_total(Category(category))

            if expense_list:

                column_names = ["Expense Name", "Amount", "Date", "Category"]
                self._expense_table = ttk.Treeview(
                    master=self._frame, columns=column_names, show="headings", selectmode="browse")
                self._style.configure("Treeview.Heading", background="#AFE4DE")

                for column in column_names:
                    self._expense_table.heading(column, text=column)
                for expense in expense_list:
                    self._expense_table.insert("", END, values=expense)
                self._expense_table.grid(
                    row=4, columnspan=2, sticky=constants.NSEW, padx=5, pady=5)

                self._insert_table_scrollbar(self._expense_table)

            else:
                note = ttk.Label(
                    master=self._frame, text="You do not currently have any recorded expenses", background="#AFE4DE")
                note.grid(row=4, padx=5, pady=5)

    def _delete_table(self):
        for element in self._expense_table.get_children():
            self._expense_table.delete(element)

    def _insert_table_scrollbar(self, table):
        scrollbar = ttk.Scrollbar(
            self._frame, orient=VERTICAL, command=table.yview)
        table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=4, column=2, sticky=(constants.NS, constants.W))

    def _get_category_dropdown(self):
        self._selected_table_category = StringVar()
        category_options = self.expense_service.list_all_categories()
        if category_options:
            expense_category_dropdown = OptionMenu(
                self._frame, self._selected_table_category, *category_options)
            expense_category_dropdown.grid(
                row=3, column=1, padx=5, pady=5, sticky=(constants.EW))

    def _initialize_edit_expenses(self):
        edit_expenses_header = ttk.Label(
            master=self._frame, text="Edit and Delete Expenses", background="pink")
        edit_expense_label = ttk.Label(
            master=self._frame, text="Choose expense to edit by selecting it via click, choose expense aspect to edit in the dropdown and then fill in changed value in the text field.", background="#AFE4DE")

        self._selected_expense_editable = StringVar()
        edit_options = ["Name", "Amount", "Date", "Category", "Delete"]
        edit_expense_dropdown = OptionMenu(
            self._frame, self._selected_expense_editable, *edit_options)

        self._expense_user_change_input = ttk.Entry(master=self._frame)

        edit_expenses_header.grid(row=15, padx=10, pady=10, sticky=(
            constants.E, constants.W))
        edit_expense_label.grid(row=16, padx=5, pady=5, sticky=(
            constants.E, constants.W))
        edit_expense_dropdown.grid(row=17, padx=5, pady=5, sticky=(
            constants.E, constants.W))
        self._expense_user_change_input.grid(row=18, sticky=(
            constants.E, constants.W), padx=5, pady=5)

        edit_expense_button = ttk.Button(
            master=self._frame, text="Edit Expense", command=self._edit_expenses)
        edit_expense_button.grid(row=19, padx=5, pady=5, sticky=(
            constants.E, constants.W))

    def _edit_expenses(self):
        editable = self._selected_expense_editable.get()
        chosen_expense = self._expense_table.focus()

        if editable and chosen_expense:
            chosen_expense_details = self._expense_table.item(chosen_expense)

            old_expense = Expense(chosen_expense_details.get("values")[0], chosen_expense_details.get("values")[1],
                                  chosen_expense_details.get("values")[2], chosen_expense_details.get("values")[3])

            if editable == "Delete":
                self.expense_service.delete_expense(old_expense)

                remaining_expenses = self.expense_service.list_all_expenses()
                if not remaining_expenses:
                    self._expense_overview()
                    return

                else:
                    self._get_category_dropdown()
                    self._initialize_edit_categories()

            user_change = self._expense_user_change_input.get()

            if user_change:
                if editable == "Name":
                    self.expense_service.edit_expense_name(
                        user_change, old_expense)

                elif editable == "Amount":
                    try:
                        self.expense_service.edit_expense_amount(
                            user_change, old_expense)
                    except InvalidInputError:
                        self._display_error_message(
                            "Invalid input. Make sure you have entered a nonnegative numeric amount")

                elif editable == "Date":
                    try:
                        self.expense_service.edit_expense_date(
                            user_change, old_expense)
                    except InvalidInputError:
                        self._display_error_message(
                            "Invalid input. Make sure you have entered a valid date in YYYY-MM-DD format")

                elif editable == "Category":
                    self.expense_service.edit_expense_category(
                        user_change, old_expense)
                    self._get_category_dropdown()
                    self._initialize_edit_categories()

            self._expense_user_change_input.delete(0, constants.END)
            self._get_expense_table()

    def _initialize_edit_categories(self):
        edit_categories_header = ttk.Label(
            master=self._frame, text="Edit and Delete Categories", background="pink")
        edit_categories_label = ttk.Label(
            master=self._frame, text="Choose category to edit or delete by selecting it from the dropdown and to edit, fill in the changed name in the text field. Deleting a category moves all expenses in that category to 'undefined'", background="#AFE4DE")

        self._selected_category_editable = StringVar()
        categories = self.expense_service.list_all_categories()
        if categories:
            self._edit_categories_dropdown = OptionMenu(
                self._frame, self._selected_category_editable, *categories)

            self._category_user_change_input = ttk.Entry(master=self._frame)

            edit_categories_header.grid(row=20, padx=10, pady=10, sticky=(
                constants.E, constants.W))
            edit_categories_label.grid(row=21, padx=5, pady=5, sticky=(
                constants.E, constants.W))
            self._edit_categories_dropdown.grid(row=22, padx=5, pady=5, sticky=(
                constants.E, constants.W))
            self._category_user_change_input.grid(row=23, sticky=(
                constants.E, constants.W), padx=5, pady=5)

            edit_categories_button = ttk.Button(
                master=self._frame, text="Edit Category", command=self._edit_categories)
            edit_categories_button.grid(row=24, padx=5, pady=5, sticky=(
                constants.E, constants.W))

            delete_category_button = ttk.Button(
                master=self._frame, text="Delete Category", command=self._delete_categories)
            delete_category_button.grid(row=25, padx=5, pady=5, sticky=(
                constants.E, constants.W))

            self._get_category_dropdown()

    def _edit_categories(self):
        editable = self._selected_category_editable.get()

        if editable:
            old_category = Category(editable)
            new_category = self._category_user_change_input.get()
            self.expense_service.rename_category(new_category, old_category)

            self._expense_user_change_input.delete(0, constants.END)
            self._edit_categories_dropdown.destroy()
            self._initialize_edit_categories()
            self._get_expense_table()

    def _delete_categories(self):
        editable = self._selected_category_editable.get()

        if editable:
            old_category = Category(editable)
            self.expense_service.delete_category(old_category)
            self._edit_categories_dropdown.destroy()
            self._initialize_edit_categories()
            self._get_expense_table()

    def _display_error_message(self, message):
        messagebox.showerror("Error", message)
