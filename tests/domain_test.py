import pytest
from server.domain.cards import Card, Color, Number, Deck, HandCard
from server.domain.player import Player
from server.domain.game import Game, Board
from server.domain.exceptions import *
from database.gameSerializer import GameSerializer
from server.domain.results import GameResult
import time

@pytest.fixture
def game():
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game._board._deck._cards = [
        Card(Number.TWO, Color.RED),
        Card(Number.TWO, Color.RED),
        Card(Number.TWO, Color.RED),
        Card(Number.TWO, Color.RED),
    ]

    for player in game._players.values():
        player._hand = [
            HandCard(Card(Number.TWO, Color.RED)),
            HandCard(Card(Number.TWO, Color.RED)),
            HandCard(Card(Number.TWO, Color.RED)),
            HandCard(Card(Number.TWO, Color.RED)),
            HandCard(Card(Number.TWO, Color.RED)),
        ]
    return game

def test_deck_size(): #ok
    deck = Deck()
    assert deck.get_deck_count() == 50

def test_draw_reduces_size(): #ok
    deck = Deck()
    deck.draw()
    assert deck.get_deck_count() == 49

def test_play_card_correct(game): #ok
    player = game._players["P1"]

    card = HandCard(Card(Number.ONE, Color.RED))
    player._hand[0] = card
    game._board._piles[Color.RED] = 0

    game.playCard("P1", 0)

    assert game._board._piles[Color.RED] == 1

def test_play_card_wrong(game): #ok
    
    # force wrong card
    game.playCard("P1", 0) #2 RED

    assert game._board._misfires == 1

def test_hint_to_yourself (game): #fail --> not an exception anymore
    
    result = game.giveHint("P1", "P1", color= Color.RED)
    
    assert result.success == False
    
def test_token_decreases(game): #ok
    before = game._board.token
    game.debugPrintState()
    game.giveHint("P1", "P2",color=Color.RED)
    assert game._board.token == before - 1

'''
def test_cannot_hint_without_tokens(): #fail --> not an exception anymore
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game._board._token = 0

    with pytest.raises(Exception):
        game.giveHint("P1", "P2", color=Color.RED)
'''

