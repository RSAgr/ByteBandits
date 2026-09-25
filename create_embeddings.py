"""Backward-compatible entry point for loading embeddings into PostgreSQL.

Use ``python data/load_embeddings_to_postgres.py --help`` for all options.
"""

from data.load_embeddings_to_postgres import main


if __name__ == "__main__":
    main()
