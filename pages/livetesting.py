from dash import html, dcc, Input, Output, State, callback, ALL
import main
import plotly.graph_objects as go

layout = html.Div(className="page-content", children=[
    dcc.Store(id="live-results", data={}),
    dcc.Store(id="lt-sync", data={}),

    html.H1("Live Testing", className="page-title", style={
        "position": "absolute",
        "top": "60px",
        "left": "25px",
        "margin": "0",
        "color": "#EFF6E0",
        "z-index": "100"
    }),

    dcc.Interval(
        id="live-update-interval",
        interval=5 * 1000, # Update every 5 seconds
        n_intervals=0
    ),

    html.Div(className="main-layout", children=[

        # === LEFT: Main Content ===
        html.Div(className="main-content", children=[

            # PNL Graph
            html.Div(className="card hero-card", children=[
                html.Div(className="card-header", children=[
                    html.H2("PNL Graph", className="card-title"),
                    dcc.Dropdown(
                        id="pnl-strategy-filter",
                        options=[{"label": "All Strategies", "value": "all"}],
                        value="all",
                        className="strategy-dropdown",
                        clearable=False,
                        persistence=True,
                        persistence_type="local"
                    )
                ]),
                dcc.Graph(
                    id="pnl-graph",
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
                        id="trades-strategy-filter",
                        options=[{"label": "All Strategies", "value": "all"}],
                        value="all",
                        className="strategy-dropdown",
                        clearable=False,
                        persistence=True,
                        persistence_type="local"
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
                    html.Tbody(id="trades-card-body")  # initially empty
                ])
            ]),
        ]),
        # === RIGHT: Sidebar ===
        html.Div(className="sidebar", children=[

            # === Controls Card ===
            html.Div(className="card sidebar-card", children=[
                html.Div(
                    className="card-header",
                    style={"display": "flex", "justify-content": "space-between", "align-items": "center"},
                    children=[
                        html.H3("Controls", className="card-title"),
                        html.Div(
                            style={"display": "flex", "align-items": "center", "gap": "8px"},
                            children=[
                                html.Span("Run", style={"font-weight": "bold"}),
                                html.Button(
                                    className="toggle-switch active" if main.live_running else "toggle-switch",
                                    id={"type": "lt-toggle", "index": "livetest"},
                                    n_clicks=0
                                )
                            ]
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
                            className="text-input",
                            persistence=True,
                            persistence_type="local"
                        )
                    ]),

                    html.Div(className="input-box", children=[
                        html.Label("Starting Balance", className="input-label"),
                        dcc.Input(
                            id="balance-input",
                            type="number",
                            value=10000,
                            className="text-input",
                            persistence=True,
                            persistence_type="local"
                        )
                    ]),

                    html.Div(className="input-box", children=[
                        html.Label("Timeframe", className="input-label"),
                        dcc.Input(
                            id="timeframe-input",
                            type="text",
                            value="1Min",
                            className="text-input",
                            persistence=True,
                            persistence_type="local"
                        )
                    ])
                ])
            ]),

            # === Active Strategies Section ===
            html.Div(
                className="strategy-list",
                children=[
                    html.Div(className="card strategy-card", children=[
                        html.Div(className="strategy-header", children=[
                            html.H4(name),
                            html.Button(
                                className="toggle-switch active" if name in main.get_active_strategies() else "toggle-switch",
                                id={"type": "toggle", "index": name},
                                n_clicks=0
                            )
                        ]),
                        html.Details(open=False, children=[
                            html.Summary("Metrics"),
                            html.Div(className="metric-box", id={"type": "strategy-summary", "index": name}, children=[
                                html.P("Metrics will appear here if strategy is on.")
                            ])
                        ])
                    ]) for name in main.list_strategy_names()
                ]
            )
        ])
    ])
])

