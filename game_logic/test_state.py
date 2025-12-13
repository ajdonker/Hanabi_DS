import pytest
from cards import Deck, Card, Color
from state import GameState


def test_deck_count_and_draw():
    deck = Deck()
    # total cards: 5 colors * (3+2+2+2+1) = 5*10 = 50
    assert deck.get_deck_count() == 50
    drawn = [deck.draw() for _ in range(50)]
    assert all(isinstance(c, Card) for c in drawn)
    assert deck.get_deck_count() == 0
    assert deck.draw() is None


def test_play_card_success_and_clear_hints():
    gs = GameState(["P1", "P2"])
    # force a known card in P1 hand
    gs.players[0].hand[0] = Card(1, Color.RED)
    # give a hint on that slot first
    gs.players[0].hints[0].append('RED')
    success = gs.play_card(0, 0)
    assert success is True
    # hint cleared
    assert gs.players[0].hints[0] == []
    assert gs.board[Color.RED] == 1


def test_play_card_misfire_and_discard():
    gs = GameState(["P1", "P2"])
    # find a card that will misfire (number > 1)
    idx = next(i for i,c in enumerate(gs.players[0].hand) if c.number != 1)
    misfire = gs.play_card(0, idx)
    assert misfire is False
    assert gs.misfires == 1
    # discarded card moved to discards
    assert isinstance(gs.discards[-1], Card)


def test_discard_clears_hints_and_draw():
    gs = GameState(["P1", "P2"])
    # set up hint at slot
    gs.players[1].hints[2].append('1')
    old = gs.players[1].hand[2]
    gs.discard(1, 2)
    assert gs.players[1].hints[2] == []
    assert gs.players[1].hand[2] != old


def test_give_hint_color_and_number():
    gs = GameState(["P1", "P2"])
    # controlled hand: only slot 0 is RED, slot 1 is BLUE, others white
    hand_size = len(gs.players[1].hand)
    controlled_hand = [Card(2, Color.RED), Card(2, Color.BLUE)] + [Card(1, Color.WHITE) for _ in range(hand_size - 2)]
    gs.players[1].hand = controlled_hand
    gs.players[1].hints = [[] for _ in range(hand_size)]
    gs.tokens = 5
    # RED hint
    gs.give_hint(0, 1, color=Color.RED)
    assert gs.players[1].hints[0] == ['RED']
    for idx in range(1, hand_size):
        assert 'RED' not in gs.players[1].hints[idx]
    # number hint
    gs.give_hint(0, 1, number=2)
    assert '2' in gs.players[1].hints[0]
    assert '2' in gs.players[1].hints[1]


def test_check_end_conditions():
    # misfire end
    gs = GameState(["P1", "P2"])
    gs.misfires = 3
    assert gs.check_end() is True
    # full board end
    gs = GameState(["P1", "P2"])
    gs.board = {c:5 for c in Color}
    assert gs.check_end() is True
    # empty deck end
    gs = GameState(["P1", "P2"])
    gs.deck.cards = []
    gs.deck.deck_count = 0
    assert gs.check_end() is True


def test_serialize_state_structure():
    gs = GameState(["P1", "P2"])
    snap = gs.serialize_state()
    assert set(snap.keys()) == {'board', 'tokens', 'misfires', 'deck_count', 'hands', 'current_turn'}
    assert isinstance(snap['hands'], list)
    assert len(snap['hands']) == 2

if __name__ == '__main__':
    pytest.main()
