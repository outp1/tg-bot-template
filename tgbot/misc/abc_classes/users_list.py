from collections.abc import MutableSequence


class UsersList(MutableSequence):
    def __init__(self, users_list):
        self.users_list = users_list

    def __getitem__(self, i):
        return self.users_list[i]

    def __len__(self):
        return len(self.users_list)

    def __delitem__(self, key):
        del self.users_list[key]

    def __setitem__(self, key, value):
        self.users_list[key, value]

    def insert(self, key, value):
        self.users_list.insert(key, value)

    def __str__(self):
        return str(self.users_list)
