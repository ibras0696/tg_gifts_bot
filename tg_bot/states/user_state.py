from aiogram.fsm.state import StatesGroup, State

# Состояние дял удаления сообщение invoce
class DeleteInvoiceState(StatesGroup):
    message_invoice = State()