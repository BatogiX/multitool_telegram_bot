class Service:
    key: str = "service"

    def __new__(cls, service_name: str):
        return {cls.key: service_name}
