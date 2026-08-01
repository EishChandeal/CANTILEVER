import customtkinter
from src.config import APP_NAME, PALETTE
from src.services.finance_service import FinanceService
from src.services.budget_service import BudgetService
from src.services.savings_service import SavingsService
from src.services.settings_service import SettingsService

from src.gui.components.sidebar import Sidebar
from src.gui.components.header import Header

from src.gui.pages.dashboard_frame import DashboardFrame
from src.gui.pages.transactions_frame import TransactionsFrame
from src.gui.pages.budget_frame import BudgetFrame
from src.gui.pages.savings_frame import SavingsFrame
from src.gui.pages.reports_frame import ReportsFrame
from src.gui.pages.settings_frame import SettingsFrame

class App(customtkinter.CTk):
    """Main Application Window for Personal Finance System."""

    PAGE_TITLES = {
        "dashboard": "Dashboard",
        "transactions": "Transactions",
        "budget": "Budget Manager",
        "savings": "Savings Goals",
        "reports": "Reports & Visualizations",
        "settings": "Settings & Configurations"
    }

    def __init__(self, db_manager):
        super().__init__()

        self.db_manager = db_manager
        self.title(APP_NAME)
        self.geometry("1150x700")
        self.minsize(1150, 700)
        self.configure(fg_color=PALETTE["BG"])

        # Instantiate Services Layer
        self.services = {
            "finance": FinanceService(db_manager),
            "budget": BudgetService(db_manager),
            "savings": SavingsService(db_manager),
            "settings": SettingsService(db_manager)
        }

        # Layout Configuration (2 Columns: Sidebar | Main Content)
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Left Sidebar
        self.sidebar = Sidebar(self, on_navigate_callback=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Right Main Area Container
        self.main_container = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")

        self.main_container.grid_rowconfigure(0, weight=0, minsize=65)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 2a. Header
        self.header = Header(self.main_container, initial_title=self.PAGE_TITLES["dashboard"])
        self.header.grid(row=0, column=0, sticky="ew")

        # 2b. Page Content Container
        self.content_area = customtkinter.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew")

        # Instantiate Page Frames
        self.pages = {}
        page_classes = {
            "dashboard": DashboardFrame,
            "transactions": TransactionsFrame,
            "budget": BudgetFrame,
            "savings": SavingsFrame,
            "reports": ReportsFrame,
            "settings": SettingsFrame
        }

        for key, cls in page_classes.items():
            frame = cls(self.content_area, self.db_manager, self.services)
            self.pages[key] = frame

        self.current_page_key = None

        # Display initial page on startup
        self.show_page("dashboard")

    def show_page(self, page_key: str):
        """Swaps the visible page frame in the content area."""
        if page_key not in self.pages:
            return

        # Hide current page frame
        if self.current_page_key and self.current_page_key in self.pages:
            self.pages[self.current_page_key].pack_forget()

        # Display selected page frame
        self.current_page_key = page_key
        selected_frame = self.pages[page_key]
        selected_frame.pack(fill="both", expand=True)

        # Update Header Title
        title = self.PAGE_TITLES.get(page_key, "Finance App")
        self.header.set_title(title)

        # Call page refresh hook
        selected_frame.refresh()
