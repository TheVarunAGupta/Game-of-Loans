from dash import html, dcc, Input, Output, State, ctx, dash, dash_table, callback, ALL
import main
import plotly.graph_objects as go
import pandas as pd

layout = html.Div(className="page-content", children=[
    dcc.Store(id="backtest-results", data={}),

    html.H1("Back Testing", className="page-title", style={
        "position": "absolute",
        "top": "60px",          # adjust to match navbar height
        "left": "25px",         # align with navbar/content
        "margin": "0",
        "color": "#EFF6E0",
        "z-index": "100"
    }),

    html.Div(className="main-layout", children=[

        # ===== LEFT: Main Content =====
        html.Div(className="main-content", children=[

            # PNL Graph
            html.Div(className="card hero-card", children=[
                html.Div(className="card-header", children=[
                    html.H2("PNL Graph", className="card-title"),
                    dcc.Dropdown(
                        id="bt-pnl-strategy-filter",
                        options=[{"label": "All Strategies", "value": "all"}],
                        value="all",
                        className="strategy-dropdown",
                        clearable=False
                    )
                ]),
                dcc.Graph(
                    id="bt-pnl-graph",
                    figure=go.Figure(
                        data=[],
                        layout=go.Layout(
                            title='PNL',
                            xaxis_title='Time',
                            yaxis_title='Portfolio Value',
                            template='plotly_dark'
                        )
                    ),
                    style={"height": "400px"}
                )
            ]),

            # Trades Table
            html.Div(className="card trades-card", style={"max-height": "300px", "overflow-y": "scroll"}, children=[
                html.Div(className="card-header", children=[
                    html.H2("Trades", className="card-title"),
                    dcc.Dropdown(
                        id="bt-trades-strategy-filter",
                        options=[{"label": "All Strategies", "value": "all"}],
                        value="all",
                        className="strategy-dropdown",
                        clearable=False
                    )
                ]),
                html.Table(className="trades-table", children=[
                    html.Thead([
                        html.Tr([
                            html.Th("Strategy"),
                            html.Th("Symbol"),
                            html.Th("Side"),
                            html.Th("Time"),
                            html.Th("Price"),
                            html.Th("Quantity"),
                        ])
                    ]),
                    html.Tbody(id="bt-trades-card-body")  # initially empty
                ])
            ]),
        ]),
        # ===== RIGHT: Sidebar =====
        html.Div(className="sidebar", children=[

            # --- Controls Card ---
            html.Div(className="card sidebar-card", children=[
                # Header row: title + button
                html.Div(
                    className="card-header",
                    style={"display": "flex", "justify-content": "space-between", "align-items": "center"},
                    children=[
                        html.H3("Controls", className="card-title"),
                        html.Button(
                            "Run Backtest",
                            className="button",
                            id="run-backtest-btn",
                            n_clicks=0
                        )
                    ]
                ),

                # Collapsible section for parameters
                html.Details(open=False, children=[
                    html.Summary("Parameters"),

                    html.Div(className="input-box", children=[
                        html.Label("Symbol", className="input-label"),
                        dcc.Input(
                            id="symbol-input",
                            type="text",
                            value="AAPL",
                            className="text-input"
                        )
                    ]),

                    html.Div(className="input-box", children=[
                        html.Label("Start Date", className="input-label"),
                        dcc.Input(
                            id="start-date-input",
                            type="text",
                            value="2021-12-01",
                            className="text-input"
                        )
                    ]),

                    html.Div(className="input-box", children=[
                        html.Label("End Date", className="input-label"),
                        dcc.Input(
                            id="end-date-input",
                            type="text",
                            value="2021-12-31",
                            className="text-input"
                        )
                    ]),

                    html.Div(className="input-box", children=[
                        html.Label("Starting Balance", className="input-label"),
                        dcc.Input(
                            id="balance-input",
                            type="number",
                            value=10000,
                            className="text-input"
                        )
                    ]),

                    html.Div(className="input-box", children=[
                        html.Label("Timeframe", className="input-label"),
                        dcc.Input(
                            id="timeframe-input",
                            type="text",
                            value="1Min",
                            className="text-input"
                        )
                    ])
                ])
            ]),

            # --- Active Strategies Section ---
            html.Div(
                className="strategy-list",
                children=[
                    html.Div(className="card strategy-card", children=[
                        html.Div(className="strategy-header", children=[
                            html.H4(name),
                            html.Button(
                                className="toggle-switch",
                                id={"type": "toggle", "index": name},
                                n_clicks=0
                            )
                        ]),
                        html.Details(open=False, children=[
                            html.Summary("Metrics"),
                            html.Div(className="metric-box", id={"type": "bt-strategy-summary", "index": name}, children=[
                                html.P("Metrics will appear here after backtest.")
                            ])
                        ])
                    ]) for name in main.list_strategy_names()
                ]
            )
        ])
    ])
])

