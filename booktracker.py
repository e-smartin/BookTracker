#!/usr/bin/env python3
"""
BookTracker: keep track of your reading from the terminal.

    python3 booktracker.py

Your books are saved in library.json, next to this script.
"""

import json
import os
import shutil
import sys
import textwrap
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

DATA_FILE = Path(os.environ.get("BOOKTRACKER_FILE") or Path(__file__).with_name("library.json")).expanduser()
WIDTH = max(64, min(shutil.get_terminal_size((80, 24)).columns, 100)) - 2  # length of a full line


# ── Colours ──────────────────────────────────────────────────────────────────

if os.name == "nt":
    os.system("")  # switches on colour support in the Windows console

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _style(code):
    return lambda text: f"\033[{code}m{text}\033[0m" if USE_COLOR else str(text)


bold, dim, accent, quote = _style("1"), _style("2"), _style("1;36"), _style("2;3")
red, green, yellow, blue, magenta, cyan = map(_style, ["31", "32", "33", "34", "35", "36"])


# ── Saving and loading ───────────────────────────────────────────────────────

def load_books():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        sys.exit(f"Could not read {DATA_FILE}: {error}")


def save_books(books):
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(books, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(DATA_FILE)  # swap in one go, so a crash never leaves a half-written file


# ── Asking questions ─────────────────────────────────────────────────────────

def ask(label="", hint=""):
    """Show a prompt like `  Title (hint) › ` and return the trimmed answer."""
    prompt = "  "
    if label:
        prompt += bold(label) + " "
    if hint:
        prompt += dim(f"({hint})") + " "
    return input(prompt + cyan("› ")).strip()


def ask_int(label, low, high=None, hint="", optional=False, extra=()):
    """Ask until the answer is a whole number from low to high (or one of `extra`).
    If optional, an empty answer returns None."""
    while True:
        answer = ask(label, hint)
        if optional and not answer:
            return None
        try:
            number = int(answer)
            if number in extra or (number >= low and (high is None or number <= high)):
                return number
        except ValueError:
            pass
        allowed = f"from {low} to {high}" if high is not None else f"of {low} or more"
        warn(f"Please type a whole number {allowed}.")


def ask_date(label):
    """Ask for a date. An empty answer means today."""
    while True:
        answer = ask(label, "YYYY-MM-DD, Enter = today")
        if not answer:
            return date.today()
        day = parse_date(answer)
        if day is None:
            warn("Please use the YYYY-MM-DD format, e.g. 2026-09-14.")
        elif day > date.today():
            warn("That date is in the future.")
        else:
            return day


def parse_date(text):
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            pass
    return None


# ── Printing ─────────────────────────────────────────────────────────────────

def ok(message):
    print(f"  {green('✔')} {message}")


def warn(message):
    print(f"  {red('✘')} {message}")


def note(message):
    print(f"  {dim(message)}")


def stat(value, label):
    return f"{bold(value)} {dim(label)}"


def rule(title=""):
    """A full-width line, optionally with a section title in it."""
    if title:
        print(f"\n  {dim('──')} {bold(title.upper())} {dim('─' * (WIDTH - len(title) - 6))}\n")
    else:
        print(f"  {dim('─' * (WIDTH - 2))}")


def bar(value, maximum, width, paint=green):
    filled = value * width // maximum if maximum else 0
    if value > 0 and filled == 0:
        filled = 1  # a sliver, so any reading at all shows up
    return paint("█" * filled) + dim("░" * (width - filled))


def percent(value, maximum):
    return f"{value * 100 // maximum:>3}%"


def stars(rating):
    if rating is None:
        return dim("not rated".ljust(16))
    return yellow("★" * rating) + dim("☆" * (10 - rating)) + f" {rating:>2}/10"


def fit(text, width):
    """Pad text to exactly `width` characters, shortening it with … if it's too long."""
    return text.ljust(width) if len(text) <= width else text[: width - 1] + "…"


def title_width(books, room):
    """Titles get as much space as the longest one needs, within the room available."""
    return max(12, min(room, max(len(book["title"]) for book in books)))


def plural(count, word):
    return f"{count:,} {word}" + ("" if count == 1 else "s")


def long_date(iso):  # "2026-09-05" -> "5 Sep 2026"
    day = date.fromisoformat(iso)
    return f"{day.day} {day:%b %Y}"


def short_date(iso):  # "2026-09-05" -> " 5 Sep"
    day = date.fromisoformat(iso)
    return f"{day.day:>2} {day:%b}"


def month_name(month):  # "2026-09" -> "Sep 2026"
    return f"{date.fromisoformat(month + '-01'):%b %Y}"


# ── Reading stats ────────────────────────────────────────────────────────────

def pages_by_month(books):
    """Pages read per month ("YYYY-MM"), worked out from each book's progress log."""
    pages = defaultdict(int)
    for book in books:
        previous = 0
        for entry in book.get("log", []):
            pages[entry["date"][:7]] += entry["page"] - previous
            previous = entry["page"]
    return pages


def months_between(first, last):
    """Every month from first to last, both included, as "YYYY-MM"."""
    year, month = map(int, first.split("-"))
    while f"{year:04d}-{month:02d}" <= last:
        yield f"{year:04d}-{month:02d}"
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def days_taken(book):
    """Days from start to finish, counting both. None when the start date is unknown."""
    if not (book.get("started") and book.get("finished")):
        return None
    return (date.fromisoformat(book["finished"]) - date.fromisoformat(book["started"])).days + 1


def summary(books):
    if not books:
        return dim("Your library is empty. Add your first book with 1.")
    reading = sum(1 for book in books if not book.get("finished"))
    this_month = max(pages_by_month(books).get(f"{date.today():%Y-%m}", 0), 0)
    return dim(" · ").join([
        stat(reading, "reading"),
        stat(len(books) - reading, "finished"),
        stat(f"{this_month:,}", f"pages in {date.today():%B}"),
    ])


# ── Screens ──────────────────────────────────────────────────────────────────

SHELF = [(5, red), (6, yellow), (4, green), (6, cyan), (3, magenta), (5, blue), (6, red)]


def banner():
    """The app name next to a tiny bookshelf (book heights are in half-lines, 1 to 6)."""
    today = date.today()
    beside = [bold("B O O K T R A C K E R"), dim("every page counts"),
              dim(f"{today:%A} {today.day} {today:%B %Y}")]
    print()
    for row, text in enumerate(beside):
        level = 5 - 2 * row  # the half-line at the bottom of this row
        shelf = "".join(paint(("█" if height > level else "▄" if height == level else " ") * 2)
                        for height, paint in SHELF)
        print(f"    {shelf}    {text}")
    print("   " + dim("▀" * (2 * len(SHELF) + 2)))


def show_menu(books):
    print(f"\n  {summary(books)}\n")
    for key, label in [("1", "Add a new book"), ("2", "Update progress"),
                       ("3", "Check library"), ("q", "Quit")]:
        print(f"   {accent(key)}  {label}")
    print()


def add_book(books):
    rule("New book")
    title = ask("Title", "Enter = back")
    if not title:
        return
    total = ask_int("Total pages", 1)
    current = ask_int("Current page", 0, total, "Enter = 0, -1 = finished", optional=True, extra=(-1,))
    current = total if current == -1 else current or 0
    finished = current == total
    day = ask_date("Finished on" if finished else "Started on").isoformat()

    book = {
        "title": title,
        "started": None if finished else day,  # unknown for books added already finished
        "finished": day if finished else None,
        "total_pages": total,
        "current_page": current,
        "rating": None,
        "comment": "",
        "log": [{"date": day, "page": current}],
    }
    books.append(book)
    save_books(books)
    print()
    if finished:
        ok(f"Added {bold(title)} · finished {long_date(day)}")
        review(books, book)
    else:
        ok(f"Added {bold(title)} · page {current} of {total} · started {long_date(day)}")


def update_progress(books):
    rule("Update progress")
    reading = sorted((b for b in books if not b.get("finished")), key=lambda b: b["started"])
    if not reading:
        note("Nothing in progress. Add a book first (option 1).")
        return

    book = reading[0]  # with a single book in progress there's nothing to choose
    if len(reading) > 1:
        title_w = title_width(reading, min(30, WIDTH - 41))
        for number, item in enumerate(reading, 1):
            current, total = item["current_page"], item["total_pages"]
            print(f"  {accent(f'{number:>3}')}  {fit(item['title'], title_w)}  {bar(current, total, 12)}  "
                  f"{percent(current, total)}  {dim(f'p. {current}/{total}')}")
        print()
        choice = ask_int("Which book", 1, len(reading), "Enter = back", optional=True)
        if choice is None:
            return
        book = reading[choice - 1]
        print()

    old, total = book["current_page"], book["total_pages"]
    print(f"  {bold(book['title'])}  {dim(f'on page {old} of {total}')}")
    page = ask_int("New page", 0, total, "-1 = finished", optional=True, extra=(-1,))
    if page is None:
        return
    if page == -1:
        page = total
    if page == old:
        note("That's the page you were already on, nothing to update.")
        return

    today = date.today().isoformat()
    log = book.setdefault("log", [])
    if log and log[-1]["date"] == today:
        log[-1]["page"] = page  # several updates on the same day count as one
    else:
        log.append({"date": today, "page": page})
    book["current_page"] = page
    print()

    if page < total:
        save_books(books)
        change = f"{page - old:+,} pages"
        ok(f"{bar(page, total, 16)}  {percent(page, total).strip()} · page {page} of {total}  "
           f"{dim(f'({change})')}")
        return

    book["finished"] = today
    save_books(books)
    ok(f"{bold('Finished!')} {book['title']} · {total:,} pages in {plural(days_taken(book), 'day')}")
    review(books, book)


def review(books, book):
    """Ask for a 0-10 rating and a comment once a book is finished."""
    print()
    note("How was it? (Enter to skip)")
    book["rating"] = ask_int("Rating", 0, 10, "0-10", optional=True)
    book["comment"] = ask("Comment")
    save_books(books)
    if book["rating"] is not None:
        ok(f"Review saved  {stars(book['rating'])}")
    elif book["comment"]:
        ok("Comment saved")


def show_library(books):
    if not books:
        print()
        note("Nothing here yet. Add your first book with 1.")
        return
    reading = sorted((b for b in books if not b.get("finished")), key=lambda b: b["started"])
    finished = sorted((b for b in books if b.get("finished")), key=lambda b: b["finished"])

    # Books in progress, each with a progress bar.
    if reading:
        rule("Reading now")
        pages = [f"{b['current_page']}/{b['total_pages']}" for b in reading]
        pages_w = max(map(len, pages))
        title_w = title_width(reading, WIDTH - pages_w - 48)
        for book, page_text in zip(reading, pages):
            current, total = book["current_page"], book["total_pages"]
            print(f"   {fit(book['title'], title_w)}  {bar(current, total, 16)}  "
                  f"{percent(current, total)}  {page_text:>{pages_w}}  "
                  f"{dim('since ' + long_date(book['started']))}")

    # One bar per month for the pages read, with the books finished that month underneath.
    rule("Month by month")
    logged = pages_by_month(books)
    finished_in = defaultdict(list)
    for book in finished:
        finished_in[book["finished"][:7]].append(book)
    this_month = f"{date.today():%Y-%m}"
    months = list(months_between(min([*logged, *finished_in, this_month]), this_month))
    read = {month: max(logged.get(month, 0), 0) for month in months}
    best = max(read.values())
    pages_w = len(f"{best:,}")
    title_w = title_width(finished, WIDTH - 51) if finished else 0
    mark_best = sum(1 for pages in read.values() if pages) > 1

    quiet = []  # months in a row with nothing logged, shown as a single line
    for month in months:
        if not read[month] and not finished_in[month] and month != this_month:
            quiet.append(month)
            continue
        if quiet:
            show_quiet(quiet)
            quiet = []
        line = f"   {month_name(month)}  {bar(read[month], best, 24, cyan)}  {read[month]:>{pages_w},} pages"
        if mark_best and read[month] == best:
            line += "  " + yellow("← best month")
        print(line)
        for book in finished_in[month]:
            row = (f"{'':13}{green('✔')} {short_date(book['finished'])}  "
                   f"{fit(book['title'], title_w)}  {stars(book.get('rating'))}")
            days = days_taken(book)
            if days:
                row += "  " + dim(plural(days, "day").rjust(8))
            print(row)
            if book.get("comment"):
                for text in textwrap.wrap(f"“{book['comment']}”", WIDTH - 24):
                    print(" " * 23 + quote(text))
        print()

    # Totals.
    rule()
    rated = [b["rating"] for b in finished if b.get("rating") is not None]
    totals = [stat(len(books), "book" if len(books) == 1 else "books"),
              stat(len(finished), "finished"),
              stat(f"{sum(b['current_page'] for b in books):,}", "pages read")]
    if rated:
        totals.append(stat(f"{sum(rated) / len(rated):.1f}", "average rating"))
    print("   " + dim(" · ").join(totals))


def show_quiet(months):
    """One faint line for a stretch of months with no reading logged."""
    first, last = month_name(months[0]), month_name(months[-1])
    if first == last:
        span = first
    elif first[-4:] == last[-4:]:
        span = f"{first[:3]} – {last}"  # "Jun – Aug 2026"
    else:
        span = f"{first} – {last}"
    print(f"   {dim(span + ' · nothing logged')}\n")


# ── Main loop ────────────────────────────────────────────────────────────────

def main():
    books = load_books()
    banner()
    actions = {"1": add_book, "2": update_progress, "3": show_library}
    while True:
        show_menu(books)
        try:
            choice = ask().lower()
        except (KeyboardInterrupt, EOFError):
            break
        if choice in ("q", "quit", "exit"):
            break
        if choice in actions:
            try:
                actions[choice](books)
            except KeyboardInterrupt:  # Ctrl+C cancels the current step, not the app
                print()
                note("Cancelled.")
            except EOFError:
                break
        elif choice:
            warn("Please choose 1, 2, 3 or q.")
    print()
    note("Happy reading!")
    print()


if __name__ == "__main__":
    main()
