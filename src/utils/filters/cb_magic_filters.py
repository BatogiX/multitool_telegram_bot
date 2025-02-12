from models.callback_data import StartMenuCallbackData, HashMenuCallbackData, PasswordManagerCallbackData as PwManCb


class CbMagicFilters:
    @staticmethod
    def HashMenu_ENTER(cb_data) -> bool:
        return cb_data == HashMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()

    @staticmethod
    def StartMenu_ENTER(cb_data) -> bool:
        return cb_data == StartMenuCallbackData(action=StartMenuCallbackData.ACTIONS.ENTER).pack()

    @staticmethod
    def PasswordManager_ENTER(cb_data) -> bool:
        return cb_data == PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.ENTER).pack()

    @staticmethod
    def PasswordManager_CREATE_SERVICE(cb_data) -> bool:
        return cb_data == PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.CREATE_SERVICE).pack()

    @staticmethod
    def PasswordManager_DELETE_SERVICES(cb_data) -> bool:
        return cb_data == PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.DELETE_SERVICES).pack()

    @staticmethod
    def PasswordManager_DELETE_PASSWORD(cb_data) -> bool:
        return cb_data == PwManCb.PasswordManager(action=PwManCb.PasswordManager.ACTIONS.DELETE_PASSWORD).pack()
