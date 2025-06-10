import random
from typing import Any
from itertools import product, combinations, chain

# http://cs.gettysburg.edu/~tneller/papers/acg2017.pdf

# Lookup table for scoring sets of dice.
scoring = { # c
    (1, 1, 1): 1000,
    (6, 6, 6): 600,
    (5, 5, 5): 500,
    (4, 4, 4): 400,
    (3, 3, 3): 300,
    (2, 2, 2): 200,
    tuple([1]): 100,
    tuple([5]): 50
}

target_score = 2000

sequences: dict[int, tuple[tuple[int]]] = dict()

scoring_combos: dict[tuple[int], dict[int, int]] = dict()


class Player:
    score: int = 0
    turn_score: int = 0
    roll: tuple[int] = []

    def roll(self):
        self.roll = roll(len(self.roll))

    def __repr__(self) -> str:
        pass


def cache():
    print("Generating roll sequences cache...")

    # Pre-cache roll sequences
    sequences = {
        dice:generate_sequences(dice) for dice in range(1, 7)
    }

    cache_size = sum(len(values) for values in sequences.values())
    print(f"Cache size: {cache_size}")

    print("Generating scoring combinations cache...")
    
    scoring_combos = {
        roll:possible_scorings(roll) \
            for roll in chain(*sequences.values()) 
    }

    cache_size = sum(len(values) for values in scoring_combos.values())
    print(f"Cache size: {cache_size}")


def roll(size: int) -> tuple[int]:
    return (random.randint(1, 6) for _ in range(size))


def score(dice: list[int]) -> int:
    score = 0

    for combo, combo_score in scoring.items():
        while match(combo, dice):
            [dice.remove(die) for die in combo]
            score += combo_score
    
    return score


def match(combo: tuple[int], roll: list[int]):
    roll_list = list(roll)
    for die in combo:
        if die not in roll_list:
            return False
        roll_list.remove(die)
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


def p_rolling(
    player_score: int, # b
    opponent_score: int, # d
    remaining_dice: int, # n
    player_turn_score: int # t
):
    p = 0
    print(sequences)
    for sequence in sequences[remaining_dice]:
        p += p_winning_from_scoring(
            player_score,
            opponent_score,
            remaining_dice,
            player_turn_score,
            sequence
        ) * (1 / len(sequences[remaining_dice]))
    return p


def p_winning_from_scoring( # W(b, d, n, t, r)
    player_score: int, # b
    opponent_score: int, # d
    remaining_dice: int, # n
    player_turn_score: int, # t
    roll: tuple[int] # r
):
    scoring_combos = possible_scorings(roll).items()

    if not scoring_combos:
        return 1 - p_winning_from_banking(
            opponent_score,
            player_score,
            6,
            0
        )
    else:
        return max([
            p_winning_from_banking(
                player_score,
                opponent_score,
                hot_dice(remaining_dice - sn),
                player_turn_score + sp
            ) \
                for sn, sp in scoring_combos
        ])
        

# TODO: Avoid generating combinations that won't score.
def possible_scorings(roll: tuple[int]) -> dict[int, int]:
    scorings: dict[int, int] = {}

    combos = list(
        chain.from_iterable(
            combinations(roll, n) for n in range(len(roll))
        )
    )

    for combo in combos:
        combo_list = list(combo)
        combo_score = score(combo_list)
        if combo_score > 0:
            scorings[len(combo) - len(combo_list)] = combo_score

    return scorings


def hot_dice(remaining_dice: int) -> int:
    return 6 if remaining_dice == 0 else remaining_dice


def generate_sequences(n: int) -> tuple[tuple[Any]]:
    temp = (tuple(range(1, 7)) for _ in range(n))
    return tuple(product(*temp))


if __name__ == "__main__":
    cache()

    p_banking = p_winning_from_banking(
        0,
        0,
        6,
        0
    )

    print(p_banking)
