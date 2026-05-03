from server.domain.gameInterface import GameInterface
from server.domain.cards import Card,Color,Number,HandCard,Deck
from server.domain.player import Player
from server.domain.game import Game,Board

class GameSerializer:
    @staticmethod
    def from_dict(data: dict) -> Game:
        # --- players ---
        players = []
        for p_data in data["players"]:
            p = Player(p_data["username"])

            hand = []
            for c_data in p_data["hand"]:
                card = HandCard(
                    Card(
                        Number[c_data["number"]],
                        Color[c_data["color"]]
                        )
                )
                hints = c_data.get("hints", {})

                if hints.get("color"):
                    card.setHintColor(Color[hints["color"]])

                if hints.get("number"):
                    card.setHintNumber(Number[hints["number"]])

                hand.append(card)

            p.setHand(hand)
            p.setLastTurn(p_data.get("last_turn", False))
            players.append(p)

        # --- board ---
        board_data = data["board"]
        board = Board(
            deck=Deck.from_cards([
                Card(Number[d["number"]], Color[d["color"]])
                for d in board_data["deck"]
            ]),
            piles={Color[c]: v for c, v in board_data["piles"].items()},
            discards=[
                Card(Number[d["number"]], Color[d["color"]])
                for d in board_data["discards"]
            ],
            token=board_data["tokens"],
            misfires=board_data["misfires"]
        )

        # --- game ---
        game = Game(
            gameID=data["game_id"],
            board=board,
            players=players,
            playerTurn=data["player_turn"]
        )

        game.setFinalTurn(data["final_turn"])
        return game

    @staticmethod
    def to_dict(game: GameInterface) -> dict: 
            return {
                "game_id": game.gameID,
                "player_turn": game.playerTurn,
                "final_turn": game.finalTurn,

                "players": [
                    {
                        "username": p.getUsername,
                        "hand": [
                            {
                                "number": c.card.number.name,
                                "color": c.card.color.name,
                                "hints": {
                                    "color": c.color.name if c.hintColor else None,
                                    "number": c.number.name if c.hintNumber else None
                                }
                            }
                            for c in p.getHand
                        ],
                        "last_turn": p.getLastTurn()
                    }
                    for p in game.players.values()
                ],

                "board": {
                    "piles": {c.name: v for c, v in game.board.piles.items()},
                    "discards": [
                        {"number": c.number.name, "color": c.color.name}
                        for c in game.board._discards
                    ],
                    "deck": [
                        {"number": c.number.name, "color": c.color.name}
                        for c in game.board.deck.get_cards()
                    ],
                    "tokens": game.board.token,
                    "misfires": game.board.misfires,
                    "deck_count": game.board.deck.get_deck_count()
                }
            } 
