#!/usr/bin/env python3
import argparse
from pprint import pprint

from nlp.card import build_book_card
from nlp.entities import extract_entities
from nlp.lexical_diversity import compute_lexical_diversity
from nlp.similarity import find_similar_books
from nlp.summarization import summarize_book
from nlp.topics import extract_topics
from services.gutenberg import GutenbergError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create lightweight NLP book cards from Project Gutenberg books."
    )
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--lexdiv", metavar="ID", help="compute lexical diversity")
    commands.add_argument("--topics", metavar="ID", help="extract section topic words")
    commands.add_argument("--entities", metavar="ID", help="extract characters and locations")
    commands.add_argument("--summarize", metavar="ID", help="summarize a book")
    commands.add_argument("--similar", metavar="ID", help="find five similar books")
    commands.add_argument("--card", metavar="ID", help="build a complete book card")
    parser.add_argument("--no-cache", action="store_true", help="ignore cached NLP results")
    args = parser.parse_args()

    try:
        result = _run_command(args, use_cache=not args.no_cache)
    except (GutenbergError, ValueError) as error:
        parser.exit(1, f"bookworm: error: {error}\n")

    if isinstance(result, str):
        print(result)
    else:
        pprint(result, sort_dicts=False)

    return 0


def _run_command(args: argparse.Namespace, use_cache: bool):
    if args.lexdiv:
        return compute_lexical_diversity(args.lexdiv, use_cache=use_cache)
    if args.topics:
        return extract_topics(args.topics, use_cache=use_cache)
    if args.entities:
        return extract_entities(args.entities, use_cache=use_cache)
    if args.summarize:
        return summarize_book(args.summarize, use_cache=use_cache)
    if args.similar:
        return find_similar_books(args.similar, use_cache=use_cache)
    if args.card:
        return build_book_card(args.card, use_cache=use_cache)
    raise ValueError("no command provided")


if __name__ == "__main__":
    raise SystemExit(main())
