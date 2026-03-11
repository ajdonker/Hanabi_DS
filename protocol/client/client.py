import socket, json, threading

HOST, PORT = 'localhost', 12345

class Client:
    def __init__(self):
        # Connect to server and create file-like reader
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.sock_file = self.sock.makefile('r')
        self.idx = None  # assigned by server in first message
        self.game_started = False

        # Start listener thread
        threading.Thread(target=self.receive_loop, daemon=True).start()

        # Send JOIN immediately after connecting
        name = input("Your name> ")
        join_msg = json.dumps({"type": "JOIN", "player": name}) + "\n"
        self.sock.sendall(join_msg.encode())

    def receive_loop(self):
        while True:
            line = self.sock_file.readline()
            if not line:
                print("Connection closed by server.")
                break
            msg = json.loads(line)
            msg_type = msg.get("type")
            if msg_type == "ASSIGN_IDX":
                self.idx = msg.get("idx")
                print(f"Assigned player index: {self.idx}")
            elif msg_type == "STATE":
                # First STATE marks game start
                if not self.game_started:
                    print("All players joined. Game is starting!\n")
                    self.game_started = True
                self.handle_state(msg)
            elif msg_type == "ERROR":
                print("Error from server:", msg.get("msg"))

    def handle_state(self, state):
        self.current_turn = state.get("current_turn")
        print("--- Game State ---")
        print("Board:", state.get("board"))
        print("Tokens:", state.get("tokens"), "Misfires:", state.get("misfires"))
        for i, hand in enumerate(state.get("hands", [])):
            if i == self.idx:
                # Show hints for your own cards
                display = []
                for card_info in hand:
                    # card_info is a dict with 'number','color','hints'
                    hints = card_info.get('hints', [])
                    display.append({'hints': hints})
                print(f"Player {i} (you): {display}")
            else:
                print(f"Player {i}: {hand}")
        print(f"Current turn: {self.current_turn}")
        # Prompt to play only on your turn
        if self.game_started and self.idx == self.current_turn:
            self.prompt_action()

    def prompt_action(self):
        cmd = input("Your move (PLAY idx / HINT p color / DISC idx): ")
        parts = cmd.split()
        if parts[0] == "PLAY":
            msg = {"type": "PLAY", "player_idx": self.idx, "card_idx": int(parts[1])}
        elif parts[0] == "HINT":
            target = int(parts[1]) # which player you hint at 
            # can be also bound checked whether it belongs in the bounds for play 
            val = parts[2]
            if val.isdigit():  # number hint
                msg = {"type": "HINT", "from": self.idx, "to": target, "number": int(val)}
            else:  # color hint
                msg = {"type": "HINT", "from": self.idx, "to": target, "color": val.upper()}
        elif parts[0] == "DISC":
            msg = {"type": "DISC", "player_idx": self.idx, "card_idx": int(parts[1])}
        else:
            print("Invalid command")
            return
        self.sock.sendall((json.dumps(msg) + "\n").encode())

if __name__ == "__main__":
    import threading
    client = Client()
    # keep the main thread alive
    threading.Event().wait()