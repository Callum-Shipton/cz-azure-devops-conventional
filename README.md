# cz-azure-devops-conventional

**cz-azure-devops-conventional** is a plugin for the [**commitizen tools**](https://github.com/commitizen-tools/commitizen), a toolset that helps you to create [**conventional commit messages**](https://www.conventionalcommits.org/en/v1.0.0/). Since the structure of conventional commits messages is standardized they are machine readable and allow commitizen to automaticially calculate and tag [**semantic version numbers**](https://semver.org/) as well as create **CHANGELOG.md** files for your releases.

This plugin extends the commitizen tools by:
- **require a Azure Devops work item id** in the commit message
- **create links to Azure Devops** work items in the CHANGELOG.md

When you call commitizen `commit` you will be required to enter the a Azure Devops work item id (or multiple ids, see below).
```
> cz commit
? Select the type of change you are committing fix: A bug fix. Correlates with PATCH in SemVer
? Azure Devops work item number (multiple "42, 123").
...
```

The changelog created by cz (`cz bump --changelog`)will contain links to the Azure Devops work items.
```markdown
## v1.0.0 (2024-10-10)

### Features
- **[#123](https://dev.azure.com/org-name/project-name/_workitems/edit/123)**: create changelogs with links to work items
- **[#42](https://dev.azure.com/org-name/project-name/_workitems/edit/42),[#13](https://dev.azure.com/org-name/project-name/_workitems/edit/13)**: allow multiple work items to be referenced in the commit
``` 


## Installation

Install with pip
`python -m pip install cz-azure-devops-conventional` 

You need to use a cz config file that has the **required** additional value `azure_devops_project_base_url` and `github_repo` and may contain the **optional** value `project_prefix`.

Example `.cz.yaml` config for this repository
```yaml
commitizen:
  name: cz-azure-devops-conventional
  tag_format: v$version
  version: 1.0.0
  azure_devops_project_base_url: https://dev.azure.com/org-name/project-name
```

### pre-commit
Add this plugin to the dependencies of your commit message linting with `pre-commit`. 

Example `.pre-commit-config.yaml` file.
```yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v2.17.13
    hooks:
      - id: commitizen
        stages: [commit-msg]
        additional_dependencies: [cz-azure-devops-conventional]
```
Install the hook with 
```bash
pre-commit install --hook-type commit-msg
```

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
This plugin would not have been possible without the fantastic work from:
* [commitizen tools](https://github.com/commitizen-tools/commitizen)
* [conventional_JIRA](https://github.com/Crystalix007/conventional_jira)
* [cz-github-jira-conventional](https://github.com/apheris/cz-github-jira-conventional)