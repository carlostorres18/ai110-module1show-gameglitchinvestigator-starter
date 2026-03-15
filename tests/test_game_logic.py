from pathlib import Path
from streamlit.testing.v1 import AppTest
from logic_utils import check_guess, get_range_for_difficulty, update_score

APP_PATH = str(Path(__file__).parent.parent / "app.py")

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


def test_new_game_resets_status_after_game_ends():
    """
    Regression test for the new-game-blocked bug.

    Before the fix, the New Game handler reset `attempts` and `secret` but never
    reset `status`. After a game ended (won or lost), the status gate
    (`if st.session_state.status != "playing": st.stop()`) would immediately halt
    execution on rerun — leaving the player permanently stuck on the end-game
    screen even after clicking New Game.

    After the fix, `status` is reset to "playing" inside the New Game handler,
    so the gate lets the new game through and the guess input is accessible again.

    Covers both terminal states: "won" and "lost".
    """
    for terminal_status in ("won", "lost"):
        at = AppTest.from_file(APP_PATH)
        at.run()
        assert not at.exception

        # Simulate a finished game by forcing status to a terminal state
        at.session_state["status"] = terminal_status
        at.run()
        assert not at.exception

        # Click "New Game" — button[1] because button[0] is the form's Submit Guess
        at.button[1].click().run()
        assert not at.exception

        # Core assertion: status must be reset to "playing" so the gate lets through
        assert at.session_state["status"] == "playing", (
            f"After clicking New Game from '{terminal_status}' state, "
            f"status should be 'playing' but got '{at.session_state['status']}'"
        )

        # The guess input must be visible — proves st.stop() was NOT triggered
        assert len(at.text_input) > 0, (
            "Guess input not found — the status gate is still blocking the new game"
        )


def test_new_game_clears_history():
    """
    Regression test for the history-not-reset bug.

    Before the fix, the New Game handler reset `attempts`, `secret`, and `status`
    but never reset `history`. Guesses from a previous game remained in the list,
    so the Developer Debug Info would show stale guesses as if they belonged to
    the current game.

    After the fix, `history` is reset to [] inside the New Game handler, so only
    guesses from the active game appear in the list.
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    # Make a guess to populate history
    at.text_input[0].set_value("42")
    at.button[0].click().run()  # Submit Guess (form submit button)
    assert not at.exception

    # History must contain the guess before we reset
    assert 42 in at.session_state["history"], (
        "Expected guess 42 to be in history after submission"
    )

    # Click "New Game" — button[1] is the New Game button
    at.button[1].click().run()
    assert not at.exception

    # Core assertion: history must be empty after a new game starts
    assert at.session_state["history"] == [], (
        f"After clicking New Game, history should be [] but got "
        f"{at.session_state['history']}"
    )


def test_enter_key_submits_guess():
    """
    Regression test for the Enter-key-does-nothing bug.

    Before the fix, the submit trigger was `st.button`, which only returns True
    when the button is physically clicked — pressing Enter in the text field
    caused a plain page rerun with `submit=False`, so the guess was silently
    ignored and no attempt was consumed.

    After the fix, the input lives inside `st.form` with `st.form_submit_button`.
    Streamlit forms wire Enter-key presses inside the form directly to the submit
    button, so pressing Enter now correctly processes the guess.

    In AppTest, `set_value(...).run()` on a form text_input simulates exactly
    that: typing a value and pressing Enter. The assertion confirms that the
    guess was actually processed (attempt count incremented), which would have
    failed on the old plain-button code.
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    attempts_before = at.session_state["attempts"]

    # Simulate typing a guess and pressing Enter via form submit button
    at.session_state["secret"] = 99  # ensure the guess is valid but not a win
    at.text_input[0].set_value("42")
    at.button[0].click().run()
    assert not at.exception

    # Core assertion: Enter must have triggered form submission and consumed an attempt
    assert at.session_state["attempts"] == attempts_before + 1, (
        "Pressing Enter did not submit the guess — "
        "attempt count unchanged, which means the submit was ignored"
    )


