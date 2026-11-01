# Link do repozytorium: https://github.com/Chl3pka/zadanie_3_python/tree/main

import sys
import argparse
import csv
import json
import pathlib
import os
import random
from pathlib import Path

# Nazwy bez polskich znaków w kodzie i terminalu, żeby uniknąć problemów i ułatwić wczytywanie
# Słownik tłumaczy argument wywołania na nazwę katalogu
MONTHS = {
    "styczen": "styczeń",
    "luty": "luty",
    "marzec": "marzec",
    "kwiecien": "kwiecień",
    "maj": "maj",
    "czerwiec": "czerwiec",
    "lipiec": "lipiec",
    "sierpien": "sierpień",
    "wrzesien": "wrzesień",
    "pazdziernik": "październik",
    "listopad": "listopad",
    "grudzien": "grudzień",
}

DAYS = {
    "pn": "poniedziałek",
    "wt": "wtorek",
    "sr": "środa",
    "cz": "czwartek",
    "pt": "piątek",
    "sb": "sobota",
    "nd": "niedziela",
}

DAY_ORDER = list(DAYS)

PERIODS = {
    "r": "rano",
    "w": "wieczorem",
}

# Funkcja parsująca argumenty wywołania programu
def parse_args():
    parser = argparse.ArgumentParser(
        description = "Tworzenie i odczyt danych typu CSV/JSON",
        formatter_class = argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-m", "--miesiace",
        nargs = "+",
        choices = MONTHS.keys(),
        metavar = "MIESIACE",
        required = True,
        help = "Wymagane. Miesiące do przeszukania lub zapisania (bez polskich znaków)",
    )

    parser.add_argument(
        "-d", "--dni",
        nargs = "+",
        metavar = "ZAKRESY",
        required = True,
        help = "Wymagane. Zakres dla każdego miesiąca, np. pn-wt, pt\nSkróty dni: pn, wt, sr, cz, pt, sb, nd",
    )

    parser.add_argument(
        "-p", "--pory",
        nargs = "*",
        choices = PERIODS.keys(),
        default = [],
        help = "Pory dla kolejnych dni: r albo w (opcjonalne, domyślnie r)",
    )

    mode = parser.add_mutually_exclusive_group(required = True)
    mode.add_argument(
        "-t", "--tworz",
        action = "store_true",
        help = "Utwórz plik",
    )
    mode.add_argument(
        "-o", "--odczyt",
        action = "store_true",
        help = "Odczytaj plik\nWybierz dokładnie jedną opcję trybu",
    )

    format = parser.add_mutually_exclusive_group(required = True)
    format.add_argument(
        "-c", "--csv",
        action = "store_true",
        help = "Format CSV",
    )
    format.add_argument(
        "-j", "--json",
        action = "store_true",
        help = "Format JSON\nWybierz dokładnie jedną opcję formatu",
    )

    args = parser.parse_args()

    if len(args.miesiace) != len(args.dni):
        parser.error("Podaj dokładnie jeden zakres dni na każdy miesiąc.")

    return args

#Funkcja przetwarza zakresy dni na listy
#Zakresy się zawijają, a więc np. sb-pn to sobota, niedziela, poniedziałek
#Zakres typu "pt-pt" traktujemy jak pojedyńczy dzień
def expand_day_ranges(day_range):
    if "-" not in day_range:  #Zakres to pojedyńczy dzień
        if day_range not in DAYS:
            raise ValueError(f"podano niepoprawny dzień: {day_range}")
        return [day_range]

    start, end = day_range.split("-", maxsplit = 1)

    if start not in DAYS or end not in DAYS:
        raise ValueError(f"podano niepoprawny zakres dni: {day_range}")

    i = DAY_ORDER.index(start)
    limit = DAY_ORDER.index(end)
    result = []

    while True:
        result.append(DAY_ORDER[i])

        if i == limit:
            break

        i = (i + 1) % len(DAY_ORDER)

    return result

#Funkcja odpowiednio generuje ścieżki do poszczególnych danych
def generate_paths(args):
    months = args.miesiace
    days = []
    periods = args.pory

    n = len(months)
    total_days = 0

    for i in range(n):
        days.append(expand_day_ranges(args.dni[i]))
        total_days += len(days[-1])

    if len(periods) > total_days:
        raise ValueError("podano więcej pór niż dni")

    paths = []
    period_index = 0
    extension = ".csv" if args.csv else ".json"

    for i in range(n):
        for day in days[i]:
            period = "r"
            if (period_index < len(periods)):
                period = periods[period_index]
                period_index += 1

            path = os.path.join("dane", MONTHS[months[i]], DAYS[day], PERIODS[period], f"Dane{extension}")
            paths.append(Path(path))

    return paths

#Funkcja zapisująca dane do pliku z odpowiednią ścieżką i w podanym formacie
def write_data(path, is_csv):
    path.parent.mkdir(parents = True, exist_ok = True)  # Tworzymy ścieżkę do katalogu docelowego, jeśli nie istnieje

    record = {
        "Model": random.choice(["A", "B", "C"]),
        "Wynik": random.randint(0, 1000),
        "Czas": f"{random.randint(0, 1000)}s",
    }

    with path.open("w", newline = "", encoding = "utf-8") as file:
        if is_csv:
            # Wbudowany writer z biblioteki csv działa w innym formacie niż wymagany, więc robimy bezpośredni zapis tekstowy
            file.write("Model; Wynik; Czas;\n")
            file.write(
                f"{record['Model']} ; {record['Wynik']} ; {record['Czas']};\n"
            )
        else:
            json.dump(record, file, ensure_ascii = False, indent = 4)

#Funkcja wczytująca dane z pliku z odpowiednią ścieżką i w podanym formacie
def read_data(path, is_csv):
    with path.open("r", encoding = "utf-8") as file:
        if is_csv:
            reader = csv.DictReader(
                file,
                delimiter = ";",
                skipinitialspace = True
            )

            for record in reader:
                if record["Model"].strip() == "A":
                   return int(record["Czas"].strip().removesuffix("s"))
        else:
            record = json.load(file)
            if record["Model"] == "A":
                return int(record["Czas"].removesuffix("s"))

    return 0

def main():
    args = parse_args()

    try:
        paths = generate_paths(args)
    except ValueError as error:
        raise SystemExit(f"Błąd argumentów: {error}")

    total_time = 0

    for path in paths:
        if args.tworz:
            write_data(path, args.csv)
            print(f"Utworzono: {path}")

        else:
            if not path.exists():
                print(f"Brak pliku: {path}")
                continue

            try:
                total_time += read_data(path, args.csv)
            except (ValueError, KeyError, json.JSONDecodeError) as error:
                print(f"Błąd odczytu {path}: {error}")
            except (OSError, csv.Error) as error:
                print(f"Nie można odczytać {path}: {error}")

    if args.odczyt:
        print(f"Suma czasu dla modelu A: {total_time}s")


if __name__ == "__main__":
    main()