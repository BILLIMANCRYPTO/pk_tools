import os
import requests
from web3 import Web3
from eth_account import Account
from settings import URL, API_KEY, CONTRACT_ADDRESS
from datetime import datetime, timedelta

# Функция для проверки взаимодействия с контрактом через Etherscan API
def check_contract_interaction(address, contract_address, api_key):
    url = f"https://api.{URL}/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        transactions = response.json()['result']
        for tx in transactions:
            if tx['to'].lower() == contract_address.lower():
                return True
    return False

# Функция для получения времени последней транзакции
def get_last_transaction_time(address, api_key):
    url = f"https://api.{URL}/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        transactions = response.json()['result']
        if transactions:
            return datetime.utcfromtimestamp(int(transactions[0]['timeStamp']))
    return None

# Функция для проверки, была ли транзакция в текущем месяце
def is_transaction_this_month(last_transaction_time):
    if last_transaction_time:
        now = datetime.utcnow()
        return last_transaction_time.year == now.year and last_transaction_time.month == now.month
    return False

# Чтение приватных ключей из файла
with open("keys.txt", "r") as f:
    private_keys = f.read().strip().splitlines()

# Параметры для проверки взаимодействия с контрактом
contract_address = CONTRACT_ADDRESS
etherscan_api_key = API_KEY  # Замените на ваш API ключ от Etherscan

# Параметры для проверки транзакций в текущем месяце
scrollscan_api_key = API_KEY  # Замените на ваш API ключ от Scrollscan

# Запрос выбора режима работы у пользователя
print("Выберите режим работы:")
print("1. Проверка взаимодействия с контрактом")
print("2. Проверка транзакций в текущем месяце")
choice = input("Введите номер режима работы: ")

# Проверка выбора и выполнение соответствующего действия
if choice == "1":
    mode = "contract"
elif choice == "2":
    mode = "transaction"
else:
    print("Некорректный выбор.")
    exit()

# Проверка взаимодействия с контрактом и транзакций в текущем месяце для каждого приватного ключа
for private_key in private_keys:
    address = Account.from_key(private_key).address
    if mode == "contract" and not check_contract_interaction(address, contract_address, etherscan_api_key):
        with open("notused.txt", "a") as f:
            f.write(private_key + '\n')
    elif mode == "transaction":
        last_transaction_time = get_last_transaction_time(address, scrollscan_api_key)
        if not is_transaction_this_month(last_transaction_time):
            with open("notused.txt", "a") as f:
                f.write(private_key + '\n')
