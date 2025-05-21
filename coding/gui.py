import timeit
import numpy as np
import ipywidgets as widgets
import plotly.graph_objects as go
import pandas as pd
from IPython.display import clear_output, display
import time
import json

from blackbox import generate_function


class CodingGame:
    def __init__(self, max_rounds, cooldown, frequency=0.3, width=1000, duration=10, functions=None, submissions=None):
        if functions is None and submissions is None:
            with open("submissions.json", "r") as f:
                submissions = json.load(f)
        self.candidates = functions if functions is not None else CodingGame.clean(submissions)
        self.frequency = frequency
        self.length = duration
        self.width = width
        self.last_cooldown = cooldown
        self.max_rounds = max_rounds
        self.init_play()
        self.initialize_ui()

    @staticmethod
    def clean(candidates):
        return {
            outer_key: generate_function(max(inner_dict.items(), key=lambda item: item[0])[1])
            for outer_key, inner_dict in candidates.items()
        }

    def initialize_ui(self):
        self.output = widgets.Output()
        self.plot_output = widgets.Output(layout=dict(width='100%'))
        self.game_ui = widgets.HBox(
            [self.output, self.plot_output],
            layout=widgets.Layout(
                align_items='center',
                justify_content='center',
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
                name=team,
            ))
        fig.update_layout(showlegend=True, xaxis_title='Round', yaxis_title='Score', xaxis_range=[0, self.max_rounds], width=self.width)
        with self.plot_output:
            clear_output(wait=True)
            display(fig)

    def start_new_round(self):
        self.current_round += 1
        self.last_number = self.gen.pareto(3)

    def loop(self):
        with self.output:
            while self.current_round < self.max_rounds:
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

    def init_play(self):
        self.gen = np.random.default_rng(seed=None)
        self.last_update = -2 ** 31
        self.team_scores = {team: [0] for team in self.candidates}
        self.team_blocked_until = {team: -1 for team in self.candidates}
        self.last_number = None
        self.current_round = 0

    def play(self, countdown=0):

        with self.output:
            clear_output()
        with self.plot_output:
            clear_output()

        display(self.vertical_box)
        with self.output:
            for i in range(countdown, 0, -1):
                print(i)
                time.sleep(1)
                clear_output()
        self.start = timeit.default_timer()
        self.loop()

    def _ipython_display_(self):
        display(self.vertical_box)
