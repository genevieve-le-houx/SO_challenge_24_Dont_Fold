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
    # Start highest combination to less
    # Royal flush
    royal_flush_possible = True
    straight_flush_possible = True

    first_suit: CardSuitEnum | None = None
    previous_rank_value: int | None = None

    occurences_of_rank: dict[CardRankEnum, int] = {}

    for i, card in enumerate(hand):
        if i == 0:
            first_suit = card.suit
            previous_rank_value = card.rank_value

        if card.rank not in occurences_of_rank:
            occurences_of_rank[card.rank] = 1
        else:
            occurences_of_rank[card.rank] += 1

        if card.rank not in (
            CardRankEnum.ten,
            CardRankEnum.jack,
            CardRankEnum.queen,
            CardRankEnum.king,
            CardRankEnum.ace,
        ):
            royal_flush_possible = False

        if i >= 1:
            if previous_rank_value + 1 != card.rank_value:
                royal_flush_possible = False
                straight_flush_possible = False

            if card.suit is not first_suit:
                royal_flush_possible = False
                straight_flush_possible = False

            previous_rank_value = card.rank_value

    if royal_flush_possible:
        # TODO confirm
        if (
            hand[0].rank == CardRankEnum.ten
            and hand[1].rank == CardRankEnum.jack
            and hand[2].rank == CardRankEnum.queen
            and hand[3].rank == CardRankEnum.king
            and hand[4].rank == CardRankEnum.ace
            and len(set(x.suit for x in hand)) == 1
        ):
            return "Royal Flush", 512

    if straight_flush_possible:
        if (
            hand[0].rank_value + 1 == hand[1].rank_value
            and hand[1].rank_value + 1 == hand[2].rank_value
            and hand[2].rank_value + 1 == hand[3].rank_value
            and hand[3].rank_value + 1 == hand[4].rank_value
            and len(set(x.suit for x in hand)) == 1
        ):

            return "Straight Flush", 256

    # Check for four of a kind
    if 4 in occurences_of_rank.values():
        return "Four of a Kind", 128

    # Check for full house
    if (
        3 in occurences_of_rank.values()
        and 2 in occurences_of_rank.values()
    ):
        return "Full House", 64


    # Check for flush
    set_suit = set()
    for card in hand:
        set_suit.add(card.suit)

    if len(set_suit) == 1:
        return "Flush", 32

    # Check for straight
    if (
        hand[0].rank_value + 1 == hand[1].rank_value
        and hand[1].rank_value + 1 == hand[2].rank_value
        and hand[2].rank_value + 1 == hand[3].rank_value
        and hand[3].rank_value + 1 == hand[4].rank_value
    ):
        return "Straight", 16

    # Check for three of a kind
    if 3 in occurences_of_rank.values():
        return "Three of a Kind", 8

    # Check for two pair or pair
    if 2 in occurences_of_rank.values():
        number_of_two = 0
        for rank, occurence in occurences_of_rank.items():
            if occurence == 2:
                number_of_two += 1

        if number_of_two == 1:
            return "Pair", 2
        elif number_of_two == 2:
            return "Two Pair", 4

    return "High Card", 1


def main():
    list_hands = read_data(Path("data.json"))

    total_points = 0
    for hand in list_hands:
        hand_name, highest_point = find_highest_point(hand)
        total_points += highest_point

    print(total_points)


if __name__ == "__main__":
    main()
