class Game:
    def __init__(self, candidates, max_rounds, cooldown, frequency=0.3, width=500, length=10):
        self.teams = []
        self.scores = dict()
        self.candidates = candidates
        self.frequency = frequency
        self.width = width
        self.max_rounds = max_rounds
        self.last_cooldown = cooldown
        self.last_update = -2**31
        self.start = timeit.default_timer()
        self.length = length
        self.stop_request = False
        self.started = False
        self.gen = np.random.default_rng(seed=None)
        self.initialize_ui()
        
    def initialize_ui(self):
        self.current_round = 0
        self.team_scores = {team: [0] for team in self.candidates}
        self.team_blocked_until = {team: -1 for team in self.candidates}
        self.last_number = None
        self.output = widgets.Output()
        self.plot_output = widgets.Output(layout=dict(width='100%'))
        self.game_ui = widgets.HBox(
            [self.output, self.plot_output],
            layout=widgets.Layout(
                align_items='center',
                justify_content='center', 
                border='solid 1px gray',
                width='100%'
            )
        )
        top_spacer = widgets.Box(layout=widgets.Layout(flex='1 1 auto'))
        bottom_spacer = widgets.Box(layout=widgets.Layout(flex='1 1 auto'))
        self.vertical_box = widgets.VBox(
            [top_spacer, self.game_ui, bottom_spacer],
            layout=widgets.Layout(
                height='100vh',
                display='flex',
                flex_flow='column',
                align_items='center',
                justify_content='center',
            )
        )

        self.update_plot()
    
    def update_plot(self):
        fig = go.Figure()
        for team in self.candidates:
            n = self.current_round
            step = int(n / 100 + 1)
            fig.add_trace(go.Scatter(
                x=list(range(self.current_round + 1))[::step],
                y=self.team_scores[team][::step],
                mode='lines',
                name=team
            ))
        fig.update_layout(xaxis_title='Round', yaxis_title='Score', xaxis_range=[0, self.max_rounds], width=self.width)
        with self.plot_output:
            clear_output(wait=True)
            display(fig)
    
    def start_new_round(self):
        self.current_round += 1
        self.last_number = self.gen.pareto(3)
        
    def loop(self):
        with self.output:
            while self.current_round < self.max_rounds and not self.stop_request:
                self.start_new_round()
                eliminate = []
                for team, btn in self.candidates.items():
                    args = (self.last_number, self.last_cooldown, self.current_round, self.max_rounds, self.team_scores[team][-1], [y[-1] for (x, y) in self.team_scores.items() if x != team])
                    tic_team = timeit.default_timer()
                    took_action = btn(*args) and self.current_round > self.team_blocked_until[team] 
                    toc_team = timeit.default_timer()
                    if toc_team - tic_team > self.length / self.max_rounds / 10:
                        eliminate.append(team)
                    score = self.last_number if took_action else 0
                    self.team_scores[team].append(self.team_scores[team][-1] + score)
                    if took_action:
                        self.team_blocked_until[team] = self.current_round + self.last_cooldown
                for x in eliminate:
                    del self.candidates[x]
                toc = timeit.default_timer()
                target = self.start + self.current_round / self.max_rounds * self.length
                if toc < target:
                    time.sleep(target - toc)
                if toc > self.last_update + self.frequency:
                    self.last_update = toc
                    self.update_plot()
                    
            self.update_plot()
            df = (
                pd.DataFrame(
                    {x: self.team_scores[x][-1] for x in self.team_scores}.items(), 
                    columns=['Name', 'Score']
                )
                .sort_values('Score', ascending=False)
                .reset_index(drop=True)
                .rename(index=lambda x: x + 1)
                .round(2)
            )
            display(df)
                
    def play(self):
        self.loop()
        
    def _ipython_display_(self):
        display(self.vertical_box)

game = Game(candidates={
    'Watford': lambda *x: foo(*x, threshold=0.1), 
    'Manchester': lambda *x: foo(*x, threshold=0.5), 
    'Cambridge': lambda *x: foo(*x, threshold=0), 
    'Edinburgh':foo 
}, max_rounds = 2000, cooldown=3, width=500, length=10)

game = Game(candidates={
    'Watford': foo, 
    'Manchester': foo, 
    'Cambridge': foo, 
    'Edinburgh':foo 
}, max_rounds = 20000, cooldown=3, width=500, length=30)
game.play()
