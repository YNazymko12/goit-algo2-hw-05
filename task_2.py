from colorama import Fore, Style, init
import time
from datasketch import HyperLogLog
import re
from tabulate import tabulate


# Ініціалізація colorama
init()

def load_data(file_path: str) -> list:
    """
    Завантажує IP-адреси з лог-файлу, ігноруючи некоректні рядки.
    """
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    ip_addresses = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                match = ip_pattern.search(line)
                if match:
                    ip_addresses.append(match.group())
    except (FileNotFoundError, UnicodeDecodeError, Exception) as e:
        print(Fore.RED + f"Помилка: {e}" + Style.RESET_ALL)
        raise

    if not ip_addresses:
        raise ValueError("У файлі не знайдено жодної коректної IP-адреси.")

    return ip_addresses

def exact_count_unique_ips(ip_addresses: list) -> int:
    """Підраховує точну кількість унікальних IP-адрес за допомогою множини."""
    return len(set(ip_addresses))

def hyperloglog_count_unique_ips(ip_addresses: list, p: int = 10) -> int:
    """Оцінює кількість унікальних IP-адрес за допомогою HyperLogLog."""
    hll = HyperLogLog(p)
    for ip in ip_addresses:
        hll.update(ip.encode("utf-8"))
    return int(hll.count())

def compare_methods(ip_addresses: list):
    """Порівнює продуктивність точного підрахунку та HyperLogLog."""
    # Точний підрахунок
    start_time = time.time()
    exact_count = exact_count_unique_ips(ip_addresses)
    exact_time = time.time() - start_time

    # Підрахунок HyperLogLog
    start_time = time.time()
    hll_count = hyperloglog_count_unique_ips(ip_addresses)
    hll_time = time.time() - start_time

    # Дані для таблиці
    data = [
        ["Унікальні елементи", exact_count, hll_count],
        ["Час виконання (сек)", f"{exact_time:.4f}", f"{hll_time:.4f}"],
    ]

    print(Fore.CYAN + "Результати порівняння:" + Style.RESET_ALL)
    print(tabulate(data, headers=["Метод", "Точний підрахунок", "HyperLogLog"], tablefmt="grid"))

if __name__ == "__main__":
    file_path = "lms-stage-access.log"
    try:
        ip_addresses = load_data(file_path)
        compare_methods(ip_addresses)
    except Exception as e:
        print(Fore.RED + f"Програма завершена з помилкою: {e}" + Style.RESET_ALL)
