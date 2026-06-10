import argparse
import json
import sys

from modules.card import build_book_card
from modules.entities import extract_entities
from modules.lexdiv import compute_lexdiv
from modules.similar import find_similar_books
from modules.summarize import summarize_book
from modules.topics import extract_topics_for_book
from utils.cache import CacheError
from utils.gutenberg import GutenbergError, load_book


COMMANDS = ("lexdiv", "topics", "entities", "summarize", "similar", "card")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    selected_commands = get_selected_commands(args)

    if len(selected_commands) != 1:
        parser.error("choose exactly one command: --lexdiv, --topics, --entities, --summarize, --similar, or --card")

    command = selected_commands[0]
    book_id = getattr(args, command)

    try:
        result = run_command(command, book_id)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (GutenbergError, CacheError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print_result(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bookworm.py",
        description="Analyze Project Gutenberg books and generate book cards.",
    )
    parser.add_argument("--lexdiv", metavar="ID", help="compute lexical diversity metrics")
    parser.add_argument("--topics", metavar="ID", help="extract topic keywords by section")
    parser.add_argument("--entities", metavar="ID", help="extract characters and locations")
    parser.add_argument("--summarize", metavar="ID", help="summarize a book in a few sentences")
    parser.add_argument("--similar", metavar="ID", help="recommend five similar books")
    parser.add_argument("--card", metavar="ID", help="generate the complete book card")
    return parser


def get_selected_commands(args: argparse.Namespace) -> list[str]:
    return [command for command in COMMANDS if getattr(args, command) is not None]


def run_command(command: str, book_id: str):
    validate_book_id(book_id)

    if command == "lexdiv":
        return compute_lexdiv(load_book(book_id))

    if command == "topics":
        return extract_topics_for_book(book_id)

    if command == "entities":
        return extract_entities(load_book(book_id))

    if command == "summarize":
        return summarize_book(book_id)

    if command == "similar":
        return find_similar_books(book_id)

    if command == "card":
        return build_book_card(book_id)

    raise ValueError(f"unknown command: {command}")


def validate_book_id(book_id: str) -> None:
    if not str(book_id).strip().isdigit() or int(book_id) <= 0:
        raise ValueError("book id must be a positive integer")


def print_result(result) -> None:
    if isinstance(result, str):
        print(result)
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
