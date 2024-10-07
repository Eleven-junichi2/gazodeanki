from pathlib import Path
import json
import tomllib

import click

APIKEYS_PATH = Path(__file__).parent / "apikeys.toml"
with open(APIKEYS_PATH, "rb") as f:
    apikeys = tomllib.load(f)

DECKS_FILE_EXT = ".json"
DECKS_PATH = Path(__file__).parent / ("decks" + DECKS_FILE_EXT)

if DECKS_PATH.exists():
    with open(DECKS_PATH, "r") as f:
        decks: dict[str, dict] = json.load(f)
else:
    decks = {}


def update_decks_file(decks, msg="Database updated successfully."):
    with open(DECKS_PATH, "w") as f:
        json.dump(decks, f)
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
    """Add a new card to the specified deck.
    If the question already exists, ask the user if he/she wants to write it.
    """
    if deck not in decks:
        click.echo(f"Deck '{deck}' does not exist, creating a new deck...")
        decks[deck] = {}
    if question in decks[deck]:
        if force or click.confirm("Question already exists. Rewrite it's card?"):
            deck[question] = answer
        else:
            return
    decks[deck] = {question: answer}
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
@click.option("--show-answers", "-sa", is_flag=True, show_default=True, default=False)
def cards(deck, show_answers=True):
    for question, answer in decks[deck].items():
        if show_answers:
            click.echo("question:")
            click.echo(end=" ")
        click.echo(question)
        if show_answers:
            click.echo("answer:")
            click.echo(" " + answer)
            if len(decks[deck]) > 1:
                click.echo()


@main.command()
@click.argument("deck", required=True)
def study(deck):
    for question, answer in decks[deck].items():
        click.echo("question:")
        click.echo(" " + question)
        click.pause("press any key to show answer...")
        click.echo("answer:")
        click.echo(" " + answer)


@main.command()
@click.argument("deck", required=True)
def set_imgs_for_qs(deck):
    pass


if __name__ == "__main__":
    main()
