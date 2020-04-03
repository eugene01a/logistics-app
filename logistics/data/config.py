import yaml
import os
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
def config_home():
    return os.environ.get('CONFIG_HOME', PROJECT_ROOT)

def load(filename, mode = 'r'):
    config_home_path = os.path.join(config_home(), '%s.yml' % filename )
    with open(config_home_path, mode) as ymlfile:
        return yaml.load(ymlfile)


def save_evernote_access_token(access_token):
    config_home_path = os.path.join(config_home(), 'auth.yml')
    doc = load('auth')
    doc['evernote']['access_token'] = access_token
    with open(config_home_path, 'w') as f:
        yaml.dump(doc, f, default_flow_style=False)