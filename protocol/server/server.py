import socket, threading, json
from game_logic.state import GameState
from game_logic.cards import Color

HOST, PORT = '0.0.0.0', 12345
LOBBY_SIZE = 2  # number of players required to start. 

clients = []      # list of (conn, addr, name)
lobby_names = []  # track names until game starts
game = None # global variable. A single server process handles only 1 game instance. 
lock = threading.Lock()


def broadcast_state():
    """Send current game state to all connected clients."""
    payload = {
        "type": "STATE",
        "board": {c.name: v for c, v in game.board.items()},
        "tokens": game.tokens,
        "misfires": game.misfires,
        "deck_count": game.deck.get_deck_count(),
        "hands": [
            [ {"number": card.number, "color": card.color.name, "hints": ps.hints[idx]}
              for idx, card in enumerate(ps.hand) ]
            for ps in game.players
        ],
        "players": [name for (_, _, name) in clients],
        "current_turn": game.current_turn
    }
    msg = json.dumps(payload) + "\n"
    for conn, _, _ in clients:
        try:
            conn.sendall(msg.encode())
        except Exception:
            pass


def handle_client(conn, addr):
    ''' After accepting client socket (conn,addr), wraps it so that it can read lines as a file.
    Let LOBBY_SIZE players join before creating game instance. Loop until game ends, accepting 
    messages and composing proper move to be done in the BoardState object.
    '''
    global game
    conn_file = conn.makefile('r')

    # Receive JOIN
    line = conn_file.readline()
    if not line:
        conn.close()
        return
    join = json.loads(line)
    name = join.get("player")

    with lock:
        idx = len(clients)
        clients.append((conn, addr, name))
        if game is None:
            # still in lobby phase
            lobby_names.append(name)
            # assign idx and inform client
            conn.sendall((json.dumps({"type": "ASSIGN_IDX", "idx": idx}) + "\n").encode())
            # start game when lobby full
            if len(lobby_names) == LOBBY_SIZE:
                game = GameState(lobby_names)
                # broadcast initial state
                broadcast_state()
        else:
            # game already started: reject or assign new spectator idx
            conn.sendall((json.dumps({"type": "ERROR", "msg": "Game already in progress"}) + "\n").encode())
            conn.close()
            return

    # Main loop: only after game started
    while True:
        line = conn_file.readline()
        if not line:break
        msg = json.loads(line)
        with lock:
            try:
                if msg.get("type") == "PLAY":
                    game.play_card(msg["player_idx"], msg["card_idx"])
                elif msg.get("type") == "HINT":
                    if "color" in msg:
                        game.give_hint(
                            msg["from"],
                            msg["to"],
                            color=Color[msg["color"]]
                        )
                    elif "number" in msg:
                        game.give_hint(
                            msg["from"],
                            msg["to"],
                            number=msg["number"]
                        )
                elif msg.get("type") == "DISC":
                    game.discard(msg["player_idx"], msg["card_idx"])
                broadcast_state()
            except Exception as e:
                conn.sendall((json.dumps({"type": "ERROR", "msg": str(e)}) + "\n").encode())

    # cleanup on disconnect - close all wrapped sockets
    with lock:
        clients[:] = [c for c in clients if c[0] != conn]
    conn_file.close()
    conn.close()
def main():
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}, waiting for {LOBBY_SIZE} players...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()