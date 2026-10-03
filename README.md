# BookTracker

A small terminal app to keep track of your reading: what you're reading now, how far along you are, and month by month how much you've read.

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
   q  Quit

  ›
```

Type a number (or `q`) and press Enter.

## 1 · Add a new book

| Question | What to type |
|---|---|
| **Title** | The book's title. Press Enter on its own to go back to the menu. |
| **Total pages** | The number of pages in the book. |
| **Current page** | The page you're on. Press Enter for 0, or type `-1` if you've already finished it. |
| **Started on** | The date as `YYYY-MM-DD` (`DD/MM/YYYY` works too). Press Enter for today. |

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

   Project Hail Mary     ███████████░░░░░   71%  340/476  since 12 Sep 2026
   The Name of the Wind  █░░░░░░░░░░░░░░░    9%   66/662  since 28 Sep 2026

  ── MONTH BY MONTH ──────────────────────────────────────────────────────────

   Jul 2026  █████░░░░░░░░░░░░░░░░░░░  140 pages

   Aug 2026  ████████████████████████  582 pages  ← best month
             ✔  3 Aug  The Hobbit    ★★★★★★★★☆☆  8/10   15 days
                       “Cosy.”
             ✔ 21 Aug  Dune          ★★★★★★★★★☆  9/10   17 days
                       “Spice must flow.”

   Sep 2026  ████████████░░░░░░░░░░░░  300 pages

   Oct 2026  ████░░░░░░░░░░░░░░░░░░░░  106 pages

  ────────────────────────────────────────────────────────────────────────────
   4 books · 2 finished · 1,128 pages read · 8.5 average rating
```

- **Reading now**: every book in progress, with how far along you are and when you started.
- **Month by month**: one bar per month for the pages you read, so your strongest periods stand out (the best one is marked). Under each month are the books you finished then, with the date, your rating, how many days it took and your comment. A stretch of months with no reading is folded into a single line, like `Feb – Apr 2026 · nothing logged`.
- **Totals** at the bottom.

In the terminal it's all in colour.

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

To keep the library somewhere else, set `BOOKTRACKER_FILE`:

```
BOOKTRACKER_FILE=~/Dropbox/books.json python3 booktracker.py
```

## Tips

- **Ctrl+C** cancels whatever you're in the middle of and takes you back to the menu. At the menu, it quits.
- Colours switch off on their own when the output isn't a terminal, or if you set the `NO_COLOR` environment variable.
