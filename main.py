import requests
from collections import defaultdict
import json

TRANSMITTERS_URL = "https://sonik.space/api/transmitters"
OBSERVATIONS_URL = "https://sonik.space/api/observations"
PAGE_SIZE = 100


def fetch_transmitters(page=1):
    """Получение страниц с передатчиками из API."""
    response = requests.get(f"{TRANSMITTERS_URL}?page={page}&size={PAGE_SIZE}")
    response.raise_for_status()
    return response.json()


def get_all_transmitters():
    """Получение всех передатчиков с пагинацией."""
    transmitters = []
    page = 1

    while True:
        data = fetch_transmitters(page)
        transmitters.extend(data)

        if len(data) < PAGE_SIZE:
            break
        page += 1

    return transmitters


def calculate_success_percentage(stat):
    total = stat.get('total_count', 0)
    good = stat.get('good_count', 0)
    if total == 0:
        return 0
    return (good / total) * 100


def main():
    transmitters = get_all_transmitters()

    satellite_transmitters = defaultdict(list)

    for transmitter in transmitters:
        satellite_name = transmitter['satellite_name']
        satellite_transmitters[satellite_name].append(transmitter)

    # Поиск спутника с максимальным количеством передатчиков
    max_satellite = max(satellite_transmitters, key=lambda k: len(satellite_transmitters[k]))
    max_transmitters = satellite_transmitters[max_satellite]

    # Поиск передатчика с наибольшим процентом успешных наблюдений
    best_transmitter = max(max_transmitters, 
                           key=lambda t: calculate_success_percentage(t['stat']))

    report = {
        "satellite": {
            "name": max_satellite,
            "transmitter_count": len(max_transmitters),
            "transmitter": {
                "uuid": best_transmitter['uuid'],
                "description": best_transmitter['description'],
                "success_rate": calculate_success_percentage(best_transmitter['stat']),
                "stat": best_transmitter['stat'],
            }
        }
    }

    # Вывод информации в стандартный поток
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
