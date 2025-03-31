from utils import BotUtils

SERVICE_TEXT = "*Service*: "

#  Callback handler texts
ENTER_TEXT = "Choose option"
IMPORT_FROM_FILE_TEXT = "Please send the .csv file and enter your Master Password in caption"
NO_SERVICES_TEXT = "You don't have any services yet. Create one now?"
DELETE_SERVICES_TEXT = "Are you sure you want to delete all services?\n\nIf yes - please enter your Master Password"
ASK_MASTER_PASSWORD_TEXT = "Please enter your Master Password"
CREATE_PASSWORD_TEXT = "Please enter your <Master Password> <login> <password>"
CHANGE_SERVICE_TEXT = "Please enter new service name"
DELETE_SERVICE_TEXT = f"Are you sure you want to delete this service?\n\nIf yes - please enter your Master Password"
DELETE_PASSWORD_TEXT = "\n\nAre you sure you want to delete this password?\nIf yes - please enter your <Master Password> <login> <password>"
CREATE_SERVICE_TEXT = "Please enter <Master Password> <service name> <login> <password>"
LOGIN_TEXT = "\n\n*Login*: "
PASSWORD_TEXT = "\n*Password*: "
WARNING = (
    "❗WARNING❗\n"
    "If you lose your Master Password you won't be able to decrypt your passwords. "
    "We do not store your Master Password and key for encryption/decryption in any way, "
    "so we won't be able to recover it for you.\n\n"
    "Your Master Password must be at least 12 characters long and contain at least one number, "
    "one uppercase letter, one lowercase letter and one special character.\n\n"
)


def gen_services_text(services_offset: int) -> str:
    return (
        "Choose service"
        f"\nPage: {services_offset + 1}"
    )


def gen_credentials(service: str, login: str, password: str) -> str:
    service = BotUtils.add_protocol(service)
    service = BotUtils.escape_markdown_v2(service)
    return (
        SERVICE_TEXT + service +
        LOGIN_TEXT + f"`{login}`" +
        PASSWORD_TEXT + f"`{password}`"
    )


# FSM handler texts
IMPORT_FROM_FILE_FSM = "Passwords were successfully imported from file\n\n"
EXPORT_TO_FILE_TEXT = "Passwords were successfully exported to file"
PASSWORD_DELETED_TEXT = "Password was deleted successfully\n\n"
ALL_SERVICES_DELETED_TEXT = "All services deleted successfully"
SERVICE_DELETED_TEXT = "Service was deleted successfully\n\n"


def gen_passwords_text(service: str, pwds_offset: int) -> str:
    service = BotUtils.add_protocol(service)
    return (
        SERVICE_TEXT + service +
        "\n\nChoose your login to see password" +
        f"\nPage: {pwds_offset + 1}"
    )
