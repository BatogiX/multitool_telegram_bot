from models.callback_data import StartMenuCallbackData, HashMenuCallbackData


class CbMagicFilters:
    @staticmethod
    def HashMenu_ENTER(cb_data) -> bool:
        return cb_data == HashMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()

    @staticmethod
    def StartMenu_ENTER(cb_data) -> bool:
        return cb_data == StartMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()
