from gscrap.data import builder

def build():
    with builder.build() as bld:
        if bld:
            event = bld.label_type("Event")
            button = bld.label_type("Button")
            container = bld.label_type("Container")

            game = bld.project_type("Game")
            cards = bld.project_type("Cards")

            # numbers = bld.project_type("Numbers")
            #
            # number = numbers.add_label("Number", container)
            #
            # number.add_instance("Fraction")
            # number.add_instance("Null") #no number

            card_game = game.add_child("Card Game")
            card_game.add_component(cards)

            poker = card_game.add_child("Poker")

            # state label where instances can be (active, inactive, ...)
            state_label = poker.add_label("PlayerState", event, capture=True, classifiable=True)

            state_label.add_instance("Active")
            state_label.add_instance("Inactive")
            state_label.add_instance("Seated")
            state_label.add_instance("Unseated")
            state_label.add_instance("Null")

            #label where instances are (bet, call, fold, ...)
            poker_action_label = poker.add_label("Action", event, classifiable=True)

            poker_action_label.add_instance("Call")
            poker_action_label.add_instance("Fold")
            poker_action_label.add_instance("Bet")
            poker_action_label.add_instance("All-In")
            poker_action_label.add_instance("Raise")
            poker_action_label.add_instance("Null") #no action

            poker_act_btn_lbl = poker.add_label("PlayerAction", button, classifiable=True)

            poker_act_btn_lbl.add_instance("Call")
            poker_act_btn_lbl.add_instance("Fold")
            poker_act_btn_lbl.add_instance("Bet")
            poker_act_btn_lbl.add_instance("All-In")
            poker_act_btn_lbl.add_instance("Raise")
            poker_act_btn_lbl.add_instance("Null")

            # poker_act_btn_lbl.add_component(poker_action_label)

            card_state = cards.add_label("CardState", event, 2, capture=True, classifiable=True)

            card_state.add_instance("Hidden")
            card_state.add_instance("Shown")
            card_state.add_instance("Null")

            card_label = cards.add_label("Card", container)
            rank_label = cards.add_label("Rank", container, 13, capture=True, classifiable=True)
            suit_label = cards.add_label("Suit", container, 4, capture=True, classifiable=True)

            rank_label.add_instance("A")
            rank_label.add_instance("K")
            rank_label.add_instance("Q")
            rank_label.add_instance("J")
            rank_label.add_instance("10")
            rank_label.add_instance("9")
            rank_label.add_instance("8")
            rank_label.add_instance("7")
            rank_label.add_instance("6")
            rank_label.add_instance("5")
            rank_label.add_instance("4")
            rank_label.add_instance("3")
            rank_label.add_instance("2")
            rank_label.add_instance("Null")

            suit_label.add_instance("Heart")
            suit_label.add_instance("Diamond")
            suit_label.add_instance("Spade")
            suit_label.add_instance("Club")
            suit_label.add_instance("Null")

            card_label.add_component(rank_label)
            card_label.add_component(suit_label)

            poker_button = poker.add_label(
                "Button",
                container,
                capture=True,
                classifiable=True
            )

            poker_button.add_instance("Dealer")
            poker_button.add_instance("SmallBlind")
            poker_button.add_instance("BigBlind")
            poker_button.add_instance("Null")

            position = poker.add_label("Position", container)

            board_label = poker.add_label("Board", container, True)

            board_label.add_component(card_label)

            opponent = poker.add_label("Opponent", container)

            opponent.add_component(card_label)
            opponent.add_component(poker_action_label)
            opponent.add_component(state_label)
            opponent.add_component(poker_button)
            opponent.add_component(position)

            player = card_game.add_label("Player", container, True)

            player.add_component(card_label)
            player.add_component(poker_act_btn_lbl)
            player.add_component(poker_button)
            player.add_component(position)
            player.add_component(state_label)