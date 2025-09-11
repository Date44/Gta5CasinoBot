import json
import os
from collections import Counter
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

CONFIG_FILE = 'config.json'
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)
API_TOKEN = config['API_TOKEN']

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

list1 = [0, 28, 9, 26, 30, 11, 7, 20, 32, 17, 5, 22, 34, 15, 3, 24, 36, 13, 1, 37, 27, 10, 25, 29, 12, 8, 19, 31, 18, 6, 21, 33, 16, 4, 23, 35, 14, 2]

def get_data_file(user_id):
    return f'numbers_data_{user_id}.json'

def load_data(user_id):
    data_file = get_data_file(user_id)
    if not os.path.exists(data_file):
        return {'lists': [[]], 'current': 0}
    with open(data_file, 'r') as f:
        return json.load(f)

def save_data(user_id, data):
    data_file = get_data_file(user_id)
    with open(data_file, 'w') as f:
        json.dump(data, f)

def get_all_numbers(data):
    numbers = []
    for lst in data['lists']:
        numbers.extend(lst)
    return numbers

def get_stats(numbers):
    if not numbers:
        return []
    counter = Counter(numbers)
    total = sum(counter.values())
    most_common = counter.most_common(3)
    result = []
    for num, count in most_common:
        percent = round(count / total * 100, 2)
        result.append((num, percent))
    return result

def get_next_stats(data, current_num):
    next_numbers = []
    for lst in data['lists']:
        for i in range(len(lst) - 1):
            if lst[i] == current_num:
                next_numbers.append(lst[i + 1])
    if not next_numbers:
        return []
    counter = Counter(next_numbers)
    total = sum(counter.values())
    most_common = counter.most_common(3)
    result = []
    for num, count in most_common:
        percent = round(count / total * 100, 2)
        result.append((num, percent))
    return result

@dp.message(Command('start'))
async def start_cmd(message: Message):
    await message.answer('Hi! Send me a number, and I’ll save it.\n/newlist — start a new list.\n/stats — view the top 3 numbers.')

@dp.message(Command('newlist'))
async def newday_cmd(message: Message):
    user_id = message.from_user.id
    data = load_data(user_id)
    data['lists'].append([])
    data['current'] = len(data['lists']) - 1
    save_data(user_id, data)
    await message.answer('A new list has been created.')

@dp.message(Command('stats'))
async def stats_cmd(message: Message):
    user_id = message.from_user.id
    data = load_data(user_id)
    numbers = get_all_numbers(data)
    stats = get_stats(numbers)
    if not stats:
        await message.answer('No data yet.')
        return
    text = 'Top 3 numbers of all time:\n'
    for num, percent in stats:
        text += f'{num if num != 37 else "00"}: {percent}%\n'
    await message.answer(text)

@dp.message()
async def number_handler(message: Message):
    num = message.text
    if num == "00":
        num = "37"
    if not (num and num.strip().isdigit()):
        return
    num = int(num.strip())
    user_id = message.from_user.id
    data = load_data(user_id)
    data['lists'][data['current']].append(num)
    save_data(user_id, data)
    next_numbers = []
    for lst in data['lists']:
        for i in range(len(lst) - 1):
            if lst[i] == num:
                next_numbers.append(lst[i + 1])
    if next_numbers:
        counter = Counter(next_numbers)
        top3 = counter.most_common(3)
        text = 'TOP 3 numbers that go after this number:\n'
        for n, count in top3:
            if n in list1:
                idx = list1.index(n)
                before = list1[idx - 1] if idx > 0 else list1[-1]
                after = list1[idx + 1] if idx < len(list1) - 1 else list1[0]
                text += f'{before if before != 37 else "00"} '
                text += f'{n if n != 37 else "00"} '
                text += f'{after if after != 37 else "00"} ({count} раз)\n'
            else:
                text += f'{n if n != 37 else "00"} (not in the main list) ({count} once)\n'
    else:
        text = 'There is no data on the following numbers after that.'
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
