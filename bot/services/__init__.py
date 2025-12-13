from bot.config import CATEGORIES_FILE, TRANSACTIONS_FILE, USERS_FILE
from bot.storage.json_store import JsonStore
from bot.services.category_service import CategoryService
from bot.services.export_service import ExportService
from bot.services.report_service import ReportService
from bot.services.transaction_service import TransactionService
from bot.services.user_service import UserService


def create_services():
    user_store = JsonStore(USERS_FILE)
    category_store = JsonStore(CATEGORIES_FILE)
    transaction_store = JsonStore(TRANSACTIONS_FILE)

    user_service = UserService(user_store)
    category_service = CategoryService(category_store)
    transaction_service = TransactionService(transaction_store)
    report_service = ReportService(transaction_service, category_service, user_service)
    export_service = ExportService(report_service)

    return {
        "users": user_service,
        "categories": category_service,
        "transactions": transaction_service,
        "reports": report_service,
        "exports": export_service,
    }
