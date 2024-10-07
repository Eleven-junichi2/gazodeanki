from pathlib import Path
import json
import tomllib

from term_image.image import from_file
import click
import requests

IMGS_DIRPATH = Path(__file__).parent / "images"

APIKEYS_PATH = Path(__file__).parent / "apikeys.toml"
with open(APIKEYS_PATH, "rb") as f:
    apikeys = tomllib.load(f)

DECKS_FILE_EXT = ".json"
DECKS_PATH = Path(__file__).parent / ("decks" + DECKS_FILE_EXT)

if DECKS_PATH.exists():
    with open(DECKS_PATH, "r", encoding="utf-8") as f:
        decks: dict[str, dict] = json.load(f)
else:
    decks = {}


def update_decks_file(decks, msg="Database updated successfully."):
    with open(DECKS_PATH, "w", encoding="utf-8") as f:
        json.dump(decks, f, ensure_ascii=False)
    click.echo(msg)


@click.group()
def main():
    pass


@main.command()
@click.argument("deck", required=True)
@click.option("--question", "-q", required=True)
@click.option("--answer", "-a", required=True)
@click.option("--force", "-F", is_flag=True, show_default=True, default=False)
def add(deck: str, question: str, answer: str, force: bool):
    """Add a new card/Update the card.
    If the card for question already exists, ask the user if he/she wants to write it.
    """
    if deck not in decks:
        click.echo(f"Deck '{deck}' does not exist, creating a new deck...")
        decks[deck] = {}
    if question in decks[deck]:
        if force or click.confirm("Question already exists. Rewrite it's card?"):
            decks[deck][question] = answer
        else:
            return
    decks[deck][question] = answer
    click.echo(f"Added card to deck '{deck}':\nquestion: {question}\nanswer: {answer}")
    update_decks_file(decks)


@main.command()
@click.argument("deck", required=True)
@click.option("--question", "-q")
@click.option("--force", "-F", is_flag=True, show_default=True, default=False)
def remove(deck: str, question: str, force: bool):
    """Remove a card for the specified question from the specified deck."""
    if question:
        if question in decks[deck]:
            if force or click.confirm(
                f"Are you sure you want to remove card for this question: '{question}'?"
            ):
                decks[deck].pop(question)
                click.echo(
                    f"Removed card for question: '{question}' from deck '{deck}'."
                )
                update_decks_file(decks)
        else:
            click.echo(f"Card for question: '{question}' not found in deck '{deck}'.")
    else:
        if deck in decks:
            if force or click.confirm(
                f"Are you sure you want to remove deck '{deck}'?"
            ):
                decks.pop(deck)
                update_decks_file(decks)
        else:
            click.echo(f"Deck '{deck}' does not exist.")


@main.command()
@click.argument("deck", required=True)
@click.option("--show-answers", "-sa", is_flag=True, show_default=True, default=True)
@click.option("--show-img-for-question", "-img-4-question", is_flag=True, show_default=True, default=True)
def cards(deck, show_answers, show_img_for_question):
    for question, answer in decks[deck].items():
        if show_answers:
            click.echo("question:")
            click.echo(" ", nl=False)
        click.echo(question)
        img_filepath = IMGS_DIRPATH.joinpath(question+".jpg")
        if img_filepath.exists():
            image = from_file(img_filepath)
            image.draw(h_align="<")
        if show_answers:
            click.echo("answer:")
            click.echo(" " + answer)
            if len(decks[deck]) > 1:
                click.echo()

@main.command()
def decklist():
    for deck in decks.keys():
        click.echo(deck)


@main.command()
@click.argument("deck", required=True)
def study(deck):
    for question, answer in decks[deck].items():
        click.echo("question:")
        click.echo(" " + question)
        img_filepath = IMGS_DIRPATH.joinpath(question+".jpg")
        if img_filepath.exists():
            image = from_file(img_filepath)
            image.draw(h_align="<")
        click.pause("press any key to show answer...")
        click.echo("answer:")
        click.echo(" " + answer)
        if len(decks[deck]) > 1:
            click.echo()
    click.pause("press any key to exit")


@main.command()
@click.argument("deck", required=True)
def set_imgs_for_qs(deck):
    if deck not in decks:
        click.echo(f"Deck '{deck}' does not exist")
        return
    for question in decks[deck].keys():
        response = requests.get(
            "https://pixabay.com/api/",
            params={"key": apikeys["pixabay"], "q": question},
        )
        response.raise_for_status()
        search_results = response.json()
        img_url: str = search_results["hits"][0]["webformatURL"]
        img_data = requests.get(img_url).content
        if not IMGS_DIRPATH.exists() or not IMGS_DIRPATH.is_dir():
            IMGS_DIRPATH.mkdir()
        with open(
            IMGS_DIRPATH / (question + ".jpg"),
            mode="wb",
        ) as f:
            f.write(img_data)
            print(f"set image for question: {question}")


if __name__ == "__main__":
    main()
