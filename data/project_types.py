from data import builder

with builder.build() as bld:
    event = bld.label_type("Event")
    button = bld.label_type("Button")
    container = bld.label_type("Container")

    game = bld.project_type("Game")
    cards = bld.project_type("Cards")

    card_game = game.add_child("Card Game")
    card_game.add_component(cards)

    poker = card_game.add_child("Poker")

    # state label where instances can be (active, inactive, ...)
    state_label = game.add_label("State", event)
    #label where instances are (bet, call, fold, ...)
    action_label = game.add_label("Action", event)
    # button action label instances are (bet, call, fold, ...)
    button_action_label = game.add_label("Action", button)

    card_label = cards.add_label("Card", container)
    rank_label = cards.add_label("Rank", container, 13)
    suit_label = cards.add_label("Suit", container, 4)

    card_label.add_component(rank_label)
    card_label.add_component(suit_label)

    poker_button = poker.add_label("Button", container)

    position = poker.add_label("Position", container)

    board_label = poker.add_label("Board", container, 1)

    board_label.add_component(card_label)

    opponent = poker.add_label("Opponent", container)

    opponent.add_component(card_label)
    opponent.add_component(action_label)
    opponent.add_component(state_label)
    opponent.add_component(poker_button)
    opponent.add_component(position)

    player = card_game.add_label("Player", container, 1)

    player.add_component(card_label)
    player.add_component(button_action_label)
    player.add_component(poker_button)
    player.add_component(position)