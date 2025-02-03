from aiogram import Router

password_manager_cb_router = Router(name=__name__)


# @password_manager_cb_router.callback_query(CbMagicFilters.PasswordManager_ENTER(F.data))
# async def enter_passwd_manager_menu(callback_query: CallbackQuery, state: FSMContext):
#     if is_user_have_verificate_hash():
#         await callback_query.message.edit_text(
#             text="Enter your master-password to continue",
#             reply_markup=inline_kb
#         )
#         await state.set_state(PasswordManagerStates.ReadMasterPassword)
#     else:
#         await callback_query.message.edit_text(
#             text="You don't have any passwords yet. Create one now?",
#         )