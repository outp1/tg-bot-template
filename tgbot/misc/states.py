from aiogram.dispatcher.filters.state import State, StatesGroup

# StatesGroup not calculated for iteration. Just a class.
class AdminStates(StatesGroup):
    find_user = State()

    newad_header = State() 
    newad_text = State()

    advert_media = State()
    advert_kbtext = State()
    advert_kbtype = State()
    advert_kbcontent = State()
    advert_data = State()
    advert_text = State()

    find_advert = State()

    advert_sending_date = State()
