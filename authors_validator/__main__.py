import json
from typing import Dict, List

import pandas
from unidecode import unidecode


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


def analyze(current_name: str, variations: List[str], names: List[str]) -> Dict:
    similar_names = []

    for variation in variations:
        first_name, last_name = get_first_and_last_name(variation)

        for name in names:
            if current_name == name:
                continue

            if variation == name:
                similar_names.append(variation)

            if first_name and last_name:
                if name.startswith(first_name) and name.endswith(last_name):
                    similar_names.append(name)

    return {"name": current_name, "similar_names": list(set(similar_names))}


def prepare_results(results: List[Dict], column: str) -> List[Dict]:
    prepared_results = []

    for result in results:
        if len(result["similar_names"]) > 1:
            prepared_results.extend(
                [{column: similar_name} for similar_name in result["similar_names"]]
            )

    return prepared_results


def save_results(results: List[Dict]):
    dataframe = pandas.DataFrame(results)
    dataframe.to_csv("results.csv", encoding="utf-8", index=False)


def run(file_path: str, column: str):
    df = pandas.read_csv(file_path)
    all_names = get_names(df, column)

    results = []
    for name in all_names:
        variations = get_name_variations(name)
        results.append(analyze(name, variations, all_names))

    save_results(prepare_results(results, column))


if __name__ == "__main__":
    run(file_path="test-data.csv", column="autores_unique")
