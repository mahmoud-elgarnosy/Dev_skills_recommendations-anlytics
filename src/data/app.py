# app.py
import dash
import layout
import callbacks

app = dash.Dash(__name__)

app.layout = layout.create_layout()
callbacks.register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)