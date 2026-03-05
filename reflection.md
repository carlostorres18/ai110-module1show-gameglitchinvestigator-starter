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
  - One example of an AI suggestion that was correct: 

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
