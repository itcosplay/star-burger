import requests
import git

from environs import Env

env = Env()
env.read_env()

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

environment_name = env('ENV_NAME')

headers = {
    'X-Rollbar-Access-Token': env('ROLLBAR_TOKEN'),
}

json_data = {
    'environment': environment_name,
    'revision': sha,
    'rollbar_name': environment_name,
    'local_username': environment_name,
    'comment': 'none',
    'status': 'succeeded',
}

response = requests.post('https://api.rollbar.com/api/1/deploy', headers=headers, json=json_data)

