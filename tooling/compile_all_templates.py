from functools import partial
import os
from pathlib import Path
import re
import shutil
from jinja2 import Environment


PUBLISHED_DATE_REGEX_PATTERN_GROUP_NAME = 'posted_date'
PUBLISHED_DATE_REGEX_PATTERN = r'date\: (?P<posted_date>[0-9]+\-[0-9]+\-[0-9]+)'
TEMPLATE_SUFFIX = '.jinja_template'
PYTHON_SNIPPET_SUFFIX = '.py'
PRECOMPILED_POST_SUFFIX = '.md'
RAW_POSTS_DIRECTORY_NAME = 'posts'
PRECOMPILED_POSTS_DIRECTORY_NAME = 'compiled_posts'
SNIPPET_FORMAT = """```{language}
{code}
```

"""


def is_template(path: Path) -> bool:
    return path.name.endswith(TEMPLATE_SUFFIX)


def is_python_snippet(path: Path) -> bool:
    return path.name.endswith(PYTHON_SNIPPET_SUFFIX)


def read_file_data(path: Path) -> str:
    with open(path, mode='r') as file:
        return file.read()


def pysnippet_creator(file_name: str, snippets: dict) -> str:
    snippet: str = snippets[file_name]

    snippet = snippet.rstrip()

    return SNIPPET_FORMAT.format(code=snippet, language='python')


def is_path_hidden(path: Path) -> bool:
    directory_relative_name = path.name

    if directory_relative_name.startswith('.') or directory_relative_name.startswith('_'):
        return False
    
    return True


if __name__ == '__main__':
    posts_location = Path(RAW_POSTS_DIRECTORY_NAME)
    precompiled_posts_location = Path(PRECOMPILED_POSTS_DIRECTORY_NAME)

    # Prepare precompiled posts location to compile posts after deleting stale data.
    print(f'Deleting the directory {precompiled_posts_location} with all content and recreating the directory.')
    try:
        shutil.rmtree(path=PRECOMPILED_POSTS_DIRECTORY_NAME)
    except Exception as exception:
        print(f'**********\nCaught the following exception {exception}, ignoring.\n**********')
    precompiled_posts_location.mkdir(parents=True, exist_ok=True)

    # Prepare context for following steps.
    published_date_pattern = re.compile(PUBLISHED_DATE_REGEX_PATTERN)
    environment = Environment()

    for post_directory in posts_location.iterdir():
        precompiled_post_location_directory = precompiled_posts_location / post_directory.name

        if is_path_hidden(path=post_directory):
            continue

        # Check if there are any templates to precompile at all. If not - skip the directory.
        template_paths_to_compile = tuple(child_path for child_path in post_directory.iterdir() if is_template(path=child_path))
        if not template_paths_to_compile:
            print(f'No templates found at {post_directory} - skipping.')
            continue

        # Load all snippets for given post
        python_snippet_paths = tuple(child_path for child_path in post_PLdirectory.iterdir() if is_python_snippet(path=child_path))
        python_snippets = {}
        for python_snippet_path in python_snippet_paths:
            snippet = read_file_data(path=python_snippet_path)
            python_snippets[python_snippet_path.name] = snippet

        # Create function that allows retrieval of snippets by their names only by supplying dynamically the snippets set.
        pysnippet_retriever = partial(pysnippet_creator, snippets=python_snippets)

        # For each template, read it, fill it with snippets and save compiled version in precompiled posts directory.
        for template_path in template_paths_to_compile:
            template_data = read_file_data(path=template_path)

            # Find date on which the post is to be published.
            searched_data = published_date_pattern.search(template_data)
            published_date = searched_data.group(PUBLISHED_DATE_REGEX_PATTERN_GROUP_NAME)

            # Compile data by inserting snippets and other related data.
            template = environment.from_string(source=template_data)
            precompiled_post_data = template.render(pysnippet=pysnippet_retriever)

            # Determine the precompiled post path.
            precompiled_post_name = template_path.name.replace(TEMPLATE_SUFFIX, PRECOMPILED_POST_SUFFIX)
            full_precompiled_post_name = f'{published_date}-{precompiled_post_name}'
            precompiled_post_path = precompiled_post_location_directory / full_precompiled_post_name

            # Make sure the post directory exists in precompiled posts directory.
            precompiled_post_location_directory.mkdir(parents=True, exist_ok=True)

            # Save precompiled post.
            with open(precompiled_post_path, mode='w+') as file:
                file.write(precompiled_post_data)
            
            print(f'Compiled {template_path} into {precompiled_post_path}.')