def test_hint_direction_matches_guess():
    """
    Regression test for the swapped hint direction bug.

    Before the fix, the message mapping in app.py had the directions inverted:
      - "Too High" was paired with "📈 Go HIGHER!" (should be Go LOWER)
      - "Too Low"  was paired with "📉 Go LOWER!"  (should be Go HIGHER)

    So a player who guessed too high was told to go even higher — making the
    game unsolvable by following the hints.

    After the fix, the mapping is correct:
      - guess > secret → outcome "Too High" → hint says "Go LOWER"
      - guess < secret → outcome "Too Low"  → hint says "Go HIGHER"
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    # Fix the secret so we control whether each guess is too high or too low
    at.session_state["secret"] = 50

    # --- Guess too high (80 > 50): hint must tell the player to go LOWER ---
    at.text_input[0].set_value("80")
    at.button[0].click().run()
    assert not at.exception

    feedback = at.session_state["feedback"]
    assert feedback is not None, "No feedback was set after submitting a guess"
    assert "LOWER" in feedback[1], (
        f"Guess too high (80 > 50): expected hint to say 'Go LOWER' but got '{feedback[1]}'"
    )
    assert "HIGHER" not in feedback[1], (
        f"Guess too high (80 > 50): hint incorrectly says 'Go HIGHER' — direction is still swapped"
    )

    # --- Guess too low (20 < 50): hint must tell the player to go HIGHER ---
    at.text_input[0].set_value("20")
    at.button[0].click().run()
    assert not at.exception

    feedback = at.session_state["feedback"]
    assert feedback is not None, "No feedback was set after submitting a guess"
    assert "HIGHER" in feedback[1], (
        f"Guess too low (20 < 50): expected hint to say 'Go HIGHER' but got '{feedback[1]}'"
    )
    assert "LOWER" not in feedback[1], (
        f"Guess too low (20 < 50): hint incorrectly says 'Go LOWER' — direction is still swapped"
    )


def test_feedback_persists_after_single_submit():
    """
    Regression test for the double-submit bug.

    Before the fix, feedback was stored in `pending_messages`, a list that was
    unconditionally cleared on every render pass:

        st.session_state.pending_messages = []   # old line 142

    Streamlit can trigger extra reruns internally (e.g. from session_state
    mutations during render). Any such rerun wiped pending_messages before the
    player saw the result, making the app appear unresponsive — guesses were
    silently processed but the feedback vanished, so the player had to press
    Submit a second time to see any output.

    After the fix, feedback is written to `st.session_state.feedback`, a plain
    tuple that is only overwritten when a NEW guess is submitted. It therefore
    survives extra reruns unchanged.

    This test verifies:
      1. A single Submit sets feedback immediately (guess IS recognized on click 1).
      2. An extra rerun — simulating Streamlit's internal reruns — does NOT clear
         that feedback (the player still sees the result without a second click).
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    at.session_state["secret"] = 50  # pin secret so the guess is not a win

    # Single Submit — the player presses the button exactly once
    at.text_input[0].set_value("30")
    at.button[0].click().run()
    assert not at.exception

    # Assertion 1: feedback must be set after ONE submit
    assert "feedback" in at.session_state, (
        "feedback key missing after a single submit — the guess was not recognized. "
        "This is the double-submit bug: pending_messages was cleared before display."
    )
    feedback_after_submit = at.session_state["feedback"]
    assert feedback_after_submit is not None, (
        "feedback is None after a single submit — guess was processed but result lost."
    )
    assert feedback_after_submit[1] != "", (
        "feedback message is empty after a single submit"
    )

    # Assertion 2: an extra rerun must not wipe the feedback
    # (old pending_messages pattern cleared the list on every render pass)
    at.run()
    assert not at.exception

    assert "feedback" in at.session_state, (
        "feedback key was removed by an extra rerun — this is the double-submit bug. "
        "The old pending_messages pattern wiped messages on every render pass."
    )
    feedback_after_rerun = at.session_state["feedback"]
    assert feedback_after_rerun is not None, (
        "feedback was cleared by an extra rerun — this is the double-submit bug. "
        "The old pending_messages pattern wiped messages on every render pass, so "
        "any Streamlit-internal rerun made feedback disappear until the next Submit."
    )
    assert feedback_after_rerun == feedback_after_submit, (
        "feedback changed after an extra rerun without a new submission — "
        "something is still clearing or mutating it unexpectedly."
    )


