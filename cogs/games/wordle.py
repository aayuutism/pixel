import random
from cogs.games.words import WORDS

def get_random_word() -> str:
    """Flattens the categorized dictionary to pick a random 5-letter word."""
    all_words = [word for letter_group in WORDS.values() for word in letter_group]
    return random.choice(all_words).upper()

def check_guess(secret: str, guess: str) -> str:
    """Evaluates the guess against the secret word and returns colored blocks."""
    result = ["⬛"] * 5
    secret_letters = list(secret)
    
    # First pass: Check for Green (exact position matches)
    for i in range(5):
        if guess[i] == secret[i]:
            result[i] = "🟩"
            secret_letters[i] = None

    # Second pass: Check for Yellow (correct letter, wrong position)
    for i in range(5):
        if result[i] != "🟩" and guess[i] in secret_letters:
            result[i] = "🟨"
            secret_letters[secret_letters.index(guess[i])] = None

    return "".join(result)

def play_wordle():
    secret_word = get_random_word()
    attempts = 6
    history = []

    print("🟩🟨⬛ WELCOME TO WORDLE! ⬛🟨🟩")
    print("Guess the 5-letter word in 6 tries.\n")

    for turn in range(1, attempts + 1):
        while True:
            guess = input(f"Attempt {turn}/{attempts}: ").strip().upper()
            if len(guess) == 5 and guess.isalpha():
                break
            print("⚠️ Invalid guess! Please enter a 5-letter word.")

        feedback = check_guess(secret_word, guess)
        history.append(f"{guess}  {feedback}")

        print("\n--- Board ---")
        for line in history:
            print(line)
        print("-------------\n")

        if guess == secret_word:
            print(f"🎉 Fantastic! You guessed the word in {turn} tries!")
            return

    print(f"💀 Game Over! The word was **{secret_word}**.")

if __name__ == "__main__":
    play_wordle()
