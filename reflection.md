# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
  - So what I noticed when first trying the app, i had to manually delete the first guess that I had made and then make a new guess
  - When pressing new game, it would appear that a new game was created, but when inputting a guess it would not do anything.
  - When inspecting the hints snippet that the webpage has, it seems that it keeps track of guesses, including those of previous games even when a new one had already started.
  - It appears to be that once you win or lose a game once, you can no longer restart a new game from the webpage itself, but rather you have to stop the application from running and restart the application once again
  - 'Enter' key doesnt seem to work in the game
  - When you enter a guess you have to submit that guess twice so that it can be registered in the history of the game
  - You can repeat a guessed number and it would still count it as a new guess
  - The way that the game keeps track of the history of what numbers the user guesses, seems to be delayed and it puts in the history a number
  that the user tried even though they had just changed it, it seems that you have to press twice in order to have the bug be registered
  - Users have to clear the cache from the 3 dots menu on the side so that the game could restart again
  - it appears to be that once use all the guesses that you have, the game basically doesn't let you run a new game, because the guesses left counter has not been restarted yet.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  - First I used Claude Code in my terminal, since I have been wanting to get more used to it.
  - One example of an AI suggestion that was correct: Was that the game would allow you to input the same number twice and count both times as different tries, so it investigated that logic and it was able to not only find where, but also explain in full detail how a fix would work for this bug
  - One example of an AI suggestiong that was incorrect: It surprisingly did a good job when handling logic errors and stuff, but when it came down to creating the tests for the bugs that we were able to fix, Claude struggled a bit on creating the test and the program passing those tests. But after a change of prompt, the tests started to pass.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  - It was decided first by using the game manually after each fix that I would make, and then I would prompt the AI to make a test case so that I can test and see if there are any type of leaks in the program.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
  - So one of the test that I manually ran was the test case for the testing whether a guess was within the range that the game predefines at the beginning 1-100 and guessing 999 should output a texts saying that the guess is not within the range of the game mode, and it should not take a try guess from the player.
- Did AI help you design or understand any tests? How?
  - Yes it did, after prompting the AI to create a test for a specific bug that I fixed at the time, it would make the test, and then explain how the test works inside the program including what functions it calls when running that specific test case.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
  - Before any sort of fix was made, the check_guess function was broken and it would alternate the secret's type on every attempt. This is because the check_guess functions when it would receive a guess, ex: 40, it would receive "40" as a string and not 40 as an integer, which would make it feel as if the hint was moving.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  - Reruns makes it that every user interaction the application has, it causes the entire Python script to re-run from line 1. I would explain to my friend like this, if we were following a recipe for cooking and after everystep we make in the recipe we have to re-read the whole recipe again and do so during the entire process. For session state, to my friend I would say this, think of it as a sticky note that helps you remember values between runs, that way when you make a new run you can remember the value.

- What change did you make that finally gave the game a stable secret number?
  - The change that I made was that the session state guard would ensure that the random number function only ran once per game session, and not on every re-run. Lastly there is a check that would make it so that the program doesn't no more TypeError fallback.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
    - One habit that I would be reusing in future lab/projects would be for the AI to explain each bug one-by-one and explain how the bug is affecting the program as a whole and then making tests for those bugs one-by-one so that the AI is faster to see the problem and not get overwhelmed.

- What is one thing you would do differently next time you work with AI on a coding task?
  - One thing I would do different is to try to give the AI better prompts so that the AI can get my requests faster and it doesn't consume a lot of tokens.

- In one or two sentences, describe how this project changed the way you think about AI generated code.
  - The way this project changed the way I think about AI, is that AI is not here to replace Software Engineeners, or take away SE jobs, but rather improve the overall speed of a SE and make coding even much faster.
