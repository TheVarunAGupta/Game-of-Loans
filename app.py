from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State, MATCH
from server import app
from pages import livetesting, backtesting, strategies
import asyncio
import main
import threading


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # NavBar
    html.Div([
        dcc.Link('Live Testing', href='/livetesting'),
        dcc.Link('Backtesting', href='/backtesting'),
        dcc.Link('Strategies', href='/strategies')
    ], className='navbar'),

    # Page Content
    html.Div(id='page-content', className='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/livetesting':
        return livetesting.layout
    elif pathname == '/backtesting':
        return backtesting.layout
    elif pathname == '/strategies':
        return strategies.layout
    else:
        return livetesting.layout

@app.callback(
    Output({"type": "toggle", "index": MATCH}, "className"),
    Input({"type": "toggle", "index": MATCH}, "n_clicks"),
    State({"type": "toggle", "index": MATCH}, "className"),
    prevent_initial_call=True
)
def toggle_strategy(n_clicks, current_class):
    if current_class and "active" in current_class:
        return current_class.replace(" active", "")
    return (current_class or "toggle-switch") + " active"

@app.callback(
    Output({"type": "lt-toggle", "index": MATCH}, "className"),
    Input({"type": "lt-toggle", "index": MATCH}, "n_clicks"),
    State({"type": "lt-toggle", "index": MATCH}, "className"),
    prevent_initial_call=True
)
def toggle_run_button(n_clicks, current_class):
    if current_class and "active" in current_class:
        return current_class.replace(" active", "")
    return (current_class or "toggle-switch") + " active"


if __name__ == '__main__':
    threading.Thread(target=lambda: asyncio.run(main.run_live()), daemon=True).start()
    app.run(debug=True, use_reloader=False)