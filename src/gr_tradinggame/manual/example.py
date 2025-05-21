from gr_tradinggame.manual import ManualGame

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
