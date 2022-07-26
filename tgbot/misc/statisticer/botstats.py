from typing import Union
import logging
import datetime
import sys

import pytz


class BotStatistic: 
    
    def __init__(self, users_list: list, reg_date_index: Union[str, int] = None,
            logger: logging.Logger = logging.Logger('BotStats')):
        self.users_list = users_list
        self.logger = logger
        self.reg_date_index = reg_date_index


    async def regs_number(self, timedelta: int, reg_date_index: Union[str, int] = None):
        """Returns the number of registrations in the bot based on time span

:param timedelta: is a number that is added to the date of the function call to filter users
:param reg_date_index: is name or num of index of users_list dictionary item with registration date info 

"""
        if reg_date_index is None or self.users_list[0].get(reg_date_index) is None:
            if self.reg_date_index:
                reg_date_index = self.reg_date_index
            else:
                for item in self.users_list:
                    for key, value in item.items():  
                        if type(value) == datetime.datetime: 
                            reg_date_index = key
        today = datetime.datetime.now(pytz.timezone('Europe/Moscow')) #TODO: change timezone feature
        regs_number = 0
        for user in self.users_list:
            if user[reg_date_index] >= (today - datetime.timedelta(days=30)):
                regs_number += 1
        return regs_number

    async def sorted_users(self, num_of_lines: int = 1, sort_index: Union[str, int] = None, reverse: bool = True):
        """Returns a list of users sorted by special index

:param num_of_lines: is num of list lenght
:param sort_index: is name or num of index of users_list dictionary item with registration date info 
:param reverse: override as False to change list direction

If sort_index is not set, the instance's reg_date_index will be used

"""
        if not sort_index:
            sort_index = self.reg_date_index
        sorted_user_list = self.users_list
        sorted_user_list.sort(key=lambda x: x[sort_index], reverse=reverse)
        users_list = []
        i = 0
        for user in sorted_user_list:
            users_list.append(user)
            if i >= num_of_lines:
                break
            i += 1
        return users_list

    async def sorted_users_strings(self, str_format: str, num_of_lines: int = 1,
            sort_index: Union[str, int] = None):
        """Returns a list of rows of users sorted by special index

:param str_format: is .format() format of rows in list
:param num_of_lines: is num of list lenght
:param sort_index: is name or num of index of users_list dictionary item with registration date info 

If sort_index is not set, the instance's reg_date_index will be used

"""
        if not sort_index:
            sort_index = self.reg_date_index
        sorted_user_list = self.users_list
        sorted_user_list.sort(key=lambda x: x[sort_index], reverse=True)
        strings_list = []
        i = 0
        for user in sorted_user_list:
            strings_list.append(str_format.format(**user))
            if i >= num_of_lines:
                break
            i += 1
        return strings_list

    #TODO
    async def list_of_the_best(self, num_of_lines: int = 1, *sort_indexes, 
            logger: logging.Logger = logging, reverse: bool = True):
        if not sort_indexes:
            raise 'Sort indexes were not set'
        sorted_users = sorted(self.users_list, key=lambda x: list(x[i] for i in sort_indexes), reverse=reverse)
        users_list = []
        i = 0
        for user in sorted_users:
            if i >= num_of_lines:
                break
            users_list.append(user)
            i += 1
        return users_list
        
        
        

