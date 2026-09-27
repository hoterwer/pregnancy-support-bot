from aiogram.fsm.state import State, StatesGroup


class TrackerStates(StatesGroup):
    waiting_for_due_date = State()


class ChatStates(StatesGroup):
    talking = State()


class MoodStates(StatesGroup):
    waiting_for_note = State()


class LetterStates(StatesGroup):
    waiting_for_letter = State()


class NameStates(StatesGroup):
    waiting_for_name = State()


class DoctorQuestionStates(StatesGroup):
    waiting_for_question = State()


class ReminderStates(StatesGroup):
    waiting_for_custom_text = State()
    waiting_for_custom_daily_time = State()
    waiting_for_vitamins_time = State()