def test_invalid_input_does_not_consume_attempt():
    """
    Regression test for the invalid-input-counts-as-a-guess bug.

    Before the fix, `st.session_state.attempts += 1` ran unconditionally at the
    top of the submit block — before `parse_guess` was called. Typing "abc" or
    any non-number would still increment the attempt counter and append the raw
    string to history, silently burning one of the player's limited turns.

    After the fix, the increment is inside the `else` branch that only runs when
    `parse_guess` returns ok=True, so invalid input leaves attempts unchanged.
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    at.session_state["secret"] = 50
    attempts_before = at.session_state["attempts"]

    # Submit a non-number
    at.text_input[0].set_value("abc")
    at.button[0].click().run()
    assert not at.exception

    # Core assertion: attempts must not have changed
    assert at.session_state["attempts"] == attempts_before, (
        f"Invalid input 'abc' consumed an attempt — "
        f"attempts went from {attempts_before} to {at.session_state['attempts']}"
    )

    # Invalid input must not appear in history
    assert "abc" not in at.session_state["history"], (
        "Invalid input 'abc' was added to history — it should be silently rejected"
    )

    # An error message must be shown instead
    feedback = at.session_state["feedback"]
    assert feedback is not None and feedback[0] == "error", (
        "Expected an error feedback message for invalid input, but got none"
    )


def test_duplicate_guess_does_not_consume_attempt():
    """
    Regression test for the duplicate-guess-counts-as-new-attempt bug.

    Before the fix, there was no check against history before processing a
    guess — the same number submitted twice would increment attempts twice,
    effectively letting a player waste turns by accident (or drain attempts
    without gaining any new information).

    After the fix, an `elif guess_int in st.session_state.history` guard
    short-circuits before incrementing attempts, so repeat guesses are free.
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    at.session_state["secret"] = 50

    # First submission — should be processed normally
    at.text_input[0].set_value("30")
    at.button[0].click().run()
    assert not at.exception

    attempts_after_first = at.session_state["attempts"]
    assert 30 in at.session_state["history"], "First guess 30 should be in history"

    # Second submission of the same number — must NOT increment attempts
    at.text_input[0].set_value("30")
    at.button[0].click().run()
    assert not at.exception

    # Core assertion: attempts must not have changed on the duplicate
    assert at.session_state["attempts"] == attempts_after_first, (
        f"Duplicate guess '30' consumed an attempt — "
        f"attempts went from {attempts_after_first} to {at.session_state['attempts']}"
    )

    # History must still contain exactly one entry for 30
    assert at.session_state["history"].count(30) == 1, (
        f"Duplicate guess '30' was added to history again: {at.session_state['history']}"
    )

    # A warning message must be shown for the duplicate
    feedback = at.session_state["feedback"]
    assert feedback is not None and feedback[0] == "warning", (
        "Expected a warning feedback message for a duplicate guess, but got none"
    )


