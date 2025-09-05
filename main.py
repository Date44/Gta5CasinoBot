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
        text += f'{num}: {percent}%\n'
    await message.answer(text)

@dp.message()
async def number_handler(message: Message):
    if not (message.text and message.text.strip().isdigit()):
        return
    num = int(message.text.strip())
    user_id = message.from_user.id
    data = load_data(user_id)
    data['lists'][data['current']].append(num)
    save_data(user_id, data)
    next_stats = get_next_stats(data, num)
    if not next_stats:
        text = 'There are no numbers after this one yet.'
    else:
        text = 'Top 3 numbers that come after this number:\n'
        for n, percent in next_stats:
            text += f'{n}: {percent}%\n'
    await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
