import socket, json, threading

#HOST, PORT = '0.0.0.0', 12345
#MATCHMAKER_HOST, MATCHMAKER_PORT = "127.0.0.1",9000
class Client:
    def __init__(self,name,matchmaker_host="127.0.0.1",matchmaker_port=9000):
        '''First connect to matchmaker. Get server assigned. Then create file like reader from server msgs.'''
        self.sock = None
        self.matchmaker_host = matchmaker_host
        self.matchmaker_port = matchmaker_port
        self.sock_file = None
        self.idx = None
        self.last_state = None
        self.game_started = False
        self.current_turn = None
        self.game_id = None
        #name = input("Your name> ").strip()
        self.name = name
        # can add comms here to reject client name if it is not unique 
        
    def start(self):
        assignment = self.get_startup_assignment(self.name)
        print("Match found:", assignment)
        self.game_id = assignment["game_id"]
        self.connect_to_game_server(
            assignment["host"],
            assignment["port"],
            assignment["game_id"],
            self.name
        )
    def get_match_assignment(self, name):
        sock = socket.socket()
        sock.connect((self.matchmaker_host, self.matchmaker_port))
        sock_file = sock.makefile("r")
        msg = {"type": "JOIN_QUEUE", "player": name}
        sock.sendall((json.dumps(msg) + "\n").encode())
        print("Msg to conn sent to matchmaker")
        while True:
            line = sock_file.readline()
            if not line:
                raise Exception("Matchmaker disconnected")
            reply = json.loads(line)

            if reply["type"] == "WAITING":
                print(reply["msg"])
                continue
            elif reply["type"] == "MATCH_FOUND":
                print("Match found from matchmaker:", reply)
                sock.close()
                return reply
            elif reply["type"] == "ERROR":
                raise Exception(reply["msg"])
            
    def get_startup_assignment(self, name):
        try:
            reply = self.try_resume_by_player(name)
            print("[CLIENT] active game found, resuming...")
            self.game_id = reply["game_id"]
            return reply
        except Exception:
            print("[CLIENT] no active game found, joining queue...")
            reply = self.get_match_assignment(name)
            self.game_id = reply["game_id"]
            return reply
        
    def try_resume_by_player(self, name):
        sock = socket.socket()
        sock.connect((self.matchmaker_host, self.matchmaker_port))
        sock_file = sock.makefile("r")
        msg = {
            "type": "RESUME_GAME",
            "player": name
        }
        sock.sendall((json.dumps(msg) + "\n").encode())

        line = sock_file.readline()
        if not line:
            sock_file.close()
            sock.close()
            raise Exception("Matchmaker disconnected")

        reply = json.loads(line)
        sock_file.close()
        sock.close()

        if reply["type"] == "ERROR":
            raise Exception(reply["msg"])

        return reply
    
    def connect_to_game_server(self, host, port, game_id, name):
        print(f"[CLIENT] connecting to game server at {host}:{port} for game {game_id}")
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.sock_file = self.sock.makefile("r")
        print("[CLIENT] connected to game server")
        if self.idx is not None:
            join_msg = {
                "type": "RESUME_GAME",
            "player": name,
            "game_id": game_id,
            #"idx": self.idx
            }
        else:
            join_msg = {
                "type": "JOIN_GAME",
                "player": name,
                "game_id": game_id
            }
        print(f"[CLIENT] sending join: {join_msg}")
        self.sock.sendall((json.dumps(join_msg) + "\n").encode())

        threading.Thread(target=self.receive_loop, daemon=True).start()

    def process_server_message(self,msg):
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

    def receive_loop(self):
        while True:
            line = self.sock_file.readline()
            if not line:
                print("Connection closed by server.")
                self.handle_disconnect()
                break
            msg = json.loads(line)
            self.process_server_message(msg)
            

    def handle_state(self, state):
        ''' Prints received state and prompts for action if neccessary'''
        self.last_state = state
        self.current_turn = state.get("current_turn")
        print("--- Game State ---")
        print("Board:", state.get("board"))
        print("Tokens:", state.get("tokens"), "Misfires:", state.get("misfires"))
        for i, hand in enumerate(state.get("hands", [])):
            if i == self.idx:
                # Show only the hints for your own cards
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

    def handle_disconnect(self):
        '''Attempt to get new host/port server info from matchmaker then reconnect.'''
        print("[CLIENT] attempting reconnect via matchmaker...")
        try:
            if self.sock_file:
                try:
                    self.sock_file.close()
                except:
                    pass
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
            assignment = self.get_game_location(self.name, self.game_id)
            print("[CLIENT] reconnect assignment:", assignment)

            self.game_started = True  # it was already in progress
            self.connect_to_game_server(
                assignment["host"],
                assignment["port"],
                assignment["game_id"],
                self.name
            )
        except Exception as e:
            print("[CLIENT] reconnect failed:", e)

    def get_game_location(self, name, game_id):
        '''Request host/port information from matchmaker'''
        sock = socket.socket()
        sock.connect((self.matchmaker_host, self.matchmaker_port))
        sock_file = sock.makefile("r")

        msg = {
            "type": "RESUME_GAME",
            "player": name,
            "game_id": game_id
        }
        sock.sendall((json.dumps(msg) + "\n").encode())

        line = sock_file.readline()
        if not line:
            raise Exception("Matchmaker disconnected during resume")

        reply = json.loads(line)
        sock_file.close()
        sock.close()

        if reply["type"] == "ERROR":
            raise Exception(reply["msg"])

        return reply
    
    def prompt_action(self):
        while True:
            cmd = input("Your move (PLAY idx / HINT p val / DISC idx): ").strip()
            try:
                msg = self.process_command(cmd)
                self.sock.sendall((json.dumps(msg) + "\n").encode())
                return
            except ValueError as e:
                print(e)            

    def process_command(self,cmd):
        parts = cmd.strip().split()
        if not parts:
            raise ValueError("Empty command—try again")
        action = parts[0].upper()

        if action == "PLAY":
            if len(parts) != 2 or not parts[1].isdigit():
                raise ValueError("Usage: PLAY <card_idx>")
            return {
                "type": "PLAY",
                "player_idx": self.idx,
                "card_idx": int(parts[1])
            }

        elif action == "DISC":
            if len(parts) != 2 or not parts[1].isdigit():
                raise ValueError("Usage: DISC <card_idx>")
            return {
                "type": "DISC",
                "player_idx": self.idx,
                "card_idx": int(parts[1])
            }

        elif action == "HINT":
            if len(parts) != 3:
                raise ValueError("Usage: HINT <player_idx> <color|number>")

            target_str, val = parts[1], parts[2]
            if not target_str.isdigit():
                raise ValueError("Second argument must be the target player index.")

            target = int(target_str)

            if val.isdigit():
                return {
                    "type": "HINT",
                    "from": self.idx,
                    "to": target,
                    "number": int(val)
                }
            else:
                return {
                    "type": "HINT",
                    "from": self.idx,
                    "to": target,
                    "color": val.upper()
                }

        raise ValueError("Unknown command. Use PLAY, DISC, or HINT.")


if __name__ == "__main__":
    name = input("Your name> ").strip()
    client = Client(name)
    client.start()
    threading.Event().wait()
