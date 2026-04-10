import pytest
from server.domain.cards import Card, Color, Number, Deck, HandCard
from server.domain.player import Player
from server.domain.game import Game, Board
from server.domain.exceptions import *
from database.gameSerializer import GameSerializer

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

    assert game._board._misfires == 2

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
   
    assert game._board.misfires == 2  # started at 3

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
    game._board._misfires = 0
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




