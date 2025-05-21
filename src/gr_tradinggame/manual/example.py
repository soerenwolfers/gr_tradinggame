from .manual_game import ManualGame

game = ManualGame(
    team_names=[
        'Watford',
        'Manchester',
        'Cambridge',
        'Edinburgh'
    ],
    max_rounds=3,
    cooldown=3,
    width=500
)
