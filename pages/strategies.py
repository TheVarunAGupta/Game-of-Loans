from dash import html, dcc, Input, Output, State, ctx, dash, ALL, callback
import main

strategy_names = main.list_strategy_names()
layout = html.Div([
    # Stores
    dcc.Store(id='strategies-init', data='load'),
    dcc.Store(id='current-mode', data='idle'),  # idle | add | edit
    dcc.Store(id='editing-strat-name', data=None),

    html.Div(className='main-layout', children=[

        html.H1('Strategies', className='page-title', style={
            'position': 'absolute',
            'top': '60px',
            'left': '25px',
            'margin': '0',
            'color': '#EFF6E0',
            'z-index': '100'
        }),

        # ===== LEFT: Strategy List / Management =====
        html.Div(className='main-content', style={'flex': '1'}, children=[

            # Add New Strategy button
            html.Div(className='card', children=[
                html.H3('Add New Strategy'),
                html.Button('Add New', className='button', id='add-strategy-btn')
            ]),

            # Strategy List (dynamic)
            html.Div(id='strategy-list', children=[
                html.Div(className='card strategy-card', children=[
                    html.Div(className='strategy-header', children=[
                        html.H4(name),
                        html.Div(className='strategy-actions', style={'display': 'flex', 'gap': '10px'}, children=[
                            html.Button('Edit', className='button', id={'type': 'edit-btn', 'index': name}),
                            html.Button('Delete', className='button', id={'type': 'delete-btn', 'index': name})
                        ])
                    ])
                ]) for name in strategy_names
            ])
        ]),

        # ===== RIGHT: Code Editor =====
        html.Div(className='sidebar', style={'flex': '1'}, children=[
            html.Div(className='card', children=[
                html.H3('Strategy Code'),
                dcc.Textarea(
                    id='strategy-code-editor',
                    value='# Strategy code will appear here',
                    style={
                        'width': '100%',
                        'height': '500px',
                        'background-color': '#01161E',
                        'color': '#EFF6E0',
                        'font-family': 'monospace',
                        'padding': '10px',
                        'border-radius': '10px',
                        'border': '1px solid #124559'
                    }
                ),
                # Buttons
                html.Div(
                    style={'margin-top': '10px', 'text-align': 'right', 'display': 'flex', 'gap': '10px'},
                    children=[
                        html.Button('Save New', className='button', id='save-new-btn', style={'display': 'none'}),
                        html.Button('Save Changes', className='button', id='save-edit-btn', style={'display': 'none'}),
                        html.Button('Cancel', className='button', id='cancel-btn', style={'display': 'none'})
                    ]
                ),
                html.Div(id='message-box', style={'margin-top': '10px', 'color': 'red'})
            ])
        ])
    ])
])


# === Refresh strategy list ===
@callback(
    Output('strategy-list', 'children'),
    Input('strategies-init', 'data'),
    prevent_initial_call=False
)
def load_strategy_list(_):
    strategy_names = main.list_strategy_names()
    return [
        html.Div(className='card strategy-card', children=[
            html.Div(className='strategy-header', children=[
                html.H4(name),
                html.Div(className='strategy-actions', style={'display': 'flex', 'gap': '10px'}, children=[
                    html.Button('Edit', className='button', id={'type': 'edit-btn', 'index': name}),
                    html.Button('Delete', className='button', id={'type': 'delete-btn', 'index': name})
                ])
            ])
        ]) for name in strategy_names
    ]

# === Toggle Save/Cancel button visibility ===
@callback(
    Output('save-new-btn', 'style'),
    Output('save-edit-btn', 'style'),
    Output('cancel-btn', 'style'),
    Input('current-mode', 'data')
)
def toggle_buttons(mode):
    if mode == 'add':
        return {'display': 'inline-block'}, {'display': 'none'}, {'display': 'inline-block'}
    elif mode == 'edit':
        return {'display': 'none'}, {'display': 'inline-block'}, {'display': 'inline-block'}
    else:  # idle
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

# === Button Presses ===
@callback(
    Output('strategies-init', 'data'),
    Output('strategy-code-editor', 'value'),
    Output('current-mode', 'data'),
    Output('editing-strat-name', 'data'),
    Output('message-box', 'children'),
    Input('add-strategy-btn', 'n_clicks'),
    Input('cancel-btn', 'n_clicks'),
    Input('save-new-btn', 'n_clicks'),
    Input('save-edit-btn', 'n_clicks'),
    Input({'type': 'edit-btn', 'index': ALL}, 'n_clicks'),
    Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks'),
    State('strategy-code-editor', 'value'),
    State('editing-strat-name', 'data'),
    prevent_initial_call=True
)
def editor_actions(add_n, cancel_n, save_new_n, save_edit_n, edit_n_clicks, delete_n_clicks, code_value, editing_strat_name):
    triggered = ctx.triggered_id

    # === Add New clicked ===
    if triggered == 'add-strategy-btn':
        template = '''from strats.base_strategy import BaseStrategy

class Test(BaseStrategy):
    def __init__(self,):
        super().__init__('Test', max_lookback=1)

    def generate_signals(self, data):
        return super().generate_signals(data)'''

        return dash.no_update, template, 'add', None, 'Adding new strategy...'

    # === Cancel clicked ===
    if triggered == 'cancel-btn':
        return dash.no_update, '# Strategy code will appear here', 'idle', None, ''

    # === Edit clicked ===
    if isinstance(triggered, dict) and triggered.get('type') == 'edit-btn':
        strat_name = triggered['index']
        code = main.read_code(strat_name)
        return dash.no_update, code, 'edit', strat_name, f'Editing {strat_name}...'

    # === Delete clicked ===
    if isinstance(triggered, dict) and triggered.get('type') == 'delete-btn':
        strat_name = triggered['index']
        success = main.delete_strategy(strat_name)
        if success:
            return 'load', '# Strategy code will appear here', 'idle', None, f'Strategy "{strat_name}" deleted.'
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, f'Error: Could not delete "{strat_name}".'

    # === Save New clicked ===
    if triggered == 'save-new-btn' and code_value:
        strat_name = main.strategy_name(code_value)
        if not strat_name:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Error: Could not find strategy class in the code'
        valid, msg, class_name = main.validate_code(code_value, mode='add')
        if not valid:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, msg
        filename = main.make_strategy_filename(strat_name)
        success = main.add_new_strategy(filename, code_value)
        if success:
            return 'load', '# Strategy code will appear here', 'idle', None, f'New strategy "{class_name}" added successfully.'
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Error: Could not save new strategy file.'

    # === Save Changes clicked ===
    if triggered == 'save-edit-btn' and code_value and editing_strat_name:
        valid, msg, class_name = main.validate_code(code_value, mode='edit', original_name=editing_strat_name)
        if not valid:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, msg
        success = main.save_code(editing_strat_name, code_value)
        if success:
            return dash.no_update, '# Strategy code will appear here', 'idle', None, f'Strategy "{editing_strat_name}" updated successfully.'
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, 'Error: Could not save changes.'

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update