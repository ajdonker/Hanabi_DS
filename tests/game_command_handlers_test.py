from server.application.commands.game_commands import PlayCardCommand
from server.application.handlers.game_command_handlers import PlayCardHandler
from server.domain.cards import Card, Color, HandCard, Number
from server.domain.game import Game


class FakeGameRepository:
    def __init__(self, game):
        self.game = game
        self.saved_games = []
        self.deleted_player_game_mappings = []

    def load_game(self, game_id):
        return self.game

    def save_game(self, game):
        self.saved_games.append(game)

    def delete_player_game_mapping(self, player_id):
        self.deleted_player_game_mappings.append(player_id)


def test_play_card_deletes_player_game_mappings_when_game_is_over():
    game = Game._create_initial_game("g1", ["P1", "P2"])
    game.board.piles.update({
        Color.RED: 4,
        Color.YELLOW: 5,
        Color.GREEN: 5,
        Color.BLUE: 5,
        Color.WHITE: 5,
    })
    game.getPlayer("P1")._hand[0] = HandCard(Card(Number.FIVE, Color.RED))

    repo = FakeGameRepository(game)
    handler = PlayCardHandler(repo)

    events = handler.execute(PlayCardCommand("g1", "P1", 0))

    assert [event.event for event in events] == [
        "card_correct",
        "card_drawn",
        "game_over",
    ]
    assert repo.saved_games == [game]
    assert repo.deleted_player_game_mappings == ["P1", "P2"]