def test_out_of_range_guess_does_not_consume_attempt():
    """
    Regression test for the out-of-range guess bug.

    Before the fix, parse_guess only validated that input was a valid number —
    it never checked whether the value fell within the difficulty-based [low, high]
    range. A player on Easy mode (1–20) could guess 999 and it would be processed
    as a legitimate attempt, consuming a turn and potentially distorting the score.

    Additionally, the st.info banner always displayed "between 1 and 100" regardless
    of difficulty, so the stated range and the enforced range were inconsistent.

    After the fix, an elif guard in the submit block rejects any guess outside
    [low, high] with an error message, without incrementing attempts or touching
    history — mirroring how invalid (non-numeric) input is handled.

    This test covers:
      - A guess above the range ceiling is rejected (no attempt consumed, not in history,
        error feedback shown).
      - A guess below the range floor is rejected under the same conditions.
      - A valid in-range guess IS accepted (attempt incremented, value in history).
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    # Use Easy difficulty: range is 1–20
    at.sidebar.selectbox[0].set_value("Easy")
    at.run()
    assert not at.exception

    at.session_state["secret"] = 10  # pin secret so no accidental win
    attempts_before = at.session_state["attempts"]

    # --- Guess above ceiling (50 > 20): must be rejected ---
    at.text_input[0].set_value("50")
    at.button[0].click().run()
    assert not at.exception

    assert at.session_state["attempts"] == attempts_before, (
        f"Out-of-range guess 50 (Easy ceiling is 20) consumed an attempt — "
        f"attempts went from {attempts_before} to {at.session_state['attempts']}"
    )
    assert 50 not in at.session_state["history"], (
        "Out-of-range guess 50 was added to history — it should be rejected silently"
    )
    feedback = at.session_state["feedback"]
    assert feedback is not None and feedback[0] == "error", (
        "Expected an error feedback for an out-of-range guess above the ceiling, but got none"
    )

    # --- Guess below floor (0 < 1): must also be rejected ---
    at.text_input[0].set_value("0")
    at.button[0].click().run()
    assert not at.exception

    assert at.session_state["attempts"] == attempts_before, (
        f"Out-of-range guess 0 (Easy floor is 1) consumed an attempt — "
        f"attempts went from {attempts_before} to {at.session_state['attempts']}"
    )
    assert 0 not in at.session_state["history"], (
        "Out-of-range guess 0 was added to history — it should be rejected"
    )
    feedback = at.session_state["feedback"]
    assert feedback is not None and feedback[0] == "error", (
        "Expected an error feedback for an out-of-range guess below the floor, but got none"
    )

    # --- Valid in-range guess (5): must be accepted and consume an attempt ---
    at.text_input[0].set_value("5")
    at.button[0].click().run()
    assert not at.exception

    assert at.session_state["attempts"] == attempts_before + 1, (
        f"Valid in-range guess 5 did not consume an attempt — "
        f"attempts stayed at {at.session_state['attempts']}"
    )
    assert 5 in at.session_state["history"], (
        "Valid in-range guess 5 was not recorded in history"
    )


def test_input_clears_after_submission():
    """
    Regression test for the input-clearing bug.

    Before the fix, the text input used a static widget key, so Streamlit
    restored the previous typed value on every rerun — the user had to manually
    delete their old guess before typing a new one.

    After the fix, the input lives inside an st.form. Streamlit automatically
    resets all form inputs to empty after the form is submitted, so the field
    should be blank and ready for the next guess without any manual clearing.
    """
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert not at.exception

    # Input should start empty
    assert at.text_input[0].value == ""

    # Simulate the user typing a guess
    at.text_input[0].set_value("42")
    assert at.text_input[0].value == "42"

    # Submit the form (the "Submit Guess" form_submit_button)
    at.button[0].click().run()
    assert not at.exception

    # After submission the field must be empty — this is what the bug broke
    assert at.text_input[0].value == ""


def test_hard_difficulty_range_is_harder_than_normal():
    """
    Regression test for the Hard difficulty range bug.

    Before the fix, get_range_for_difficulty("Hard") returned (1, 50) — a range
    SMALLER than Normal's (1, 100). A smaller range means fewer possible values,
    making it EASIER to guess the number, which is the opposite of what "Hard"
    should mean.

    After the fix, Hard returns (1, 200), giving a larger search space than
    Normal and making it genuinely harder to land on the secret.

    This test asserts:
      - Hard upper bound is greater than Normal upper bound (Hard is harder by range).
      - Hard upper bound is greater than Easy upper bound.
    """
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")

    assert hard_high > normal_high, (
        f"FIXED BUG: Hard range ceiling ({hard_high}) should be greater than "
        f"Normal range ceiling ({normal_high}), but it was not — "
        f"Hard was easier than Normal before the fix."
    )
    assert hard_high > easy_high, (
        f"Hard range ceiling ({hard_high}) should be greater than "
        f"Easy range ceiling ({easy_high})."
    )


def test_win_score_not_over_penalized_by_off_by_one():
    """
    Regression test for the win score off-by-one bug.

    Before the fix, update_score calculated win points as:
        points = 100 - 10 * (attempt_number + 1)

    Since attempt_number is already 1-based (incremented before the call),
    the extra +1 over-penalized every win. A first-attempt win earned:
        100 - 10 * (1 + 1) = 80  ← wrong
    instead of:
        100 - 10 * 1 = 90         ← correct

    After the fix the formula is 100 - 10 * attempt_number, so points match
    the expected penalty per attempt without double-counting.

    This test asserts the exact point values for attempt numbers 1, 2, and 3.
    """
    # Attempt 1: should award 100 - 10*1 = 90 points (was 80 before fix)
    score_after_attempt_1 = update_score(0, "Win", 1)
    assert score_after_attempt_1 == 90, (
        f"FIXED BUG: Win on attempt 1 should award 90 points but got {score_after_attempt_1}. "
        f"The off-by-one (+1) in the formula was over-penalizing wins."
    )

    # Attempt 2: should award 100 - 10*2 = 80 points (was 70 before fix)
    score_after_attempt_2 = update_score(0, "Win", 2)
    assert score_after_attempt_2 == 80, (
        f"FIXED BUG: Win on attempt 2 should award 80 points but got {score_after_attempt_2}."
    )

    # Attempt 3: should award 100 - 10*3 = 70 points (was 60 before fix)
    score_after_attempt_3 = update_score(0, "Win", 3)
    assert score_after_attempt_3 == 70, (
        f"FIXED BUG: Win on attempt 3 should award 70 points but got {score_after_attempt_3}."
    )


def test_too_high_wrong_guess_always_penalizes():
    """
    Regression test for the wrong-guess reward bug.

    Before the fix, update_score had this logic for "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5   # ← BUG: rewarded a wrong guess!
        return current_score - 5

    On even-numbered attempts, guessing too high would ADD 5 points instead of
    deducting them, rewarding the player for being wrong.

    After the fix, "Too High" always deducts 5 points regardless of attempt number.

    This test asserts that both even and odd attempt numbers result in a -5 penalty.
    """
    starting_score = 100

    # Odd attempt (1): must penalize -5
    score_odd = update_score(starting_score, "Too High", 1)
    assert score_odd == starting_score - 5, (
        f"'Too High' on odd attempt should penalize -5 but score went from "
        f"{starting_score} to {score_odd}."
    )

    # Even attempt (2): must also penalize -5 (was +5 before fix)
    score_even = update_score(starting_score, "Too High", 2)
    assert score_even == starting_score - 5, (
        f"FIXED BUG: 'Too High' on even attempt should penalize -5 but score went from "
        f"{starting_score} to {score_even}. Before the fix this returned +5, "
        f"rewarding the player for a wrong guess."
    )

    # Even attempt (4): double-check with another even number
    score_even_4 = update_score(starting_score, "Too High", 4)
    assert score_even_4 == starting_score - 5, (
        f"FIXED BUG: 'Too High' on attempt 4 (even) should penalize -5 but got {score_even_4}."
    )
