"""Exercise: keep only the confident bird matches.

The app gets back a list of (name, score) pairs, best first, like this:

    [("Blue Jay (Cyanocitta cristata)", 0.62), ("Steller's Jay", 0.08)]

Scores go from 0 to 1. A score of 0.62 means "62% sure".

Your job: write keep_confident so it returns only the pairs whose score
is at least min_score, in the same order they came in.

Run this file to check your work:

    python3 keep_confident.py
"""


def keep_confident(results, min_score):
    # TODO: replace this line with your code.
    # Hint: a list comprehension can loop over results and keep a pair
    # when its score (the second item) is big enough.
    raise NotImplementedError("Write the body of keep_confident first")


if __name__ == "__main__":
    sample = [("Blue Jay", 0.62), ("Steller's Jay", 0.08), ("Gray Jay", 0.25)]

    assert keep_confident(sample, 0.2) == [("Blue Jay", 0.62), ("Gray Jay", 0.25)]
    assert keep_confident(sample, 0.9) == []
    assert keep_confident([], 0.2) == []
    assert keep_confident(sample, 0.0) == sample

    print("All checks passed. Nice work!")
