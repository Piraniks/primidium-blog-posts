import logging
from functools import partial
from pathlib import Path
from re import compile

from jinja2 import Environment

PUBLISHED_DATE_REGEX_PATTERN_GROUP_NAME = r'posted_date'
_DATE_REGEX_PATTERN = r'[0-9]{4}\-[0-9]{2}\-[0-9]{2}'
_PUBLISHED_DATE_REGEX_PATTERN = (
    r'date\: (?P<' + PUBLISHED_DATE_REGEX_PATTERN_GROUP_NAME + r'>' + _DATE_REGEX_PATTERN + r')'
)
PUBLISHED_DATE_PATTERN = compile(_PUBLISHED_DATE_REGEX_PATTERN)

TEMPLATE_SUFFIX = '.post_template'
PYTHON_SNIPPET_SUFFIX = '.py'
BUILT_POST_SUFFIX = '.md'

SNIPPET_FORMAT = """```{language}
{code}
```"""

TIP_FORMAT = "> {tip}"
TIP_SUFFIX = r"""
{: .prompt-tip }
"""


HIDDEN_PATH_PREFIXES = ('.', '_')


logger = logging.getLogger(name=__name__)


def is_path_hidden(*, path: Path) -> bool:
    relative_name = path.name

    return any(relative_name.startswith(hidden_path_prefix) for hidden_path_prefix in HIDDEN_PATH_PREFIXES)


def is_post_template(*, path: Path) -> bool:
    return path.name.endswith(TEMPLATE_SUFFIX)


def is_code_snippet(*, path: Path) -> bool:
    return path.name.endswith(PYTHON_SNIPPET_SUFFIX)


class NoLanguageDetected(Exception):
    pass


def determine_file_language(*, file_name: str) -> str:
    if file_name.endswith(PYTHON_SNIPPET_SUFFIX):
        return 'python'

    raise NoLanguageDetected()


def read_file_data(*, path: Path) -> str:
    with open(path, mode='r') as file:
        return file.read()


# Cannot force kwargs for file_name as templates would need to call it using kwargs as well, which is not ergonomic.
def snippet_factory(file_name: str, *, snippets: dict[Path, str], template_directory: Path) -> str:
    snippet_absolute_path = (template_directory / file_name).resolve()
    snippet: str | None = snippets.get(snippet_absolute_path)

    if snippet is None:
        raise Exception(f'Snippet {snippet_absolute_path} not found in snippets set.')

    logger.debug(f'Retrieving snippet {snippet_absolute_path} (as {file_name}) in the context of {template_directory}')

    return SNIPPET_FORMAT.format(code=snippet, language=determine_file_language(file_name=file_name))


def collect_snippets(*, path: Path, root_path: Path) -> dict[Path, str]:
    snippets = dict()
    for child_path in path.iterdir():
        if is_path_hidden(path=child_path):
            logger.info(f"Skipping directory/file as it's considered hidden {child_path}")
            continue

        if child_path.is_dir():
            logger.info(f'Entering directory {child_path} looking for templates')
            nested_snippets = collect_snippets(path=child_path, root_path=root_path)
            snippets.update(nested_snippets)

        elif child_path.is_file() and is_code_snippet(path=child_path):
            logger.info(f'Retrieving content from snippet {child_path}')
            snippet_data = read_file_data(path=child_path)
            cleaned_up_snippet_data = snippet_data.strip()

            snippets[child_path] = cleaned_up_snippet_data

    return snippets


def collect_templates(*, path: Path, root_path: Path) -> dict[Path, str]:
    templates = dict()
    for child_path in path.iterdir():
        if is_path_hidden(path=child_path):
            logger.info(f"Skipping directory/file as it's considered hidden {child_path}")
            continue

        if child_path.is_dir():
            logger.info(f'Entering directory {child_path} looking for templates')
            nested_templates = collect_templates(path=child_path, root_path=root_path)
            templates.update(nested_templates)

        elif child_path.is_file() and is_post_template(path=child_path):
            logger.info(f'Retrieving content from template {child_path}')
            template_data = read_file_data(path=child_path)
            cleaned_up_template_data = template_data

            templates[child_path] = cleaned_up_template_data

    return templates


