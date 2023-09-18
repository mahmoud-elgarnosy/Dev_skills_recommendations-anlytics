# Import your Dash app's Flask server instance
from src.app import app as application  # Replace 'app' with your actual app's filename (without .py)

# Below is an optional configuration to define environment variables.
# Replace 'your_secret_key' and 'your_other_variable' with your actual environment variables.
# This step may be necessary if your app relies on environment variables.
# You can remove this section if you don't need it.

# application.secret_key = 'your_secret_key'
# application.config['SOME_VARIABLE'] = 'your_other_variable'

if __name__ == '__main__':
    application.run()