# === Run Backtest and Store Results ===
@callback(
    Output("backtest-results", "data"),
    Input("run-backtest-btn", "n_clicks"),
    State("symbol-input", "value"),
    State("start-date-input", "value"),
    State("end-date-input", "value"),
    State("balance-input", "value"),
    State("timeframe-input", "value"),
    State({"type": "toggle", "index": ALL}, "className"),
    prevent_initial_call=True
)
def run_backtest_action(n_clicks, symbol, start_date, end_date, balance, timeframe, toggle_classes):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    strategy_names = main.list_strategy_names()
    active_strategies = [
        name for name, cls in zip(strategy_names, toggle_classes) 
        if cls and "active" in cls
    ]
    if not active_strategies:
        return {}
    
    results = {}
    run_params = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "balance": balance,
        "timeframe": timeframe,
    }

    for strat in active_strategies:
        if strat in results:
            continue
        pnl_history, trade_history, summary = main.run_backtest(
            strategy_name=strat,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            starting_balance=float(balance),
            timeframe=timeframe
        )

        strat_results = {
            "pnl_history": pnl_history.to_dict('records') if hasattr(pnl_history, "to_dict") else pnl_history,
            "trade_history": trade_history.to_dict('records') if hasattr(trade_history, "to_dict") else trade_history,
            "summary": summary
        }
        results[strat] = strat_results

    return {
        "params_hash": run_params,
        "strategies": results,
        "params": run_params,
        "active_strategies": active_strategies
    }

# === Update PNL Graph ===
@callback(
    Output("bt-pnl-graph", "figure"),
    Output("bt-pnl-strategy-filter", "options"),
    Output("bt-pnl-strategy-filter", "value"),
    Input("backtest-results", "data"),
    Input("bt-pnl-strategy-filter", "value"),
    State({"type": "toggle", "index": ALL}, "className"),
    prevent_initial_call=True
)
def update_pnl_graph(backtest_data, filter_value, toggle_classes):
    if not backtest_data or 'strategies' not in backtest_data:
        return go.Figure().update_layout(
            title="PNL",
            xaxis_title="Time",
            yaxis_title="Portfolio Value",
            template="plotly_dark"
        ), dash.no_update, dash.no_update

    results = backtest_data["strategies"]
    strategy_names = main.list_strategy_names()
    active_strategies = [
        name for name, cls in zip(strategy_names, toggle_classes)
        if cls and "active" in cls
    ]

    results = {k: v for k, v in results.items() if k in active_strategies}

    if not results:
        return go.Figure().update_layout(
            title="PNL",
            xaxis_title="Time",
            yaxis_title="Portfolio Value",
            template="plotly_dark"
        ), dash.no_update, dash.no_update

    options = [{"label": "All Strategies", "value": "all"}] + [
        {"label": name, "value": name} for name in results.keys()
    ]
    if filter_value not in [opt["value"] for opt in options]:
        filter_value = "all"

    # Build the figure
    fig = go.Figure()
    for strat, data in results.items():
        if filter_value != "all" and strat != filter_value:
            continue

        pnl_history = data.get("pnl_history", [])
        times = [log["timestamp"] for log in pnl_history]
        pnl = [log["portfolio_value"] for log in pnl_history]
        fig.add_trace(go.Scatter(x=times, y=pnl, mode="lines", name=strat))

    # title_text = "PNL"
    # if filter_value != "all":
    #     title_text = f"PNL ({filter_value})"
    fig.update_layout(
        title="PNL" if filter_value == "all" else f"PNL ({filter_value})",
        xaxis_title="Time",
        yaxis_title="Portfolio Value",
        template="plotly_dark"
    )
    return fig, options, filter_value

