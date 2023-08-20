import dash
from dash import dcc, html


app = dash.Dash(__name__)

categories_skills = {
    'Languages': ['APL', 'Assembly', 'Bash/Shell', 'C', 'C#', 'C++', 'COBOL', 'Clojure', 'Crystal', 'Dart', 'Delphi', 'Elixir', 'Erlang', 'F#', 'Fortran', 'Go', 'Groovy', 'HTML/CSS', 'Haskell', 'Java', 'JavaScript', 'Julia', 'Kotlin', 'LISP', 'Lua', 'MATLAB', 'OCaml', 'Objective-C', 'PHP', 'Perl', 'PowerShell', 'Python', 'R', 'Ruby', 'Rust', 'SAS', 'SQL', 'Scala', 'Solidity', 'Swift', 'TypeScript', 'VBA'],
    'ToolsTechs': ['Ansible', 'Chef', 'Docker', 'Flow', 'Homebrew', 'Kubernetes', 'Pulumi', 'Puppet', 'Terraform', 'Unity 3D', 'Unreal Engine', 'Yarn', 'npm'],
    'Webframes': ['ASP.NET', 'ASP.NET Core ', 'Angular', 'Angular.js', 'Blazor', 'Deno', 'Django', 'Drupal', 'Express', 'FastAPI', 'Fastify', 'Flask', 'Gatsby', 'Laravel', 'Next.js', 'Node.js', 'Nuxt.js', 'Phoenix', 'Play Framework', 'React.js', 'Ruby on Rails', 'Svelte', 'Symfony', 'Vue.js', 'jQuery'],
    'MiscTechs': ['.NET', 'Apache Kafka', 'Apache Spark', 'Capacitor', 'Cordova', 'Electron', 'Flutter', 'GTK', 'Hadoop', 'Hugging Face Transformers', 'Ionic', 'Keras', 'NumPy', 'Pandas', 'Qt', 'React Native', 'Scikit-learn', 'Spring', 'TensorFlow', 'Tidyverse', 'Torch/PyTorch', 'Uno Platform', 'Xamarin'],
    'Databases': ['Cassandra', 'Cloud Firestore', 'CouchDB', 'Couchbase', 'DynamoDB', 'Elasticsearch', 'Firebase Realtime Database', 'IBM DB2', 'MariaDB', 'Microsoft SQL Server', 'MongoDB', 'MySQL', 'Neo4j', 'Oracle', 'PostgreSQL', 'Redis', 'SQLite'],
    'Platforms': ['AWS', 'Colocation', 'DigitalOcean', 'Firebase', 'Google Cloud', 'Heroku', 'IBM Cloud or Watson', 'Linode', 'Managed Hosting', 'Microsoft Azure', 'OVH', 'OpenStack', 'Oracle Cloud Infrastructure', 'VMware'],
    'NEWCollabToolss': ['Android Studio', 'Atom', 'CLion', 'Eclipse', 'Emacs', 'GoLand', 'IPython/Jupyter', 'IntelliJ', 'Nano', 'Neovim', 'NetBeans', 'Notepad++', 'PhpStorm', 'PyCharm', 'Qt Creator', 'RAD Studio (Delphi_C++ Builder)', 'RStudio', 'Rider', 'RubyMine', 'Spyder', 'Sublime Text', 'TextMate', 'Vim', 'Visual Studio', 'Visual Studio Code', 'Webstorm', 'Xcode']
}

app.layout = html.Div([
    html.H1("Skills Selection", style={'textAlign': 'center'}),
    # Checkbox section for each category
    html.Div(
        [
            html.Div(
                [
                    html.H3(category, style={'textAlign': 'center'}),
                    dcc.Checklist(
                        options=[{'label': skill, 'value': skill} for skill in skills],
                        value=[],
                        style={'margin': '10px', 'verticalAlign': 'top'},
                        labelStyle={'fontSize': '14px', 'margin': '5px'}
                    )
                ],
                style={'display': 'grid', 'gridTemplateColumns': 'repeat(20, 1fr)', 'gap': '20px'}
            )
            for category, skills in categories_skills.items()
        ],
        style={'display': 'grid', 'gridGap': '20px', 'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))', 'margin': 'auto'}
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
