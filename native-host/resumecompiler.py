"""
Resume compilation and database utilities.
"""

import sqlite3
import resumeparser
import pathlib
import subprocess


def compile_resume(
    description: str,
    template: pathlib.Path,
    choices: pathlib.Path,
    db_path: pathlib.Path,
) -> None:
    """
    Compiles the resume and adds it to the database using the specified template and
    choices given the job description.

    Args:
        description: raw job description
        template: resume LaTeX template path
        choices: YAML file with choices for resume sections
    """
    title, _, rest = description.partition("\n")
    company, _, _ = rest.partition("\n")

    contents = resumeparser.parse_resume(description, template, choices)

    make_pdf(contents)
    insert_resume(title, company, contents, db_path)


def make_pdf(contents: str) -> None:
    """
    Compiles the resume to PDF using the given LaTeX contents.

    Args:
        contets: LaTeX contents of the resume
    """
    compile_command = format(
        """
        echo '%s' | pdflatex
        rm texput.{aux,log,out}
        rm Andre_Aw_resume.pdf
        mv texput.pdf Andre_Aw_resume.pdf
        """,
        contents,
    )

    subprocess.run(compile_command, shell=True, check=False)


def insert_resume(
    title: str, company: str, contents: str, db_path: pathlib.Path
) -> None:
    """
    Inserts the resume into the database.

    Args:
        title: title of the resume
        company: company name
        contents: LaTeX contents of the resume
        db_path: path to the SQLite database
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title: TEXT NOT NULL,
                company: TEXT NOT NULL,
                contents: TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            "INSERT INTO resumes (title, company, contents) VALUES (?, ?, ?)",
            (title, company, contents),
        )
        conn.commit()