# === Update Trades Table ===
@callback(
    Output("bt-trades-strategy-filter", "options"),
    Output("bt-trades-strategy-filter", "value"),
    Output("bt-trades-card-body", "children"),
    Input("backtest-results", "data"),
    Input("bt-trades-strategy-filter", "value"),
    State({"type": "toggle", "index": ALL}, "className"),
    prevent_initial_call=True
)
def update_trades_table(backtest_data, filter_value, toggle_classes):
    if not backtest_data or "strategies" not in backtest_data:
        return dash.no_update, dash.no_update, []

    # Get strategies from store and filter active
    results = {
        k: v for k, v in backtest_data["strategies"].items()
        if k in [name for name, cls in zip(main.list_strategy_names(), toggle_classes) if cls and "active" in cls]
    }

    if not results:
        return dash.no_update, dash.no_update, []

    options = [{"label": "All Strategies", "value": "all"}] + [
        {"label": name, "value": name} for name in results.keys()
    ]
    if filter_value not in [opt["value"] for opt in options]:
        filter_value = "all"

    rows = []
    for strat, data in results.items():
        if filter_value != "all" and strat != filter_value:
            continue
        trade_history = data.get("trade_history", [])
        for log in trade_history:
            rows.append(html.Tr([
                html.Td(strat),
                html.Td(log.get("symbol", "")),
                html.Td(html.Span(log.get("side", ""), className=f"tag {log.get('side','').lower()}")),
                html.Td(str(pd.to_datetime(log.get("timestamp", "")).strftime("%Y-%m-%d %H:%M"))),
                html.Td(f"${log.get('price', ''):,.2f}"),
                html.Td(f"{log.get('quantity', 0):,.4f}")
            ]))

    return options, filter_value, rows

# === Update Metrics ===
@callback(
    Output({"type": "bt-strategy-summary", "index": ALL}, "children"),
    Input("backtest-results", "data"),
    State({"type": "toggle", "index": ALL}, "className"),
    prevent_initial_call=True
)
def update_metrics(backtest_data, toggle_classes):
    if not backtest_data or "strategies" not in backtest_data:
        results = {}
    else:
        results = backtest_data["strategies"]
        
    strategy_names = main.list_strategy_names()
    active_strategies = [
        name for name, cls in zip(strategy_names, toggle_classes)
        if cls and "active" in cls
    ]
    # Filter only active strategies
    results = {k: v for k, v in results.items() if k in active_strategies}
    
    summaries = []
    for name in main.list_strategy_names():
        if results and name in results and "summary" in results[name]:
            summary = results[name]["summary"]
            summaries.append([
                html.P(f"Final Cash: ${summary.get('Final Cash')}"),
                html.P(f"Portfolio Value: ${summary.get('Portfolio Value')}"),
                html.P(f"Realised PnL: ${summary.get('Realised PnL')}"),
                html.P(f"Unrealised PnL: ${summary.get('Unrealised PnL')}"),
                html.P(f"Total Return %: {summary.get('Total Return %')}"),
                html.P(f"Trades Executed: {summary.get('Trades Executed')}"),
                html.P(f"Win Rate %: {summary.get('Win Rate %')}"),
                html.P(f"Sharpe Ratio: {summary.get('Sharpe Ratio')}"),
                html.P(f"Max Drawdown %: {summary.get('Max Drawdown %')}"),
                html.P(f"Profit Factor: {summary.get('Profit Factor')}")
            ])
        else:
            summaries.append([
                html.P("Metrics will appear here after backtest")
            ])
    return summaries