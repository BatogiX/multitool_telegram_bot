from callback_data import StartMenuCallbackData, HashMenuCallbackData, PasswordManagerCallbackData


class CbMagicFilters:
    @staticmethod
    def HashMenu_ENTER(cb_data) -> bool:
        return cb_data == HashMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()

    @staticmethod
    def StartMenu_ENTER(cb_data) -> bool:
        return cb_data == StartMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()

    @staticmethod
    def PasswordManager_ENTER(cb_data) -> bool:
        return cb_data == PasswordManagerCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()