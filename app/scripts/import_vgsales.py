"""
Dataset import script.

Reads the vgsales.csv dataset and populates the database tables:
- publishers
- platforms
- genres
- games

The script performs simple deduplication so that each publisher,
platform, and genre is only inserted once.

Usage:
    python -m app.scripts.import_vgsales
"""

import csv
from pathlib import Path
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.publisher import Publisher
from app.models.platform import Platform
from app.models.genre import Genre
from app.models.game import Game

import re


DATA_FILE = Path("data/vgsales.csv")

def canonical_name(value: str) -> str:
    """Normalise names so 'S.r.l' and 'Srl' variations collapse."""
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)            # collapse whitespace
    value = value.replace("’", "'")               # normalise apostrophes
    return value

def slugify(value: str) -> str:
    """Basic slugification (letters/numbers/hyphens only)."""
    value = canonical_name(value).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9\s-]", "", value)     # remove punctuation
    value = re.sub(r"\s+", "-", value).strip("-")  # spaces -> hyphens
    value = re.sub(r"-{2,}", "-", value)           # collapse hyphens
    return value or "unknown"

def unique_slug(base_slug: str, used_slugs: set[str]) -> str:
    """Ensure slug uniqueness by appending -2, -3, ... if needed."""
    slug = base_slug
    i = 2
    while slug in used_slugs:
        slug = f"{base_slug}-{i}"
        i += 1
    used_slugs.add(slug)
    return slug


def parse_int(value: str | None) -> int | None:
    # Parse an integer field that may be blank or 'N/A'.
    if value is None:
        return None
    value = value.strip()
    if value == "" or value.upper() == "N/A":
        return None
    return int(value)


def parse_float(value: str | None) -> float:
    # Parse a float field that may be blank; defaults to 0.0.
    if value is None:
        return 0.0
    value = value.strip()
    if value == "" or value.upper() == "N/A":
        return 0.0
    return float(value)


def import_data():
    db: Session = SessionLocal()

    publishers = {}
    platforms = {}
    genres = {}

    publisher_slugs: set[str] = set()
    platform_slugs: set[str] = set()
    genre_slugs: set[str] = set()

    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:

            # ---------- Publisher ----------
            pub_name = canonical_name(row.get("Publisher") or "Unknown")


            if pub_name not in publishers:
                base = slugify(pub_name)
                publisher = Publisher(name=pub_name, slug=unique_slug(base, publisher_slugs))
                db.add(publisher)
                db.flush()
                publishers[pub_name] = publisher

            # ---------- Platform ----------
            plat_name = canonical_name(row.get("Platform") or "Unknown")

            if plat_name not in platforms:
                base = slugify(plat_name)
                platform = Platform(name=plat_name, slug=unique_slug(base, platform_slugs))
                db.add(platform)
                db.flush()
                platforms[plat_name] = platform

            # ---------- Genre ----------
            genre_name = canonical_name(row.get("Genre") or "Unknown")

            if genre_name not in genres:
                base = slugify(genre_name)
                genre = Genre(name=genre_name, slug=unique_slug(base, genre_slugs))
                db.add(genre)
                db.flush()
                genres[genre_name] = genre

            # ---------- Game ----------
            game = Game(
                name=row["Name"].strip(),
                year=parse_int(row.get("Year")),

                publisher_id=publishers[pub_name].id,
                platform_id=platforms[plat_name].id,
                genre_id=genres[genre_name].id,

                na_sales=parse_float(row.get("NA_Sales")),
                eu_sales=parse_float(row.get("EU_Sales")),
                jp_sales=parse_float(row.get("JP_Sales")),
                other_sales=parse_float(row.get("Other_Sales")),
                global_sales=parse_float(row.get("Global_Sales")),
            )

            db.add(game)

    db.commit()

    db.close()

    print("Dataset import complete.")


if __name__ == "__main__":
    import_data()