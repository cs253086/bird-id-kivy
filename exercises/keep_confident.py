"""Exercise: keep only the birds the app is sure about.

The app finds a list of birds. Each bird is a pair: (name, score).
The score is how sure the app is, from 0 to 1.
0.62 means "62% sure". Higher is more sure.

Example list:

    [("Blue Jay", 0.62), ("Steller's Jay", 0.08), ("Gray Jay", 0.25)]

Your job: write keep_confident so it gives back only the birds
with a score of at least min_score, in the same order.

How to do it, one step at a time:

    1. Make an empty list called keep. (Write:  keep = [] )
    2. Look at each pair in results, one at a time. (Use a for loop.)
    3. For each pair, check: is its score at least min_score?
       (Use an if. The score is the second item, so it is pair[1].)
    4. If yes, add the pair to keep. (Use keep.append(pair) )
    5. After the loop, give back keep.  (Use return keep )

Here is the same pattern on a different problem, so you can see how
the parts fit together. This one keeps only the numbers bigger than 5:

    def keep_big(numbers):
        keep = []
        for number in numbers:
            if number > 5:
                keep.append(number)
        return keep

Run this file to check your work:

    python3 keep_confident.py

"""


def keep_confident(results, min_score):
    # TODO: write your steps here. Right now this gives back nothing.
    return None


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
        print("All checks passed. You did it!")
