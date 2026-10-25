"""Keep only the birds the app is sure about.

The app finds a list of birds. Each bird is a pair: (name, score).
The score is how sure the app is, from 0 to 1.
0.62 means "62% sure". Higher is more sure.

Example list:

    [("Blue Jay", 0.62), ("Steller's Jay", 0.08), ("Gray Jay", 0.25)]

keep_confident gives back only the birds whose score is at least
min_score, in the same order they came in.

Run this file to check the function:

    python3 keep_confident.py

"""


def keep_confident(results, min_score):
    keep = []
    for pair in results:
        score = pair[1]
        if score >= min_score:
            keep.append(pair)
    return keep


if __name__ == "__main__":
    sample = [("Blue Jay", 0.62), ("Steller's Jay", 0.08), ("Gray Jay", 0.25)]

    checks = [
        (keep_confident(sample, 0.2), [("Blue Jay", 0.62), ("Gray Jay", 0.25)]),
        (keep_confident(sample, 0.9), []),
        (keep_confident([], 0.2), []),
        (keep_confident(sample, 0.0), sample),
    ]

    all_good = True
    for number, (got, wanted) in enumerate(checks, start=1):
        if got == wanted:
            print(f"Check {number}: good!")
        else:
            all_good = False
            print(f"Check {number}: not yet. You got {got}, but we wanted {wanted}.")

    if all_good:
        print("All checks passed.")
