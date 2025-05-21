import numpy
import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.graph_objs as go
import pandas as pd


class ManualGame:
    def __init__(self, team_names, max_rounds, cooldown, width=1000):
        self.team_names = team_names
        self.max_rounds = max_rounds
        self.cooldown = cooldown
        self.gen = numpy.random.default_rng(seed=None)
        self.width = width
        self.initialize_ui()
        
    def initialize_ui(self):
        self.current_round = 0
        self.team_scores = {team: [0] for team in self.team_names}
        self.team_blocked_until = {team: -1 for team in self.team_names}
        self.last_number = None
        self.last_cooldown = self.cooldown
        self.number_display = widgets.HTML(layout=dict(width='80%'))
        self.team_buttons = {
            team: widgets.ToggleButton(description=team, value=False, tooltip=team,layout=dict(width='50%'))
            for team in self.team_names
        }
        self.submit_button = widgets.Button(description="Submit Selections", button_style='success', layout=dict(width='50%'))
        self.output = widgets.Output()
        self.controls = widgets.VBox([
                self.number_display,
                *self.team_buttons.values(),
                self.submit_button,
                self.output,
            ],
            layout=dict(width='40%', align_items='center')
        )
        self.plot_output = widgets.Output(layout=dict(width='100%'))
        
        def update_plot():
            fig = go.Figure()
            for team in self.team_names:
                fig.add_trace(go.Scatter(
                    x=list(range(self.current_round + 1)),
                    y=self.team_scores[team],
                    mode='lines+markers',
                    name=team
                ))
            fig.update_layout(xaxis_title='Round', yaxis_title='Score', xaxis_range=[0, self.max_rounds], width=self.width)
            with self.plot_output:
                clear_output(wait=True)
                display(fig)
        
        def start_new_round():
            self.current_round += 1
            self.last_number = self.gen.pareto(3)
            
            self.number_display.value = f"""
                <div style='text-align:center; padding: 10px;'>
                    <h1 style='margin-bottom: 0;'>Round {self.current_round} / {self.max_rounds} <br> Cooldown: {self.last_cooldown}</h1>
                    <h2 style='color:darkred; font-size: 48px; margin-top: 10px;'>Reward: {self.last_number:.2f}</h2>
                </div>
            """
        
            for team, btn in self.team_buttons.items():
                blocked = self.team_blocked_until[team] - self.current_round
                is_blocked = blocked >= 0
                btn.disabled = is_blocked
                btn.value = False
                btn.description = f'❌ {team} ({blocked + 1})' if is_blocked else team

        def on_submit(_):
            with self.output:
                clear_output()
                for team, btn in self.team_buttons.items():
                    took_action = btn.value and not btn.disabled
                    score = self.last_number if took_action else 0
                    self.team_scores[team].append(self.team_scores[team][-1] + score)
                    if took_action:
                        self.team_blocked_until[team] = self.current_round + self.last_cooldown
                update_plot()
            if self.current_round < self.max_rounds:
                start_new_round()
            else:
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
                self.number_display.value = ''
                self.submit_button.layout.display = 'none'
                for x in self.team_buttons.values():
                  x.layout.display = 'none'
                with self.output:
                    display(df)
                    
        self.submit_button.on_click(on_submit)
        self.game_ui = widgets.HBox(
            [self.controls, self.plot_output],
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

        update_plot()
        start_new_round()
      
    def _ipython_display_(self):
        display(self.vertical_box)

