# BookTracker

A small terminal app to keep track of your reading: what you're reading now, how far along you are, month by month how much you've read, and the books you want to read next.

## Requirements

Python 3.8 or newer. Nothing to install.

## Run it

```
python3 booktracker.py
```

On Windows: `py booktracker.py`.

You'll see the menu:

```
  3 reading · 7 finished · 136 pages in October

   1  Add a new book
   2  Update progress
   3  Check library
   4  Want to read
   q  Quit

  ›
```

Type a number (or `q`) and press Enter.

All dates are shown and typed as **DD/MM/YYYY**.

## 1 · Add a new book

| Question | What to type |
|---|---|
| **Title** | The book's title. Press Enter on its own to go back to the menu. |
| **Total pages** | The number of pages in the book. |
| **Current page** | The page you're on. Press Enter for 0, or type `-1` if you've already finished it. |
| **Started on** | The date as `DD/MM/YYYY`, e.g. `14/09/2026`. Press Enter for today. |

If you add a book you've already finished (current page = last page, or `-1`), the date question becomes **Finished on**, and you're asked for a review, just like below.

## 2 · Update progress

Pick the book from the list (if you're only reading one, it's picked for you) and type the page you're on. That's all; it's saved with today's date.

When you type the **last page** or **`-1`**, the book is marked as finished and you get two more prompts:

```
  ✔ Finished! Project Hail Mary · 476 pages in 22 days

  How was it? (Enter to skip)
  Rating (0-10) › 9
  Comment › Loved every page.
```

Press Enter to skip either one. Typed a page by mistake? Just update again with the right number; going back to a lower page is fine.

## 3 · Check library

```
  ── READING NOW ─────────────────────────────────────────────────────────────

   Project Hail Mary     ███████████░░░░░   71%  340/476  since 12/09/2026
   The Name of the Wind  █░░░░░░░░░░░░░░░    9%   66/662  since 28/09/2026

  ── MONTH BY MONTH ──────────────────────────────────────────────────────────

   Jul 2026  █████░░░░░░░░░░░░░░░░░░░  140 pages

   Aug 2026  ████████████████████████  582 pages  ← best month
             ✔ 03/08/2026  The Hobbit    ★★★★★★★★☆☆  8/10   15 days
                           “Cosy.”
             ✔ 21/08/2026  Dune          ★★★★★★★★★☆  9/10   17 days
                           “Spice must flow.”

   Sep 2026  ████████████░░░░░░░░░░░░  300 pages

   Oct 2026  ████░░░░░░░░░░░░░░░░░░░░  106 pages

  ────────────────────────────────────────────────────────────────────────────
   4 books · 2 finished · 1,128 pages read · 8.5 average rating

  ── WANT TO READ ────────────────────────────────────────────────────────────

   Babel           545 pages  added 14/09/2026
   Middlemarch       ? pages  added 30/09/2026
```

- **Reading now**: every book in progress, with how far along you are and when you started.
- **Month by month**: one bar per month for the pages you read, so your strongest periods stand out (the best one is marked). Under each month are the books you finished then, with the date, your rating, how many days it took and your comment. A stretch of months with no reading is folded into a single line, like `Feb – Apr 2026 · nothing logged`.
- **Totals** for the books you've read.
- **Want to read**: your list of books for later (see below). It only appears once the list has something on it.

In the terminal it's all in colour.

## 4 · Want to read

A list of books you'd like to read but haven't started. They're kept apart from your reading: they don't count as "reading", and they don't show up in Update progress.

The first time, you go straight to adding a book. After that, you see your list:

```
  ── WANT TO READ ────────────────────────────────────────────────────────────

    1  Babel           545 pages  added 14/09/2026
    2  Middlemarch       ? pages  added 30/09/2026

  a add a book  ·  1 start reading book 1  ·  d1 remove book 1
  Choose (Enter = back) ›
```

| Type | What happens |
|---|---|
| `a` | Add a book: the title, and the total pages (press Enter if you don't know them yet). The date added is today. |
| a number, e.g. `1` | **Start reading** that book. You're asked the start date (Enter = today), plus the total pages if you skipped them. The book moves from this list to *Reading now* at page 0, and from then on you use option 2 to log progress, as with any other book. |
| `d` + a number, e.g. `d2` | Remove that book from the list. |
| Enter | Back to the menu. |

## How pages per month are counted

Every time you update a book, the app notes today's date and the page you're on. The pages for a month are how far you moved forward during that month, across all your books. So:

- Update as you go: pages count on the day you log them.
- Pages you'd already read when you added a book count on its start date.
- Several updates on the same day are merged into one.

## Your data

Everything is saved in `library.json`, next to the script, after every change. It's plain JSON, so you can back it up, or open it to fix a typo in a title. One book looks like this:

```json
{
  "title": "Dune",
  "started": "2026-08-05",
  "finished": "2026-08-21",
  "total_pages": 412,
  "current_page": 412,
  "rating": 9,
  "comment": "Spice must flow.",
  "log": [
    {"date": "2026-08-05", "page": 0},
    {"date": "2026-08-12", "page": 150},
    {"date": "2026-08-21", "page": 412}
  ]
}
```

`started` is `null` for books you added as already finished, since the start date isn't known (which is also why they show no "days" in the library).

Inside the files, dates are stored as `YYYY-MM-DD` so they sort correctly; the app always shows them to you as DD/MM/YYYY.

Your want-to-read list lives in its own file, `library_want_to_read.json`, next to `library.json`:

```json
[
  {"title": "Babel", "total_pages": 545, "added": "2026-09-14"},
  {"title": "Middlemarch", "total_pages": null, "added": "2026-09-30"}
]
```

To keep the library somewhere else, set `BOOKTRACKER_FILE`. The want-to-read file follows it (here, `books_want_to_read.json` in the same folder):

```
BOOKTRACKER_FILE=~/Dropbox/books.json python3 booktracker.py
```

## Tips

- **Ctrl+C** cancels whatever you're in the middle of and takes you back to the menu. At the menu, it quits.
- Colours switch off on their own when the output isn't a terminal, or if you set the `NO_COLOR` environment variable.
