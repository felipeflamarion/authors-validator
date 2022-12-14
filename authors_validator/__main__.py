import json
from typing import Dict, List

import pandas
from unidecode import unidecode

IGNORE_FIRST_NAMES_LIST = []
IGNORE_LAST_NAMES_LIST = []


def get_names(df: object, column: str) -> List[str]:
    authors = df[df[column].notnull()][column]
    return authors.values.tolist()


def get_name_variations(name: str) -> List[str]:
    variations = [name]

    if not name.islower():
        variations.append(name.lower())

    if not name.isupper():
        variations.append(name.upper())

    if not name.istitle():
        variations.append(name.title())

    variations.extend(
        list(
            filter(
                lambda name: name not in variations,
                [unidecode(name) for name in variations],
            )
        )
    )

    return variations


def get_first_and_last_name(name: str) -> tuple:
    splited_name = name.strip().split(" ")
    if len(splited_name) == 1:
        return name, None

    return splited_name[0], splited_name[-1]


def analyze(current_name: str, variations: List[str], names: List[str]) -> List:
    similar_names = []
    for variation in variations:
        first_name, last_name = get_first_and_last_name(variation)

        for name in names:
            if current_name == name:
                continue

            if variation == name:
                similar_names.append(variation)

            if first_name and last_name:
                if (
                    first_name not in IGNORE_FIRST_NAMES_LIST
                    and last_name not in IGNORE_LAST_NAMES_LIST
                    and name.startswith(first_name)
                    and name.endswith(last_name)
                ):
                    similar_names.append(name)

    if similar_names:
        similar_names = [current_name, *similar_names]

    return similar_names


def prepare_results(results: List[Dict], column: str) -> List[Dict]:
    return list(map(lambda result: {column: result}, results))


def save_results(results: List[Dict]):
    dataframe = pandas.DataFrame(results)
    dataframe.to_csv("results.csv", encoding="utf-8", index=False)


def run(file_path: str, column: str):
    df = pandas.read_csv(file_path)
    all_names = get_names(df, column)

    results = []
    for name in all_names:
        if name not in results:
            variations = get_name_variations(name)
            results.extend(analyze(name, variations, all_names))

    save_results(prepare_results(results, column))


if __name__ == "__main__":
    run(file_path="data.csv", column="autores_unique")
