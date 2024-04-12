from aiogram.fsm.state import State, StatesGroup

class Support(StatesGroup):
    biography_intro_1 = State()
    biography_intro_2 = State()
    biography_intro_3 = State()
    biography_intro_show = State()
    
