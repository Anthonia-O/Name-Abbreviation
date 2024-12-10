import re
from collections import defaultdict
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console_handler)

def debug_log(message):
    """Helper function to log debug messages."""
    logger.debug(message)

def load_names(filename):
    """Load names from the provided file."""
    try:
        with open(filename, 'r') as file:
            names = [line.strip() for line in file if line.strip()]
        debug_log(f"Loaded names: {names}")
        return names
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. Please check the file path and try again.")
        return []

def load_letter_values(filename):
    """Load letter values from values.txt for scoring."""
    values = {}
    with open(filename, 'r') as file:
        for line in file:
            letter, value = line.strip().split()
            values[letter] = int(value)
    debug_log(f"Loaded letter values: {values}")
    return values

def generate_abbreviations(name):
    """Generate three-letter abbreviations from a name."""
    words = re.findall(r'[A-Za-z]+', name.upper())  # Splits names, removes non-letters
    abbreviations = set()
    all_letters = "".join(words)  # Combine all words into a single sequence

    # Generate abbreviations: first letter + two subsequent letters in order
    for i in range(1, len(all_letters) - 1):
        for j in range(i + 1, len(all_letters)):
            abbreviation = all_letters[0] + all_letters[i] + all_letters[j]
            abbreviations.add(abbreviation)

    debug_log(f"Generated abbreviations for '{name}': {abbreviations}")
    return list(abbreviations)

def calculate_score(abbreviation, words, values):
    """Calculate the score of a given abbreviation based on position and values."""
    score = 0
    for i, letter in enumerate(abbreviation[1:], start=1):  # Second and third letters
        if any(word.startswith(letter) for word in words):  # First letter of any word
            position_score = 0
        elif any(word.endswith(letter) for word in words):  # Last letter of any word
            position_score = 5 if letter != 'E' else 20
        else:
            # Middle letter logic
            position = i + 1  # Position within the abbreviation
            position_score = position + values.get(letter, 0)
        score += position_score
    debug_log(f"Score for abbreviation '{abbreviation}': {score}")
    return score

def find_best_abbreviation(names, values):
    """Find the best unique abbreviations with the lowest scores across all names."""
    abbreviation_scores = defaultdict(list)  # Track all scores for each abbreviation
    unique_abbreviations = set()

    for name in names:
        words = re.findall(r'[A-Za-z]+', name.upper())
        abbreviations = generate_abbreviations(name)

        for abbrev in abbreviations:
            score = calculate_score(abbrev, words, values)
            abbreviation_scores[abbrev].append((name, score))

    # Identify unique abbreviations
    for abbrev, entries in abbreviation_scores.items():
        if len(entries) == 1:  # Unique abbreviation
            name, score = entries[0]
            unique_abbreviations.add((name, abbrev, score))

    # Choose the best abbreviation(s) for each name
    final_abbreviations = defaultdict(list)
    for name, abbrev, score in unique_abbreviations:
        final_abbreviations[name].append((abbrev, score))

    # Sort abbreviations by score and select the best ones
    results = {}
    for name in names:
        if name in final_abbreviations:
            best = sorted(final_abbreviations[name], key=lambda x: (x[1], x[0]))  # Sort by score, then alphabetically
            best_abbrevs = [abbrev for abbrev, score in best if score == best[0][1]]  # Tied abbreviations
            results[name] = " ".join(best_abbrevs)  # Join tied abbreviations
        else:
            results[name] = ""  # No acceptable abbreviation
    debug_log(f"Final abbreviations: {results}")
    return results


def write_output(output_filename, data):
    """Write the abbreviations to an output file."""
    with open(output_filename, 'w') as file:
        for name, abbreviation in data.items():
            file.write(f"{name}\n{abbreviation}\n\n")
    debug_log(f"Results written to {output_filename}")

def main():
    """Main function to execute the program."""
    input_filename = input("Enter the name of the input .txt file: ").strip()
    surname = input("Enter your surname: ").strip().lower()

    # Load input names and letter values
    names = load_names(input_filename)
    if not names:
        print("No valid names found in the input file. Exiting.")
        return
    values = load_letter_values('values.txt')

    # Find the best abbreviations
    results = find_best_abbreviation(names, values)

    # Write results to the output file
    output_filename = f"{surname}_{input_filename.split('.')[0]}_abbrevs.txt"
    write_output(output_filename, results)
    print(f"Results have been written to {output_filename}")

if __name__ == "__main__":
    main()
