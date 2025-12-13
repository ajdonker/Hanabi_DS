from game_logic.cards import Card,Color,Deck
import json,uuid
'''
All of the game logic included in this file. Game state is created then managed here. 

'''
class PlayerState():
    def __init__(self,name:str,hand_size:int):
        self.name = name
        self.hand = [None]*hand_size
        self.hints = [[] for _ in range(hand_size)]  # append string data to these 
        # clear when that card is played / discarded 
    def clear_hints(self, card_idx: int):
        self.hints[card_idx] = [] # clear only that one which got discarded (not all)

class GameState():
    def __init__(self,player_names:list,game_id: str = None):
        self.game_id = game_id or str(uuid.uuid4())
        self.deck = Deck()
        self.deck.shuffle()
        self.players = [] # list of playerstate infos 
        hand_size = 4 if len(player_names) >= 4 else 5
        for name in player_names:
            ps = PlayerState(name,hand_size)
            for i in range(hand_size):
                ps.hand[i] = self.deck.draw()
            self.players.append(ps)
        self.board = {c:0 for c in Color} # dict Color -> number of cards in tower, all start at 0
        self.tokens = 8
        self.misfires = 0
        self.discards = []
        self.current_turn = 0 # mod player number will tell which player turn it is 
    @classmethod
    def from_serialized(cls, data: dict):
        # 1) Create an “empty” GameState with the same players + game_id
        gs = cls(data["player_names"], game_id=data["game_id"])
        
        # 2) Overwrite the board / tokens / misfires / turn / discards
        gs.board        = { Color[cname]: v for cname, v in data["board"].items() }
        gs.tokens       = data["tokens"]
        gs.misfires     = data["misfires"]
        gs.current_turn = data["current_turn"]
        gs.discards     = [
            Card(item["number"], Color[item["color"]])
            for item in data["discards"]
        ]
        
        # 3) Reconstruct each player’s hand & hints
        gs.players = []  # clear out the ones __init__ drew
        for name, hand_data in zip(data["player_names"], data["hands"]):
            ps = PlayerState(name, len(hand_data))
            for idx, card_info in enumerate(hand_data):
                # rebuild the Card
                num   = card_info["number"]
                col   = Color[card_info["color"]]
                card  = Card(num, col)
                ps.hand[idx] = card
                # rebuild the hints list
                ps.hints[idx] = list(card_info.get("hints", []))
            gs.players.append(ps)
        
        # 4) (Optionally) if you want the deck_count accurate
        #    You could create a dummy deck of the right size:
        # gs.deck = Deck()
        # gs.deck.cards = [None] * data["deck_count"]
        # gs.deck.deck_count = data["deck_count"]

        return gs
    def play_card(self,player_idx:int,card_idx:int) -> bool:
        ''' in : player id of player who does move and his card index (he doesnt know card).
        return true if card fits tower number and color. return false otherwise '''
        player = self.players[player_idx]
        card = player.hand[card_idx]
        # need to add checking if the tower for that color is full ? 
        top = self.board[card.color]
        success = False
        if card.number == top + 1:
            self.board[card.color] += 1 # if fitting, tower goes up
            success = True 
        else:
            self.discards.append(card) # card if discarded if it doesnt fit 
            self.misfires += 1
        # have to draw replacement in any case 
        player.clear_hints(card_idx) # clear hints for played card 
        player.hand[card_idx] = self.deck.draw()
        self.current_turn = (self.current_turn + 1) % len(self.players)
        return success
    def give_hint(self,from_player_idx:int,to_player_idx:int,color=None,number=None):
        if self.tokens == 0:
            raise RuntimeError("No hint tokens left")
        ps_to = self.players[to_player_idx]

        # color hint - tell him which cards have that color 
        if color is not None:
            for idx, card in enumerate(ps_to.hand):
                if card.color == color:
                    ps_to.hints[idx].append(color.name)

        # apply number hints - tell him which cards have that number 
        if number is not None:
            for idx, card in enumerate(ps_to.hand):
                if card.number == number:
                    ps_to.hints[idx].append(str(number))

        self.tokens -= 1
        self.current_turn = (self.current_turn + 1) % len(self.players)
    
    def discard(self,player_idx:int,card_idx:int):
        '''discard the card_d of player_id and draw another in its place. discarded should be shown. '''
        player = self.players[player_idx]
        card = player.hand[card_idx]
        self.discards.append(card)
        player.clear_hints(card_idx)
        self.tokens += 1
        player.hand[card_idx] = self.deck.draw()
        self.current_turn = (self.current_turn + 1) % len(self.players)
    
    def check_end(self) -> bool:
        ''' if 3 misfires are reached,
            or all 5 towers are built - 25 points 
            or deck is empty 
        '''
        if self.misfires >= 3:
            return True
        full = True
        for v in self.board.values(): # iterate values of the dict, if below 5, game not won
            if v < 5:
                full = False
                break
        if full:
            return True
        if self.deck.get_deck_count() == 0:
            return True
        return False
    def serialize_state(self):
        return {
            "game_id":    self.game_id,
            "player_names": [ps.name for ps in self.players],
            "board":      {c.name: v for c, v in self.board.items()},
            "tokens":     self.tokens,
            "misfires":   self.misfires,
            "deck_count": self.deck.get_deck_count(),
            "discards":   [ {"number":c.number, "color":c.color.name}
                            for c in self.discards ],
            "hands":      [
                [
                    {
                    "number":    card.number,
                    "color":     card.color.name,
                    "hints":     ps.hints[idx]
                    }
                    for idx,card in enumerate(ps.hand)
                ]
                for ps in self.players
            ],
            "current_turn": self.current_turn,
        }