# === Run Livetest ===
@callback(
    Output("live-results", "data"),
    Input({"type": "lt-toggle", "index": "livetest"}, "n_clicks"),
    State("symbol-input", "value"),
    State("balance-input", "value"),
    State("timeframe-input", "value"),
    State({"type": "toggle", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)

def run_livetest(n_clicks_live, symbol, balance, timeframe, strategy_clicks):
    is_active = (n_clicks_live % 2 == 1) if n_clicks_live else False

    strategy_names = main.list_strategy_names()
    active_strategies = [
        name for name, clicks in zip(strategy_names, strategy_clicks)
        if clicks and clicks % 2 == 1
    ]

    main.live_running = is_active
    main.set_active_strategies(active_strategies)
    main.current_symbol = symbol
    main.current_balance = balance
    main.current_timeframe = timeframe

    if not is_active:
        main.stop_live()
        return {"running": False, "strategies": []}

    print(">>> Callback fired")
    print("   is_active:", is_active)
    print("   active_strategies:", active_strategies)
    print("   symbol:", symbol, "balance:", balance, "timeframe:", timeframe)

    return {"running": is_active, "strategies": active_strategies}

# === Update PNL Graph ===
@callback(
    Output("pnl-graph", "figure"),
    Output("pnl-strategy-filter", "options"),
    Output("pnl-strategy-filter", "value"),
    Input("live-update-interval", "n_intervals"),
    Input("pnl-strategy-filter", "value"),
    prevent_initial_call=False
)

def update_live_pnl(n_intervals, filter_value):
    results = main.manager.get_all_results()

    active_strategies = main.get_active_strategies()
    results = {k: v for k, v in results.items() if k in active_strategies}

    if not results:
        empty_fig = go.Figure().update_layout(
            title="PNL",
            xaxis_title="Time",
            yaxis_title="Portfolio Value",
            template="plotly_dark"
        )
        default_options = [{"label": "All Strategies", "value": "all"}]
        return empty_fig, default_options, 'all'

    options = [{"label": "All Strategies", "value": "all"}] + [
        {"label": name, "value": name} for name in results.keys()
    ]
    if filter_value not in [opt["value"] for opt in options]:
        filter_value = "all"

    fig = go.Figure()
    for strat, data in results.items():
        if filter_value != "all" and strat != filter_value:
            continue

        pnl = data["pnl_history"]
        if not pnl.empty:
            fig.add_trace(go.Scatter(
                x=pnl["timestamp"], y=pnl["portfolio_value"],
                mode="lines", name=strat
            ))

    fig.update_layout(
        title="PNL" if filter_value == "all" else f"PNL ({filter_value})",
        xaxis_title="Time",
        yaxis_title="Portfolio Value",
        template="plotly_dark"
    )
    return fig, options, filter_value

# === Update Trades Table ===
@callback(
    Output("trades-strategy-filter", "options"),
    Output("trades-strategy-filter", "value"),
    Output("trades-card-body", "children"),
    Input("live-update-interval", "n_intervals"),
    Input("trades-strategy-filter", "value"),
    prevent_initial_call=False
)

def update_live_trades(n_intervals, filter_value):
    results = main.manager.get_all_results()

    active_strategies = main.get_active_strategies()
    results = {k: v for k, v in results.items() if k in active_strategies}

    if not results:
        default_options = [{"label": "All Strategies", "value": "all"}]
        return default_options, "all", []

    options = [{"label": "All Strategies", "value": "all"}] + [
        {"label": name, "value": name} for name in results.keys()
    ]
    if filter_value not in [opt["value"] for opt in options]:
        filter_value = "all"

    rows = []
    for strat, data in results.items():
        if filter_value != "all" and strat != filter_value:
            continue
        trades = data["trade_history"]
        if not trades.empty:
            for _, log in trades.iterrows():
                rows.append(html.Tr([
                    html.Td(strat),
                    html.Td(log["symbol"]),
                    html.Td(html.Span(log["side"], className=f"tag {log['side'].lower()}")),
                    html.Td(str(log["timestamp"])),
                    html.Td(f"${log['price']:,.2f}"),
                    html.Td(f"{log['quantity']:.4f}")
                ]))

    return options, filter_value, rows

# === Update Metrics ===
@callback(
    Output({"type": "strategy-summary", "index": ALL}, "children"),
    Input("live-update-interval", "n_intervals"),
    prevent_initial_call=False
)

def update_live_metrics(n_intervals):
    results = main.manager.get_all_results()
    strategy_names = main.list_strategy_names()
    active_strategies = main.get_active_strategies()

    summaries = []
    for name in strategy_names:
        if results and name in results and "summary" in results[name] and name in active_strategies:
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
            summaries.append([html.P("Metrics will appear here if strategy is running")])

    return summaries

# === Update Toggle Visuals ===
@callback(
    Output({"type": "toggle", "index": ALL}, "className", allow_duplicate=True),
    Output({"type": "lt-toggle", "index": ALL}, "className", allow_duplicate=True),
    Input("live-update-interval", "n_intervals"),
    prevent_initial_call='initial_duplicate'
)

def update_toggle_visuals(n_intervals):
    strategy_names = main.list_strategy_names()
    active = set(main.get_active_strategies())
    strat_classes = ["toggle-switch active" if name in active else "toggle-switch" for name in strategy_names]
    run_class = ["toggle-switch active" if main.live_running else "toggle-switch"]
    return strat_classes, run_class

# === Sync Strategy Toggles ===
@callback(
    Output("lt-sync", "data"),
    Input({"type": "toggle", "index": ALL}, "n_clicks"),
    State({"type": "toggle", "index": ALL}, "id"),
    prevent_initial_call=True
)
def sync_strategy_toggles(n_clicks_list, toggle_ids):
    n_clicks_list = n_clicks_list or []
    toggle_ids = toggle_ids or []
    active = []
    for tid, clicks in zip(toggle_ids, n_clicks_list):
        if clicks and clicks % 2 == 1:
            active.append(tid.get("index"))
    main.set_active_strategies(active)
    return {"active_strategies": active}