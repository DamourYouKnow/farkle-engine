import random
import os
from typing import Any, TypeAlias
from itertools import product, combinations, chain
from ast import literal_eval

# http://cs.gettysburg.edu/~tneller/papers/acg2017.pdf


Roll: TypeAlias = tuple[int]


# Lookup table for scoring sets of dice.
score_table: dict[Roll, int] = { # c
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

sequences: dict[int, tuple[Roll]] = dict()

scoring_combos: dict[Roll, dict[int, int]] = dict()


class Player:
    score: int = 0
    turn_score: int = 0
    roll: tuple[int] = []

    def roll(self):
        self.roll = roll(len(self.roll))

    def __repr__(self) -> str:
        pass


def cache():
    global sequences
    global scoring_combos

    print("Generating roll sequences cache...")

    # Pre-cache roll sequences
    sequences = {
        dice:generate_sequences(dice) for dice in range(1, 7)
    }

    cache_size = sum(len(values) for values in sequences.values())
    print(f"Cache size: {cache_size}")

    # Check if cache files exist.
    if os.path.isfile('cache.txt'):
        # Load from cache.
        with open('cache.txt', 'r') as cache_file:
            print("Loading scoring combinations cache...")
            cache = [
                line.strip().split('-') for line in cache_file.readlines()
            ]
            scoring_combos = { 
                literal_eval(split[0]) : literal_eval(split[-1]) for split in cache
            }

    # Cache file does not exist, generate and write.
    else:
        print("Generating scoring combinations cache...")
        
        scoring_combos = {
            roll:possible_scorings(roll) \
                for roll in chain(*sequences.values()) 
        }

        cache_size = sum(len(values) for values in scoring_combos.values())
        print(f"Cache size: {cache_size}")

        cache = [
            f"{str(roll)}-{str(combos)}\n" \
            for roll, combos in scoring_combos.items()
        ]

        with open("cache.txt", "w") as cache_file:
            cache_file.writelines(cache)


def roll(size: int) -> Roll:
    return (random.randint(1, 6) for _ in range(size))


def score(dice: list[int]) -> int:
    score = 0

    for combo, combo_score in score_table.items():
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
) -> float :
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
) -> float:
    p = 0
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
    roll: Roll # r
) -> float:
    combos = scoring_combos[roll].items()

    if not combos:
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
                for sn, sp in combos
        ])
        

# TODO: Avoid generating combinations that won't score.
def possible_scorings(roll: Roll) -> dict[int, int]:
    scorings: dict[int, int] = {}

    combos = list(
        chain.from_iterable(
            combinations(roll, n + 1) for n in range(len(roll))
        )
    )

    for combo in combos:
        combo_list = list(combo)
        combo_score = score(combo_list)
        dice_used =  len(combo) - len(combo_list)
        if combo_score > 0:
            if dice_used not in scorings or combo_score > scorings[dice_used]:
                scorings[dice_used] = combo_score

    return scorings


def hot_dice(remaining_dice: int) -> int:
    return 6 if remaining_dice == 0 else remaining_dice


def generate_sequences(n: int) -> tuple[int]:
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

