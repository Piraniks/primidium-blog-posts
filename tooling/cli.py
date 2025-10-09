import logging
from pathlib import Path

import typer

from tooling.build_posts import build_posts


tooling_directory = Path(__file__).parent
MAIN_REPOSITORY_DIRECTORY = tooling_directory.parent
POSTS_DIRECTORY = MAIN_REPOSITORY_DIRECTORY / 'posts'


cli_application = typer.Typer()


@cli_application.command(name='ping')
def ping():
    typer.echo('pong')


@cli_application.command(name='build-posts')
def build_posts(*, to: str):
    built_posts_directory = Path(to).absolute()

    return build_posts(posts_directory=POSTS_DIRECTORY, built_posts_directory=built_posts_directory)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    cli_application()
