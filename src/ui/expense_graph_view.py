from tkinter import ttk, constants, StringVar, OptionMenu
from matplotlib import pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.login_service import login_service
from repositories.expense_repository import ExpenseRepository
from services.expense_service import ExpenseService
from entities.category import Category


class ExpenseGraph:
    def __init__(self, root, expense_tracker_homescreen):
        self._root = root
        self._return_to_homescreen = expense_tracker_homescreen
        self._frame = None
        self._style = None

        self.user = login_service.find_logged_in_user()
        self.expense_service = ExpenseService(ExpenseRepository(), self.user)

        self._selected_category = None

        self._graph_canvas = None

        self._initialize()

    def configure(self):
        self._frame.pack(fill=constants.X)
        self._root.configure(background="#AFE4DE")

    def destroy(self):
        self._frame.destroy()

    def _initialize(self):
        self._frame = ttk.Frame(master=self._root)
        self._table_frame = ttk.Frame(master=self._frame)
        self._frame.grid_columnconfigure(1, weight=1, minsize=200)

        self._style = ttk.Style()
        self._style.configure("TFrame", background="#AFE4DE")

        header_label = ttk.Label(
            master=self._frame, text="View Your Expense History as Graphs", background="#AFE4DE")
        return_to_homescreen = ttk.Button(
            master=self._frame, text="Home", command=self._return_to_homescreen)
        
        return_to_homescreen.grid(row=0, column=3, sticky=(
            constants.E), padx=5, pady=5)
        header_label.grid(row=0, columnspan=2, sticky=(
            constants.N), padx=5, pady=5)
        
        expense_list=self.expense_service.list_all_expenses()
        if expense_list:
            self._initialize_view_graphs()
        else:
            note = ttk.Label(
                        master=self._frame, text="You do not currently have any recorded expenses", background="#AFE4DE")
            note.grid(row=4, padx=5, pady=5)

    def _initialize_view_graphs(self):
        show_all_expenses=ttk.Button(master=self._frame, text="View graph for all expenses", command=self._display_expense_graph)
        show_all_expenses.grid(row=1, padx=5, pady=5)

        choose_category_label=ttk.Label(master=self._frame, text="Choose category to view as graph", background="#AFE4DE")
        choose_category_label.grid(row=2, padx=5, pady=5)

        self._selected_category = StringVar()
        category_options = self.expense_service.list_all_categories()
        if category_options:
            self._expense_category_dropdown = OptionMenu(
                self._frame, self._selected_category, *category_options)
            self._expense_category_dropdown.grid(row=2, column=1, padx=5, pady=5)
        
        show_expenses_by_category=ttk.Button(master=self._frame, text="View graph for expenses by category", command=self._display_category_graph)
        show_expenses_by_category.grid(row=2, column=2, padx=5, pady=5)
        
    def _display_expense_graph(self):
        if self._graph_canvas:
            self._graph_canvas.get_tk_widget().destroy()

        expense_plot=self.expense_service.graph_all_expenses().get_figure()

        self._graph_canvas = FigureCanvasTkAgg(expense_plot, self._frame)
    
        self._graph_canvas.get_tk_widget().grid(row=3, column=1)
    
    def _display_category_graph(self):
        if self._graph_canvas:
            self._graph_canvas.get_tk_widget().destroy()
        
        selected_category = self._selected_category.get()

        if selected_category:
            category=Category(selected_category)
            expense_list=self.expense_service.list_expenses_by_category(category)
            if expense_list:
                expense_plot=self.expense_service.graph_expenses_by_category(category).get_figure()

                self._graph_canvas = FigureCanvasTkAgg(expense_plot, self._frame)
            
                self._graph_canvas.get_tk_widget().grid(row=3, column=1)

            else:
                note = ttk.Label(
                        master=self._frame, text="You do not currently have any recorded expenses in this category", background="#AFE4DE")
                note.grid(row=4, padx=5, pady=5)
    
        
