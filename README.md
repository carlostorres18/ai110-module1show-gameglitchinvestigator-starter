# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### Game Purpose

**Game Glitch Investigator: The Impossible Guesser** is a number-guessing game built with Streamlit. The player tries to guess a randomly chosen secret number within a limited number of attempts. After each guess the game gives a hint — "Go Higher" or "Go Lower" — to help narrow down the answer. Difficulty settings (Easy, Normal, Hard) control the number range and the attempt limit. A score is tracked throughout each session, rewarding fast wins and penalizing wrong guesses.

---

### Bugs Found

| # | Bug | Where |
|---|-----|--------|
| 1 | **Secret number regenerated on every render** — `random.randint` was called unconditionally at the top of the script, so every button click produced a new secret, making it impossible to ever win. | `app.py` |
| 2 | **Hints were inverted** — "Too High" told the player to guess higher, and "Too Low" told them to guess lower, the exact opposite of the correct direction. | `app.py` (original hint map) |
| 3 | **Hard difficulty was easier than Normal** — the Hard range was `1–50`, narrower than Normal's `1–100`, so Hard was actually the easiest mode. | `logic_utils.py` `get_range_for_difficulty` |
| 4 | **Invalid input consumed an attempt** — entering a non-number (e.g. "abc") or an empty field still incremented the attempt counter before showing the error. | `app.py` |
| 5 | **Duplicate guesses consumed an attempt** — guessing the same number twice counted as a fresh attempt instead of prompting the player to try something different. | `app.py` |
| 6 | **Out-of-range guesses were accepted** — a guess outside the difficulty range (e.g. 500 on Easy) was processed normally and consumed an attempt. | `app.py` |
| 7 | **Feedback messages disappeared before the player could read them** — feedback was stored in a `pending_messages` list that was cleared on every render pass, so the message often vanished before the UI repainted. | `app.py` |
| 8 | **New Game button was blocked by the game-over gate** — after a win or loss, clicking "New Game" reset state but then immediately hit the `status != "playing"` guard before the new status was saved, so the game stayed stuck. | `app.py` |
| 9 | **Game logic was embedded inline in `app.py`** — `check_guess`, `parse_guess`, `get_range_for_difficulty`, and `update_score` were not in a separate module, making them untestable with `pytest`. | `app.py` |

---

### Fixes Applied

1. **Persisted the secret number in `st.session_state`** — wrapped the `random.randint` call in `if "secret" not in st.session_state:` so it only runs once per game session (`app.py:30–31`).

2. **Corrected the hint map** — swapped the messages so `"Too High"` displays "Go LOWER" and `"Too Low"` displays "Go HIGHER" (`app.py:136`).

3. **Fixed Hard difficulty range** — changed the Hard range from `1–50` to `1–200` in `get_range_for_difficulty` so it is genuinely harder than Normal (`logic_utils.py:10`).

4. **Moved attempt increment inside the valid-guess branch** — `st.session_state.attempts += 1` now only runs after input passes all validation checks, so invalid input, duplicates, and out-of-range guesses do not waste a turn (`app.py:132`).

5. **Added duplicate-guess detection** — before processing a guess, the code checks `guess_int in st.session_state.history` and warns the player without consuming an attempt (`app.py:129–130`).

6. **Added bounds validation** — guesses outside `[low, high]` are rejected with an error message and do not count as an attempt (`app.py:127–128`).

7. **Replaced ephemeral `pending_messages` with a persistent `feedback` state variable** — `st.session_state.feedback` holds the last message tuple `(type, text)` and is only overwritten when a new guess is submitted, so feedback stays visible across render passes (`app.py:52–83`).

8. **Reset `status` to `"playing"` in the New Game handler** — the New Game block now sets `st.session_state.status = "playing"` before `st.rerun()`, so the game-over guard is cleared before the next render (`app.py:99–106`).

9. **Refactored logic into `logic_utils.py`** — extracted `check_guess`, `parse_guess`, `get_range_for_difficulty`, and `update_score` into a separate module and covered them with `pytest` regression tests to prevent future regressions.

## 📸 Demo

![Fixed winning game](Screenshot%202026-03-15%20at%206.35.22%20PM.png)

![Tests passing](test%20passing%20screenshot.png)


## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
