#an interface for querying events and performing actions on window

#the client holds the game logic and makes specific queries
#clients could be cli clients or other apps.

class TH(object):
    def get_actions(self):
        #returns currently available actions => could be used to get the presets
        # ex: bet, ratio:1/2 of pot etc., etc.
        return

    def get_dealer(self):
        return

    def get_blinds(self):
        #get blinds
        return

    def get_players(self):
        #contains state, chips, name for each player, position, player_id, etc.
        return

    def get_chips(self, player_id):
        return

    def get_board_cards(self):
        return

    def get_pot(self):
        return

    def get_action(self, player_id):
        #should return the performed action (call, bet, raise etc. the amount associated
        # with it
        pass

    #perform action
    def perform_action(self, action):
        # action: action_name and amount
        return