def save_built_post(*, built_post_data: str, built_post_path: Path) -> None:
    logger.info(f'Saving built post to {built_post_path}')
    built_post_directory_path = built_post_path.parent
    built_post_directory_path.mkdir(parents=True, exist_ok=True)

    built_post_path.write_text(built_post_data)


def generate_built_post_name(
    *, absolute_built_posts_directory: Path, absolute_raw_posts_directory: Path,
    template_content: str, template_directory: Path, template_path: Path
) -> Path:
    searched_data = PUBLISHED_DATE_PATTERN.search(template_content)
    if not searched_data:
        raise Exception(f'No date found in {template_path}.')

    published_date = searched_data.group(PUBLISHED_DATE_REGEX_PATTERN_GROUP_NAME)

    template_name = template_path.name
    post_name_with_correct_suffix = template_name.replace(TEMPLATE_SUFFIX, BUILT_POST_SUFFIX)
    built_post_name = f'{published_date}-{post_name_with_correct_suffix}'
    relative_template_directory = template_directory.relative_to(absolute_raw_posts_directory)

    built_post_path = absolute_built_posts_directory / relative_template_directory / built_post_name
    logger.debug(f'Built post path: {built_post_path}')

    return built_post_path


# Cannot force kwargs for file_name as templates would need to call it using kwargs as well, which is not ergonomic.
def tip_factory(tip: str) -> str:
    return TIP_FORMAT.format(tip=tip) + TIP_SUFFIX


def build_post_contents(
    *, environment: Environment, snippets: dict[Path, str], template_content: str, template_directory: Path
) -> str:
    template = environment.from_string(source=template_content)
    fetch_snippet_for_template = partial(snippet_factory, snippets=snippets, template_directory=template_directory)
    built_post_data = template.render(snippet=fetch_snippet_for_template, tip=tip_factory)

    # Ensure that the post ends with a newline to follow best practices.
    # Not sure why this isn't happening, maybe jinja2 eats newlines at the end?
    # Works fine with the snippets in the middle of the post.
    if not built_post_data.endswith('\n'):
        logger.debug(f"Adding newline to the end of the post as it's missing in the context of {template_directory}")
        built_post_data += '\n'

    return built_post_data


def build_posts(*, posts_directory: Path, built_posts_directory: Path) -> None:
    # Using absolute paths here makes it easier later on to apply relative paths - those can be cleanly resolved.
    raw_posts_absolute_directory = posts_directory.absolute()
    built_posts_absolute_directory = built_posts_directory.absolute()

    snippets = collect_snippets(path=raw_posts_absolute_directory, root_path=raw_posts_absolute_directory)
    templates = collect_templates(path=raw_posts_absolute_directory, root_path=raw_posts_absolute_directory)
    environment = Environment()
    post_data: set[tuple[Path, str]] = set()

    for template_path, template_content in templates.items():
        logger.debug(f'Building post from template {template_path}')
        template_directory = template_path.parent

        built_post_data = build_post_contents(
            environment=environment,
            snippets=snippets,
            template_content=template_content,
            template_directory=template_directory,
        )

        built_post_path = generate_built_post_name(
            absolute_built_posts_directory=built_posts_absolute_directory,
            absolute_raw_posts_directory=raw_posts_absolute_directory,
            template_content=template_content,
            template_directory=template_directory,
            template_path=template_path,
        )

        post_data.add((built_post_path, built_post_data))

    if post_data:
        for built_post_path, built_post_data in post_data:
            save_built_post(built_post_data=built_post_data, built_post_path=built_post_path)
    else:
        logger.warning('No posts to build.')
