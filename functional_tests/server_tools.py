from fabric.api import run
from fabric.context_managers import settings, shell_env


def _get_manage_dot_py(host):
    return f'~/sites/{host}/venv/bin/python3 ~/sites/{host}/manage.py'


def _get_server_env_vars(host):
    env_lines = run(f'cat ~/sites/{host}/.env').splitlines()
    return dict(l.split('=') for l in env_lines if l)


def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    print(f'manage.py: {manage_dot_py}')
    with settings(host_string=f'alex@{host}'):
        run(f'{manage_dot_py} flush --noinput')


def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with settings(host_string=f'alex@{host}'):
        env_vars = _get_server_env_vars(host)
        # shell_env sets the environment for the next command
        with shell_env(**env_vars):
            session_key = run(f'{manage_dot_py} create_session {email}')
            return session_key.strip()
