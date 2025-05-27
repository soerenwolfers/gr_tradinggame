from gr_tradinggame.manual import ManualGame

game = ManualGame(
    team_names=[
        'Watford',
        'Manchester',
        'Cambridge',
        'Edinburgh'
    ],
    max_rounds=5,
    cooldown=3,
    width=1000
)
