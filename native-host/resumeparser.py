"""
LaTeX string processing utilities.
"""

import pathlib
import yaml


HEADING_SIZE = 4


def parse_resume(
    description: str, template: pathlib.Path, choices: pathlib.Path
) -> str:
    """
    Returns a LaTeX string for compilation using the given content.

    Args:
        description: job description
        template: LaTeX resume template
        choices: lines to fill in

    Returns:
        string for compilation
    """
    description_set = set(description.lower().split())
    template_blocks = template.read_text().split("<>\n")
    choices_dict = yaml.safe_load(choices.read_text())

    output = ""
    content = False
    for block in template_blocks:
        if content:
            output += process_block(block, description_set, choices_dict)
        else:
            output += block
        content = not content

    return output


def process_block(
    block: str, description_set: set[str], choices_dict: dict[str, dict[str, str]]
) -> str:
    """
    Returns the LaTeX content used to fill a block.

    Args:
        block: single line with a comment denoting experience
        description_set: job description
        choices_dict: lines to fill in

    Returns:
        string for compilation
    """

    output = ""
    for line in get_lines(block, description_set, choices_dict):
        output += r"\resumeItem{" + line + "}\n"

    return output


def get_lines(
    block: str, description_set: set[str], choices_dict: dict[str, dict[str, str]]
) -> list[str]:
    """
    Returns lines that match the job description

    Args:
        block: single line with a comment denoting experience
        description_set: job description
        choices_dict: lines to fill in

    Returns:
        list of matching lines
    """

    experience = block.lstrip().lstrip("%").lstrip().rstrip("\n")
    choices = choices_dict[experience]
    value_order = {value: i for i, value in enumerate(choices.values())}

    matches = list(set(choices[key] for key in choices.keys() & description_set))
    nonmatches = iter(set(choices[key] for key in choices.keys() - description_set))

    while len(matches) < HEADING_SIZE:
        matches.append(next(nonmatches))

    matches = sorted(matches, key=lambda x: value_order[x])

    while len(matches) > HEADING_SIZE:
        matches.pop()

    return matches
