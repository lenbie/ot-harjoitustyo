from tkinter import Tk
from ui.login_view import LoginView
from ui.create_account_view import CreateAccountView
from ui.expense_tracker_view import ExpenseTrackerView


class UI:
    def __init__(self, root):
        self._root = root
        self._current_view = None

    def start(self):
        self._show_login_view()

    def _hide_current_view(self):
        if self._current_view:
            self._current_view.destroy()

        self._current_view = None

    def _handle_login(self):
        self._show_login_view()

    def _handle_create_account(self):
        self._show_create_account_view()

    def _handle_expense_tracker(self):
        self._show_expense_tracker_view()

    def _show_login_view(self):
        self._hide_current_view()

        self._current_view = LoginView(
            self._root, self._handle_create_account, self._handle_expense_tracker)
        self._current_view.configure()

    def _show_create_account_view(self):
        self._hide_current_view()

        self._current_view = CreateAccountView(
            self._root, self._handle_expense_tracker, self._handle_login)
        self._current_view.configure()

    def _show_expense_tracker_view(self):
        self._hide_current_view()

        self._current_view = ExpenseTrackerView(self._root, self._handle_login)
        self._current_view.configure()