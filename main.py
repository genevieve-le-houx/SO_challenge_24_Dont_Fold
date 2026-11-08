import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CardSuitEnum(Enum):
    hearts = "Hearts"
    diamonds = "Diamonds"
    clubs = "Clubs"
    spades = "Spades"

class CardRankEnum(Enum):
    two = "two"
    three = "three"
    four = "four"
    five = "five"
    six = "six"
    seven = "seven"
    eight = "eight"
    nine = "nine"
    ten = "ten"
    jack = "Jack"
    queen = "Queen"
    king = "King"
    ace = "Ace"


list_rank = [x for x in CardRankEnum]


@dataclass
class Card:
    suit: CardSuitEnum
    rank: CardRankEnum

    @property
    def rank_value(self) -> int:
        return list_rank.index(self.rank)

    # eq, le based on rank
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            raise TypeError("Must be of type Card")

        return self.rank == other.rank

    def __lt__(self, other):
        if not isinstance(other, Card):
            raise TypeError("Must be of type Card")

        return self.rank_value < other.rank_value

    def same_suit(self, other: Card) -> bool:
        return self.suit == other.suit


def read_data(filename: Path) -> list[tuple[Card, Card, Card, Card, Card]]:
    with open(filename, "r") as file:
        data = json.load(file)

    list_hands: list[tuple[Card, Card, Card, Card, Card]] = []

    for data_hand in data["poker_hands"]:
        hand = []
        for card in data_hand["cards"]:
            suit = CardSuitEnum(card["suit"])
            rank = CardRankEnum(card["rank"])
            hand.append(Card(suit, rank))

        hand.sort()
        list_hands.append(tuple(hand))

    return list_hands


def find_highest_point(hand: tuple[Card, Card, Card, Card, Card]) -> tuple[str, int]:
    first_suit: CardSuitEnum | None = None
    previous_rank_value: int | None = None

    occurrences_of_suit = {
        x: 0 for x in CardSuitEnum
    }
    occurrences_of_rank = {
        x: 0 for x in CardRankEnum
    }

    for i, card in enumerate(hand):
        occurrences_of_suit[card.suit] += 1
        occurrences_of_rank[card.rank] += 1

    # Check for royal flush
    if 5 in occurrences_of_suit.values():
        if (
            occurrences_of_rank[CardRankEnum.ten] == 1
            and occurrences_of_rank[CardRankEnum.jack] == 1
            and occurrences_of_rank[CardRankEnum.queen] == 1
            and occurrences_of_rank[CardRankEnum.king] == 1
            and occurrences_of_rank[CardRankEnum.ace] == 1
        ):
            return "Royal Flush", 512

        # Check for Straight Flush
        list_ranks = [x for x, value in occurrences_of_rank.items() if value == 1]
        list_ranks_value = [list_rank.index(x) for x in list_ranks]
        if (
            list_ranks_value[0] + 1 == list_ranks_value[1]
            and list_ranks_value[1] + 1 == list_ranks_value[2]
            and list_ranks_value[2] + 1 == list_ranks_value[3]
            and list_ranks_value[3] + 1 == list_ranks_value[4]
            and len(set(list_ranks)) == 5
        ):
            return "Straight Flush", 256

        # If did not return any yet. it is flush
        return "Flush", 32

    # Check for four of a kind
    if 4 in occurrences_of_rank.values():
        return "Four of a Kind", 128

    # Check for full house
    if (
        3 in occurrences_of_rank.values()
        and 2 in occurrences_of_rank.values()
    ):
        return "Full House", 64

    # Check for Straight
    list_ranks = [x for x, value in occurrences_of_rank.items() if value == 1]
    list_ranks_value = [list_rank.index(x) for x in list_ranks]
    if len(list_ranks_value) == 5:
        if (
            list_ranks_value[0] + 1 == list_ranks_value[1]
            and list_ranks_value[1] + 1 == list_ranks_value[2]
            and list_ranks_value[2] + 1 == list_ranks_value[3]
            and list_ranks_value[3] + 1 == list_ranks_value[4]
            and len(set(list_ranks)) == 5
        ):
            return "Straight", 16

    # Check for three of a kind
    if 3 in occurrences_of_rank.values():
        return "Three of a Kind", 8

    # Check for Two Pair or Pair
    pairs = [rank for rank, value in occurrences_of_rank.items() if value == 2]

    if len(pairs) == 1:
        return "Pair", 2
    elif len(pairs) == 2:
        return "Two Pair", 4

    return "High Card", 1


def main():
    list_hands = read_data(Path("data.json"))

    occurrence_of_hand_name = {
        "Royal Flush": 0,
        "Straight Flush": 0,
        "Four of a Kind": 0,
        "Full House": 0,
        "Flush": 0,
        "Straight": 0,
        "Three of a Kind": 0,
        "Two Pair": 0,
        "Pair": 0,
        "High Card": 0,
    }
    total_points = 0
    for hand in list_hands:
        hand_name, highest_point = find_highest_point(hand)
        occurrence_of_hand_name[hand_name] += 1
        total_points += highest_point

    print(occurrence_of_hand_name)
    print(total_points)


if __name__ == "__main__":
    main()
