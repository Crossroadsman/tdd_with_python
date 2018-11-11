import sys
import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run


REPO_URL = 'https://github.com/Crossroadsman/tdd_with_python.git'
VALID_DEPLOY_BRANCHES = ('develop', 'master',)

def deploy():

    # env.user is the unix username on the server
    # e.g., 'my_user'
    # env.host is the url we've decided for the server
    # e.g., 'staging.mysite.com'
    site_directory = f'/home/{env.user}/sites/{env.host}'

    # `run` means 'run this shell command on the server'
    # `-p` creates directories recursively, only if needed
    run(f'mkdir -p {site_directory}')

    # `cd` is a fabric context manager that means:
    # "run all the following statements inside the specified working dir
    with cd(site_directory):
        _get_latest_source()
        _update_venv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()


def _get_latest_source():

    # `local` executes a command on the local machine.
    # `capture=True` means that the function will return the output from
    # the command
    current_branch = local('git branch | grep -E "\* "', capture=True)
    current_branch = current_branch.split()[1]
    if current_branch not in VALID_DEPLOY_BRANCHES:
        sys.exit(f'{current_branch} is not a valid deployment branch')

    if exists('.git'):
        run(f'git checkout {current_branch}')
        run('git fetch')

    else:
        run(f'git clone --branch {current_branch} {REPO_URL} .')

    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_venv():
    if not exists('venv/bin/pip3'):
        run(f'python3 -m venv venv')
    run('./venv/bin/pip3 install -r requirements.txt')


def _create_or_update_dotenv():

    # `append` conditionally adds a line to a file, if that line is not
    # already in the file
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')


def _update_static_files():
    run('./venv/bin/python3 manage.py collectstatic --noinput')


def _update_database():
    run('./venv/bin/python3 manage.py migrate --noinput')
