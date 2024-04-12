from aiogram.dispatcher.filters.state import StatesGroup, State

class DataCollectionForm(StatesGroup):
    full_name = State()
    date_of_birth = State()
    date_of_death = State()
    place_of_birth = State()
    place_of_death = State()
    citizenship = State()
    children = State()
    spouse = State()
    education = State()
    career = State()
    epitaph = State()
    biography = State()
