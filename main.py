import random
from typing import Any
from itertools import product

# http://cs.gettysburg.edu/~tneller/papers/acg2017.pdf

# Lookup table for scoring sets of dice.
scoring = {
    (1, 1, 1): 1000,
    (6, 6, 6): 600,
    (5, 5, 5): 500,
    (4, 4, 4): 400,
    (3, 3, 3): 300,
    (2, 2, 2): 200,
    (1): 100,
    (5): 50
}

target_score = 2000


class Player:
    score: int = 0
    turn_score: int = 0
    roll: tuple[int] = []

    def roll(self):
        self.roll = roll(len(self.roll))

    def __repr__(self) -> str:
        pass


def roll(size: int) -> tuple[int]:
    return (random.randint(1, 6) for _ in range(size))


def score(dice: tuple[int]) -> int:
    for combo, score in scoring:
        if match(combo, dice):
            (dice.remove(die) for die in combo)
            return score
    return 0


def match(combo: tuple[int], roll: tuple[int]):
    for die in combo:
        if die not in roll:
            return False
        roll.remove(die)
    return True


def p_winning_from_banking( # W(b, d, n, t)
    player_score: int, # b
    opponent_score: int, # d
    remaining_dice: int, # n
    player_turn_score: int # t
):
    if player_score + player_turn_score >= target_score:
        return 1
    if player_turn_score == 0:
        return p_rolling(
            player_score,
            opponent_score,
            remaining_dice,
            player_turn_score
        )
    else:
        return max(
            1 - p_winning_from_banking(
                opponent_score,
                player_score + player_turn_score,
                6,
                0
            ),
            p_rolling(
                player_score,
                opponent_score,
                remaining_dice,
                player_turn_score
            )
        )


# TODO: Pre-cache sequences for all values of n from 1 to 6
def p_rolling(
    player_score: int, # b
    opponent_score: int, # d
    remaining_dice: int, # n
    player_turn_score: int # t
):
    p = 0
    sequences = generate_sequences(remaining_dice)
    for sequence in sequences:
        p += p_winning_from_scoring(
            player_score,
            opponent_score,
            remaining_dice,
            player_turn_score,
            sequence
        ) * (1 / len(sequences))
    return p


def p_winning_from_scoring( # W(b, d, n, t, r)
    player_score: int, # b
    opponent_score: int, # d
    remaining_dice: int, # n
    player_turn_score: int, # t
    roll: tuple[int] # r
):
    pass


def generate_sequences(n: int) -> list[list[Any]]:
    temp = (tuple(range(1, 7)) for _ in range(n))
    return tuple(product(*temp))


if __name__ == "__main__":
    print(len(generate_sequences(6)))