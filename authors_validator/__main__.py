from typing import Dict, List

import pandas
from unidecode import unidecode

RESULTS_FILE_NAME = "results.csv"


def get_authors_names_list(dataframe: object, column_to_normalize: str) -> List[str]:
    authors = dataframe[dataframe[column_to_normalize].notnull()][column_to_normalize]
    return authors.values.tolist()


def get_author_name_variations(author_name: str) -> List[str]:
    variations = [author_name]

    if not author_name.islower():
        variations.append(author_name.lower())

    if not author_name.isupper():
        variations.append(author_name.upper())

    if not author_name.istitle():
        variations.append(author_name.title())

    # variations.append(f"{author_name.split()[0]} {author_name.split()[-1]}")

    variations.extend(
        list(
            filter(
                lambda author_name: author_name not in variations,
                [unidecode(author_name) for author_name in variations],
            )
        )
    )

    return variations


def compare(author_name_variations: List[str], authors_names: List[str]) -> List[str]:
    similars = []

    for variation in author_name_variations:
        for author_name in authors_names:
            if variation == author_name:
                similars.append(author_name)

    return similars


def save_results(similarities: List[Dict], column_to_normalize: str):
    data = []

    for similarity in similarities:
        data.append({column_to_normalize: similarity.get("author_name")})
        for similar_name in similarity.get("similar_names"):
            data.append({column_to_normalize: similar_name})

    dataframe = pandas.DataFrame(data)
    dataframe.to_csv(RESULTS_FILE_NAME, encoding="utf-8", index=False)


def run(file_path: str, column_to_normalize: str):
    dataframe = pandas.read_csv(file_path)
    authors_names = get_authors_names_list(dataframe, column_to_normalize)

    similarities = []
    for author_name in authors_names:
        author_name_variations = get_author_name_variations(author_name)

        similars = compare(author_name_variations, authors_names)
        if len(similars) > 1:
            similarities.append(
                {
                    "author_name": author_name,
                    "similar_names": list(
                        filter(lambda similar: similar != author_name, similars)
                    ),
                }
            )

    save_results(similarities, column_to_normalize)


if __name__ == "__main__":
    # run(file_path="test-sample.csv", column_to_normalize="autores_unique")
    run(file_path="sample.csv", column_to_normalize="autores_unique")
