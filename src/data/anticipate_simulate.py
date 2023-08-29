# anticipate_simulate.py
import dash
import anticipate_simulate_layout
import anticipate_simulate_callbacks


def create_layout_register_callbacks(app):
    app_layout = anticipate_simulate_layout.create_layout()
    print('mode-content.children' not in app.callback_map)
    if 'mode-content.children' not in app.callback_map:
        anticipate_simulate_callbacks.register_callbacks(app)

    return app_layout

# app = dash.Dash(__name__)
# app.layout = create_layout_register_callbacks(app)

# if __name__ == "__main__":
#     app.run_server(debug=True)
