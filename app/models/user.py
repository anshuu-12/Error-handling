class User:
    def __init__(self, id: int, name: str, email: str, phone: str, age: int, status: str = "active"):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.age = age
        self.status = status