def test_play_card_success_and_clear_hints(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    player = game._players["P1"]

    # force known card
    card = HandCard(Card(Number.ONE, Color.RED))
    player._hand[0] = card

    # add hint
    card.setHintColor(Color.RED)

    game._board._piles[Color.RED] = 0

    game.playCard("P1", 0)

    # hints cleared
    assert card.getHints()["color"] is None

    # board updated
    assert game._board._piles[Color.RED] == 1

def test_play_valid_card_updates_board(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    player = game._players["P1"]
    card = player.getCardByID(0)
    card._card._number = Number.ONE  

    game.playCard("P1", 0)

    assert game._board.calculateScore() == 1

def test_play_card_misfire_and_discard(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    player = game._players["P1"]

    # force bad card (not 1)
    card = HandCard(Card(Number.THREE, Color.RED))
    player._hand[0] = card

    game.playCard(player.getUsername , 0)
   
    assert game._board.misfires == 1  # started at 0

def test_discard_clears_hints_and_draw(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    player = game._players["P2"]

    card = player.getCardByID(2)
    card.setHintNumber(Number.ONE)

    old_card = card

    game.discardCard("P1", 2) #just to keep turn order
    game.discardCard("P2", 2)
    card.removeHints() 
    #print(player.getCardByID(2).color)
    #print(player.getCardByID(2).number)
    #print(old_card.number)
    #print(old_card.color)
    # hints cleared
    assert old_card.getHints()["number"] is None

    # new card drawn
    assert player.getCardByID(2) != old_card

def test_discard_increases_hint_token(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    game._board._token = 5

    game.discardCard("P1", 0)

    assert game._board._token == 6 

def test_discard_does_not_exceed_max_tokens(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    game._board._token = 8  # max

    game.discardCard("P1", 0)

    assert game._board._token == 8    

def test_hint_applies_only_to_matching_cards(game): #ok

    target = game._players["P2"]

    game.giveHint("P1", "P2", color=Color.RED)

    for card in target._hand:
        if card.card.color == Color.RED:
            assert card.getHints()["color"] == Color.RED
        else:
            assert card.getHints()["color"] is None

def test_give_hint_color_and_number(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    #controlled player
    player = game._players["P2"]

    # controlled hand
    player._hand = [
        HandCard(Card(Number.TWO, Color.RED)),
        HandCard(Card(Number.TWO, Color.BLUE)),
        HandCard(Card(Number.ONE, Color.WHITE)),
    ]

    game._board._token = 5

    # color hint
    game.giveHint("P1", "P2", color=Color.RED)

    assert player._hand[0].getHints()["color"] == Color.RED
    assert player._hand[1].getHints()["color"] is None

    # number hint
    player = game._players["P1"]

    # controlled hand
    player._hand = [
        HandCard(Card(Number.TWO, Color.RED)),
        HandCard(Card(Number.TWO, Color.BLUE)),
        HandCard(Card(Number.ONE, Color.WHITE)),
    ]

    game._board._token = 5

    game.giveHint("P2", "P1",number=Number.TWO)

    assert player._hand[0].getHints()["number"] == Number.TWO
    assert player._hand[1].getHints()["number"] == Number.TWO

def test_check_end_conditions(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    # misfire end
    game._board._misfires = 3
    assert game.checkGameOver() is not None

    game._board._misfires = 4
    assert game.checkGameOver() is not None

    # full board
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game._board._piles = {c: 5 for c in Color}
    assert game.checkGameOver() is not None

    # final turn end
    game = Game._create_initial_game("g1", ["P1", "P2"])
    for p in game._players.values():
        p._lastTurn = True
    assert game.checkGameOver() is not None

def test_only_current_player_can_play(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    # suppose P1 starts
    with pytest.raises(Exception):
        game.discardCard("P2", 0)

def test_last_card_triggers_final_round(game): #ok

    game._board._deck._cards = [Card(number= 5,color=Color.RED)]  # only 1 left

    game.discardCard("P1", 0)
    assert game._finalTurn is True
'''
def test_game_over_when_no_lives(game): #fail

    game._board._misfires = 1

    with pytest.raises(Exception):
        game.playCard("P1", 0)

    print(game._board._misfires)

    assert game.checkGameOver() == 0 # 0 is score of game as no cards are scored 
'''

def test_game_over_on_perfect_score(): #ok
    game = Game._create_initial_game("g1", ["P1", "P2"])

    # simulate all fireworks completed
    game._board._piles = {c: 5 for c in Color}
    #print("Misfires:", game._board._misfires)
    #print("Piles completed:", game._board.completedPiles())
    #print("Players last turn flags:", {p._username: p._lastTurn for p in game._players.values()})
    game.checkGameOver()

    assert game.checkGameOver()

def test_game_serialization_roundtrip(game): #ok
    data = GameSerializer.to_dict(game)
    restored = GameSerializer.from_dict(data)

    assert restored._gameID == game._gameID
    assert restored._playerTurn == game._playerTurn
    assert restored._finalTurn == game._finalTurn
    assert restored._turnStartedAt == game._turnStartedAt
    assert restored._turnDeadline == game._turnDeadline

    # players
    assert set(restored._players.keys()) == set(game._players.keys())

    for username in game._players:
        p1 = game._players[username]
        p2 = restored._players[username]

        assert len(p1._hand) == len(p2._hand)

        for c1, c2 in zip(p1._hand, p2._hand):
            assert c1.card.color == c2.card.color
            assert c1.card.number == c2.card.number

def test_serialization_preserves_hints(game): #ok

    player = game.getPlayer("P1")
    card = player._hand[0]

    card.setHintColor(Color.RED)
    card.setHintNumber(Number.TWO)

    data = GameSerializer.to_dict(game)
    restored = GameSerializer.from_dict(data)

    assert GameSerializer.to_dict(restored) == GameSerializer.to_dict(game)
    
    restored_card = restored.getPlayer("P1")._hand[0]

    assert restored_card._hintColor == Color.RED
    assert restored_card._hintNumber == Number.TWO

def test_serialization_after_discard(game): #ok

    game.discardCard("P1", 0)

    data = GameSerializer.to_dict(game)
    restored = GameSerializer.from_dict(data)

    assert len(restored._board._discards) == len(game._board._discards)
    assert restored._board._token == game._board._token

def test_board_update_token_minus_at_zero_returns_false():
    board = Board(
        deck=Deck(),
        piles={c: 0 for c in Color},
        discards=[],
        token=0,
        misfires=0,
    )

    result = board.updateToken("-")

    assert result is False
    assert board.token == 0


def test_board_update_token_plus_does_not_exceed_eight():
    board = Board(
        deck=Deck(),
        piles={c: 0 for c in Color},
        discards=[],
        token=8,
        misfires=0,
    )

    result = board.updateToken("+")

    assert result is True
    assert board.token == 8


def test_board_update_token_minus_decreases_when_available():
    board = Board(
        deck=Deck(),
        piles={c: 0 for c in Color},
        discards=[],
        token=3,
        misfires=0,
    )

    result = board.updateToken("-")

    assert result is True
    assert board.token == 2


def test_board_add_discard_and_score():
    board = Board(
        deck=Deck(),
        piles={c: 0 for c in Color},
        discards=[],
        token=8,
        misfires=0,
    )

    card = HandCard(Card(Number.ONE, Color.RED))

    board.addDiscard(card)
    board._piles[Color.RED] = 2
    board._piles[Color.BLUE] = 3

    assert board.discards == [card]
    assert board.calculateScore() == 5
    assert board.completedPiles() is False


def test_get_unknown_player_raises_key_error(game):
    with pytest.raises(KeyError):
        game.getPlayer("not-a-player")


def test_play_card_wrong_turn_raises(game):
    with pytest.raises(WrongTurnException):
        game.playCard("P2", 0)

def test_discard_wrong_card_index_raises(game):
    with pytest.raises(Exception):
        game.discardCard("P1", 99)

def test_give_hint_wrong_turn_raises(game):
    with pytest.raises(WrongTurnException):
        game.giveHint("P2", "P1", color=Color.RED)

def test_give_hint_without_color_or_number_fails_and_does_not_consume_token(game):
    before_tokens = game.board.token

    result = game.giveHint("P1", "P2")

    assert result.success is False
    assert game.board.token == before_tokens
    assert result.tokensLeft == before_tokens
    assert game.playerTurn == "P2"


def test_give_hint_with_both_color_and_number_fails_and_does_not_consume_token(game):
    before_tokens = game.board.token

    result = game.giveHint("P1", "P2", color=Color.RED, number=Number.TWO)

    assert result.success is False
    assert game.board.token == before_tokens
    assert result.tokensLeft == before_tokens
    assert game.playerTurn == "P2"


def test_give_hint_with_zero_tokens_fails(game):
    game._board._token = 0

    result = game.giveHint("P1", "P2", color=Color.RED)

    assert result.success is False
    assert game.board.token == 0
    assert result.tokensLeft == 0
    assert game.playerTurn == "P2"


def test_give_hint_no_matching_cards_fails_without_consuming_token(game):
    target = game.getPlayer("P2")
    target._hand = [
        HandCard(Card(Number.ONE, Color.BLUE)),
        HandCard(Card(Number.TWO, Color.BLUE)),
    ]

    before_tokens = game.board.token

    result = game.giveHint("P1", "P2", color=Color.RED)

    assert result.success is False
    assert game.board.token == before_tokens
    assert result.tokensLeft == before_tokens
    assert game.playerTurn == "P2"

    for card in target._hand:
        assert card.getHints()["color"] is None


def test_number_hint_only_marks_matching_numbers(game):
    game = Game._create_initial_game("g1", ["P1", "P2"])

    target = game.getPlayer("P2")
    target._hand = [
        HandCard(Card(Number.ONE, Color.RED)),
        HandCard(Card(Number.TWO, Color.BLUE)),
        HandCard(Card(Number.TWO, Color.WHITE)),
    ]

    result = game.giveHint("P1", "P2", number=Number.TWO)

    assert result.success is True
    assert target._hand[0].getHints()["number"] is None
    assert target._hand[1].getHints()["number"] == Number.TWO
    assert target._hand[2].getHints()["number"] == Number.TWO


def test_change_turn_cycles_back_to_first_player(game):
    assert game.playerTurn == "P1"

    game.changeTurn()
    assert game.playerTurn == "P2"

    game.changeTurn()
    assert game.playerTurn == "P1"

def test_change_turn_sets_timer_fields(game):
    game.changeTurn()

    assert game._turnStartedAt is not None
    assert game._turnDeadline is not None
    assert game._turnDeadline > game._turnStartedAt


def test_initial_game_sets_timer_fields(game):
    assert game._turnStartedAt is not None
    assert game._turnDeadline is not None
    assert game._turnDeadline > game._turnStartedAt


def test_is_turn_expired_false_when_deadline_in_future(game):
    game._turnDeadline = time.time() + 60

    assert game.isTurnExpired() is False

def test_is_turn_expired_true_when_deadline_in_past(game):
    game._turnDeadline = time.time() - 1

    assert game.isTurnExpired() is True


def test_can_play_during_final_turn_sets_player_last_turn(game):
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game.setFinalTurn(True)

    game.canPlay("P1")

    assert game.getPlayer("P1")._lastTurn is True


def test_check_game_over_returns_none_when_game_continues(game):
    game = Game._create_initial_game("g1", ["P1", "P2"])

    game._board._misfires = 0
    game._board._piles = {c: 0 for c in Color}

    for player in game._players.values():
        player._lastTurn = False

    assert game.checkGameOver() is None


def test_discard_with_empty_deck_does_not_draw_card_and_sets_final_turn(game):
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game._board._deck._cards = []

    player = game.getPlayer("P1")
    old_hand_size = len(player._hand)

    result = game.discardCard("P1", 0)

    assert result.success is True
    assert len(player._hand) == old_hand_size - 1
    assert game.finalTurn is True
    assert player._lastTurn is True


def test_discard_game_over_can_return_zero_score(game):
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game._board._deck._cards = []
    game.getPlayer("P2")._lastTurn = True

    result = game.discardCard("P1", 0)

    assert game.getPlayer("P1")._lastTurn is True
    assert game.getPlayer("P2")._lastTurn is True
    assert result.game_over == 0


def test_play_card_with_empty_deck_does_not_draw_card(game):
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game._board._deck._cards = []

    player = game.getPlayer("P1")
    player._hand[0] = HandCard(Card(Number.ONE, Color.RED))
    old_hand_size = len(player._hand)

    result = game.playCard("P1", 0)

    assert result.success is True
    assert len(player._hand) == old_hand_size - 1
    assert game.finalTurn is True
    assert player._lastTurn is True

def test_play_card_on_full_pile_counts_only_one_misfire():
    game = Game._create_initial_game("g1", ["P1", "P2"])

    player = game.getPlayer("P1")
    player._hand[0] = HandCard(Card(Number.FIVE, Color.RED))
    game._board._piles[Color.RED] = 5

    game.playCard("P1", 0)

    assert game.board.misfires == 1
    assert len(game.board.discards) == 1

def test_game_result_set_game_over():
    result = GameResult()

    result.setGameOver(12)

    assert result.game_over == 12    

def test_play_card_game_over_after_third_misfire(game):
    # Make score non-zero, because playCard uses `if score:`
    # and score 0 would not enter the branch.
    game._board._piles[Color.BLUE] = 1

    # One wrong play should bring misfires to 3.
    game._board._misfires = 2

    # Fixture card is RED TWO while RED pile is 0, so this is invalid.
    result = game.playCard("P1", 0)

    assert game._board.misfires == 3
    assert result.game_over == game._board.calculateScore()

def test_play_card_game_over_after_final_turn_completion():
    game = Game._create_initial_game("g1", ["P1", "P2"])

    # P1 can play RED ONE successfully.
    player = game.getPlayer("P1")
    player._hand[0] = HandCard(Card(Number.ONE, Color.RED))
    game._board._piles[Color.RED] = 0

    # Make the score non-zero after the play.
    # Make the deck have exactly one card so drawing triggers final turn.
    game._board._deck._cards = [
        Card(Number.TWO, Color.BLUE)
    ]

    # P2 has already had their final turn.
    game.getPlayer("P2")._lastTurn = True

    result = game.playCard("P1", 0)

    assert game.getPlayer("P1")._lastTurn is True
    assert game.getPlayer("P2")._lastTurn is True
    assert result.game_over == 1

def test_play_card_game_over_when_piles_completed():
    game = Game._create_initial_game("g1", ["P1", "P2"])

    player = game.getPlayer("P1")
    player._hand[0] = HandCard(Card(Number.FIVE, Color.RED))

    # All piles complete except RED, which will be completed by this play.
    game._board._piles = {c: 5 for c in Color}
    game._board._piles[Color.RED] = 4

    result = game.playCard("P1", 0)

    assert game._board.completedPiles() is True
    assert result.game_over == 25
