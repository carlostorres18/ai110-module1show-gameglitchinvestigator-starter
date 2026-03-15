import random
import streamlit as st
from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

# FIXED: Replaced pending_messages/pending_balloons/input_counter with a single
# persistent "feedback" state variable. The old pattern cleared pending_messages on
# every render pass (line 142), which could wipe messages before the user saw them,
# requiring a second submit. Now feedback persists until the next guess overwrites it.
if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

if st.session_state.show_balloons:
    st.balloons()
    st.session_state.show_balloons = False

if st.session_state.feedback:
    fb_type, fb_text = st.session_state.feedback
    if fb_type == "error":
        st.error(fb_text)
    elif fb_type == "warning":
        st.warning(fb_text)
    elif fb_type == "success":
        st.success(fb_text)

with st.form("guess_form"):
    raw_guess = st.text_input(
        "Enter your guess:",
        key=f"guess_input_{st.session_state.input_counter}"
    )
    submit = st.form_submit_button("Submit Guess 🚀")

col2, col3 = st.columns(2)
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

#FIXED: Added status reset so the status gate below lets the new game through
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.feedback = None
    st.success("New game started.")
    st.rerun()

#FIXED: This gate no longer blocks new games because status is reset above
if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    # FIXED: Invalid input (non-numbers) no longer counts as an attempt — attempt
    # increment moved inside the else block so only valid, new guesses consume a turn.
    if not ok:
        st.session_state.feedback = ("error", err)
    # FIXED: Duplicate guesses no longer count as a new attempt — added a check
    # against history before incrementing attempts or processing the guess.
    # FIXED: Out-of-range guesses are now rejected — added bounds check using the
    # difficulty-based low/high range so guesses outside it don't consume an attempt.
    elif guess_int < low or guess_int > high:
        st.session_state.feedback = ("error", f"Guess must be between {low} and {high}.")
    elif guess_int in st.session_state.history:
        st.session_state.feedback = ("warning", f"You already guessed {guess_int}. Try a different number!")
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome = check_guess(guess_int, st.session_state.secret)
        messages = {"Win": "🎉 Correct!", "Too High": "📉 Go LOWER!", "Too Low": "📈 Go HIGHER!"}
        message = messages.get(outcome, "")

        if show_hint:
            st.session_state.feedback = ("warning", message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.session_state.show_balloons = True
            st.session_state.status = "won"
            st.session_state.feedback = (
                "success",
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.session_state.feedback = (
                    "error",
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

    st.session_state.input_counter += 1
    st.rerun()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
