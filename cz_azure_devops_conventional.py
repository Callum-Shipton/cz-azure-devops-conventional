import os
import re
from typing import Any, Dict, List

from commitizen import defaults, git, config
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.cz.exceptions import CzException

__all__ = ["AzureDevopsConventionalCz"]

DEFAULT_CHANGE_TYPE_MAP = {
    "feat": "Feat",
    "fix": "Fix",
    "refactor": "Refactor",
    "perf": "Perf",
}

def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class AzureDevopsConventionalCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern

    # bump all changes by at least patch level
    bump_map = { 
        "BREAKING CHANGE": defaults.MAJOR,
        "feat": defaults.MINOR,
        "fix": defaults.PATCH,
        "refactor": defaults.PATCH,
        "perf": defaults.PATCH,
        "style": defaults.PATCH,
        "test": defaults.PATCH,
        "docs": defaults.PATCH,
        "build": defaults.PATCH,
        "ci": defaults.PATCH,
        "chore": defaults.PATCH,        
    }

    bump_map_major_version_zero = {
        "BREAKING CHANGE": defaults.MINOR,
        "feat": defaults.MINOR,
        "fix": defaults.PATCH,
        "refactor": defaults.PATCH,
        "perf": defaults.PATCH,
        "style": defaults.PATCH,
        "test": defaults.PATCH,
        "docs": defaults.PATCH,
        "build": defaults.PATCH,
        "ci": defaults.PATCH,
        "chore": defaults.PATCH,
    }

    commit_parser = ConventionalCommitsCz.commit_parser
    changelog_pattern = defaults.bump_pattern

    # Read the config file and check if required settings are available
    conf = config.read_cfg()
    work_item_multiple_hint = "42, 123"

    azure_devops_project_base_url = conf.settings.get("azure_devops_project_base_url", None)

    if "change_type_map" not in conf.settings:
        change_type_map = DEFAULT_CHANGE_TYPE_MAP
    else:
        # change_type_map = conf.settings["change_type_map"]
        print("Only default change type map is supported at the moment.")
        quit()

    def questions(self) -> List[Dict[str, Any]]:
        questions: List[Dict[str, Any]] = [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "fix",
                        "name": "fix: A bug fix. Correlates with PATCH in SemVer",
                    },
                    {
                        "value": "feat",
                        "name": "feat: A new feature. Correlates with MINOR in SemVer",
                    },
                    {"value": "docs", "name": "docs: Documentation only changes"},
                    {
                        "value": "style",
                        "name": (
                            "style: Changes that do not affect the "
                            "meaning of the code (white-space, formatting,"
                            " missing semi-colons, etc)"
                        ),
                    },
                    {
                        "value": "refactor",
                        "name": (
                            "refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                    },
                    {
                        "value": "perf",
                        "name": "perf: A code change that improves performance",
                    },
                    {
                        "value": "test",
                        "name": (
                            "test: Adding missing or correcting " "existing tests"
                        ),
                    },
                    {
                        "value": "build",
                        "name": (
                            "build: Changes that affect the build system or "
                            "external dependencies (example scopes: pip, docker, npm)"
                        ),
                    },
                    {
                        "value": "ci",
                        "name": (
                            "ci: Changes to our CI configuration files and "
                            "scripts (example scopes: GitLabCI)"
                        ),
                    },
                    {
                        "value": "chore",
                        "name": "chore: Other changes that don't modify source or test files"
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "message": (
                    f'Azure Devops work item number (multiple "{self.work_item_multiple_hint}").'
                ),
                "filter": self.parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": (
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: (press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]
        return questions

    def parse_scope(self, text):
        """
        Require and validate the scope to be Azure Devops work item ids.
        """
        workItemRE = re.compile(r"\d+")

        if not text:
            return ""

        workItems = [i.strip() for i in text.strip().split(",")]
        for workItem in workItems:
            if not workItemRE.fullmatch(workItem):
                raise InvalidAnswerError(f"Azure Devops work item '{workItem}' is not valid.")

        return required_validator(workItems, msg="Azure Devops work item is required")

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        work_items = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if work_items:
            # Add # prefix to the work item numbers.
            work_items_str = ",".join(['#' + i for i in work_items])
            scope = f"({work_items_str})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{prefix}{scope}: {subject}{body}{footer}"

        return message

    def example(self) -> str:
        return (
            "fix: correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"
            r"(\(\S+\))?!?:(\s.*)"
        )
        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, "r") as f:
            content = f.read()
        return content

    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()

    def changelog_message_builder_hook(
        self, parsed_message: dict, commit: git.GitCommit
    ) -> dict:
        
        if not self.azure_devops_project_base_url:
            print("Failed to generate changelog: Azure Devops project base URL is not set in the config file.")
            quit()

        """add azure devops links to the readme"""
        if parsed_message["scope"]:
            parsed_message["scope"] = " ".join(
                [
                    f"[{work_item_id}]({self.azure_devops_project_base_url}/_workitems/edit/{work_item_id.lstrip('#')})"
                    for work_item_id in parsed_message["scope"].split(",")
                ]
            )
        return parsed_message


class InvalidAnswerError(CzException):
    ...