from aiogram.filters.callback_data import CallbackData

class NameCallback(CallbackData, prefix="my"):
    tag:str
    edit_data:str
    id:str