from server.application.commands.game_commands import PlayCardCommand,DiscardCardCommand,GiveHintCommand
from server.application.commands.auth_commands import RegisterCommand,LoginCommand
from server.application.commands.lobby_commands import JoinLobbyCommand,CreateLobbyCommand
from server.presentation.command_message import CommandMessage
from server.domain.cards import Color, Number


class CommandFactory:
    def create(self, message: CommandMessage):
        if message.action == "game.play_card":
            return PlayCardCommand(
                game_id=message.data["gameId"],
                player_id=message.data["playerId"],
                card_index=message.data["cardIndex"],
            )

        if message.action == "game.discard_card":
            return DiscardCardCommand(
                game_id=message.data["gameId"],
                player_id=message.data["playerId"],
                card_index=message.data["cardIndex"],
            )

        if message.action == "game.give_hint":
            return GiveHintCommand(
                game_id=message.data["gameId"],
                from_player=message.data["fromPlayerId"],
                to_player=message.data["toPlayerId"],
                color=Color(message.data["color"]),
                number=Number(message.data["number"]),
            )
        
        if message.action == "player.register":
            return RegisterCommand(
                full_name=message.data["fullName"],
                email=message.data["email"],
                username=message.data["username"],
                password=message.data["password"],
            )

        if message.action == "player.login":
            return LoginCommand(
                username=message.data["username"],
                password=message.data["password"],
            )

        if message.action == "lobby.create":
            return CreateLobbyCommand(
                lobby_id=message.data["lobbyId"],
                max_users=message.data["maxUsers"],
                user_creator=message.data["userCreator"],
            )

        if message.action == "lobby.join":
            return JoinLobbyCommand(
                lobby_id=message.data["lobbyId"],
                user_joined=message.data["userJoined"],
            )

        raise ValueError(f"Unknown action: {message.action}")