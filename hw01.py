from collections import UserDict
from _datetime import datetime, date, timedelta
import re


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments."
        except TypeError:
            return "Invalid input."

    return inner


def is_valid_date(birthday: date, start: date, end: date) -> bool:
    adjusted_birthday = birthday.replace(year=start.year)
    if adjusted_birthday < start and adjusted_birthday.year != end.year:
        adjusted_birthday = adjusted_birthday.replace(year=end.year)
    if start <= adjusted_birthday <= end:
        return True
    return False


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(phone):
        return bool(re.fullmatch(r"\d{10}", phone))


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Phone not found")
        if not Phone.validate(new_phone):
            raise ValueError("New phone must contain exactly 10 digits.")
        phone_obj.value = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        bd = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{self.name.value}: phones: {phones_str}, birthday: {bd}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def birthdays(self):
        result = []
        today = datetime.now().date()
        future_date = today + timedelta(days=7)
        for record in self.data.values():
            if record.birthday is None:
                continue
            if is_valid_date(record.birthday.value, today, future_date):
                result.append((record.name, record.birthday.value))
        result.sort(key=lambda item: item[1])
        return result


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    phones = "; ".join(p.value for p in record.phones)
    return phones


@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(record) for record in book.values())


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.birthday:
        return "No birthday set."
    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def birthdays(book):
    upcoming = book.birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{name}: {date}" for name, date in upcoming)


def parse_input(user_input):
    parts = user_input.split()
    return parts[0].lower(), parts[1:]


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(*args, book))

        elif command == "change":
            print(change_contact(*args, book))

        elif command == "phone":
            print(show_phones(*args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(*args, book))

        elif command == "show-birthday":
            print(show_birthday(*args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
