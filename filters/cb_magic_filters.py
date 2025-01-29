from callback_data import StartMenu, HashMenu


class CbMagicFilters:
    @staticmethod
    def HashMenu_ENTER(cb_data) -> bool:
        return cb_data == HashMenu(action=StartMenu.ACTIONS.ENTER).pack()

    @staticmethod
    def StartMenu_ENTER(cb_data) -> bool:
        return cb_data == StartMenu(action=StartMenu.ACTIONS.ENTER).pack()