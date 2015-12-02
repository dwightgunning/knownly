from fabric.api import cd, env, run

prod_server = '178.79.169.241'


def base_env():
    env.user = 'knownly'
    env.root = '/sites/knownly'
    env.directory = '%s/source' % env.root
    env.activate = 'source %s/venvs/current/bin/activate' % env.root
    env.supervisor_webapp_program = 'knownly'
    env.supervisor_workers_program = 'knownly-workers'


def prod():
    base_env()
    env.hosts = [prod_server]


def run_under_venv(command):
    run(env.activate + ' && ' + command)


def git_pull(remote='origin', branch='prod'):
    """Updates the repository."""
    with cd(env.directory):
        run('git fetch --all')
        run('git reset --hard %s/%s' % (remote, branch))


def restart_website():
    run("sudo /usr/local/bin/supervisorctl restart %s" %
        env.supervisor_webapp_program)


def restart_workers():
    run("sudo /usr/local/bin/supervisorctl restart %s" %
        env.supervisor_workers_program)


def deploy(remote='origin', branch='master'):
    """Run the actual deployment steps, e.g: $ fab prod deploy"""
    with cd(env.directory):
        git_pull(remote=remote, branch=branch)
        run_under_venv("npm i")
        run_under_venv("bower install --config.interactive=false")
        run_under_venv("pip install -r %s/requirements.txt" % env.directory)
        run_under_venv("python manage.py migrate --noinput")
        # Build Knownly statics
        run('gulp deploy')
        # collect statics from Django and installed apps (excl. Knownly)
        run_under_venv("python manage.py collectstatic --noinput")

    restart_website()
    restart_workers()
