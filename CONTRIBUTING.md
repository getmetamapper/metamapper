# Contributing Guide

Want to contribute towards this repository? This document is a good place to start.

## How can I contribute?

### Reporting Bugs

When [opening a new issue](https://github.com/metamapper-io/metamapper/issues/new/choose), always make sure to fill out the issue template. This step is crucial, as it gives our team insight into what is actually happening so we can quickly triage and resolve your issue.

Please report a single bug per issue.

Provide reproduction steps: List all the steps necessary to reproduce the issue. The person reading your bug report should be able to follow these steps to reproduce your issue with minimal effort.

### Feature Requests

If you would like to suggest an enhancement or ask for a new feature, please open a [feature request](https://github.com/metamapper-io/metamapper/issues/new/choose) via the Issue Tracker. We'll do our best to review your request and respond within 48 hours.

Please try to provide as much details as possible – the primary focus should be on the **problem you are trying to solve** (with examples) and the secondary focus should be on your proposed solution.

### Documentation

Metamapper could always use better documentation. We host our [documentation](https://www.metamapper.io) using [Github](https://github.com/metamapper-io/docs) and [Docusaurus](https://github.com/facebook/docusaurus).

Please feel free to open a PR to contribute!

### Pull Requests

**Code contributions are welcomed and encouraged.** We could always use help addressing bugs, questions, and documentation improvements. Scanning through the [Issue Tracker](https://github.com/metamapper-io/metamapper/issues) is a good place to start.

For major changes or significant features, we suggest you reach out first and discuss what you'd like to implement and how. This will make sure that your changes are aligned with our vision for Metamapper and that no one else is already working on a similar implementation.

#### Opening a Pull Request

We use the Pull Request feature in GitHub to manage code changes and deployments. The development process *generally* follows this pattern:

- Fork the [metamapper](https://github.com/metamapper-io/metamapper) repository
- Create a new branch off the `master` branch
- Make your code changes
- If your changes are spread across multiple commits, squash them into a single commit
- Open a pull request via the GitHub UI and tag **@metamapper-io/core**

We'll review the pull request, approve, and then merge as appropriate. Code review is mandatory for this repository. It will add some overhead for each change, but it will also prevent bad code from being shipped.

#### Rebase Worfklow

Metamapper uses a rebase workflow. We expect every commit to represent a clear and stable change. We also expect every pull request should consist of a single commit.

#### Squashing

If your branch uses multiple commits, you will need to squash it down to a single commit. It is important that you update the finalized commit message to follow our accepted format.

For example, the Github UI will create a new commit message which is a combination of all commits. **This does not follow the commit guidelines** that are described below.

If you’re working locally, it often can be useful to `--amend` a commit, or utilize `rebase -i` to reorder, squash, and reword your commits. Here is a [nice walk-through](https://www.internalpointers.com/post/squash-commits-into-one-git) on how to squash commits.

#### Commit Guidelines

We ask that all contributors follow the relatively strict rules described in this section when making git commits. Legible messages make project history and tracked changes easier to follow.

##### General Rules

- Each commit should be a single, stable change
- Limit the commit messages to 70 characters
- Capitalize the subject line
- Do not end the subject line with a period
- Use present tense (e.g., "implement" versus "implemented" or "implements")

##### Commit Message Format

As previously mentioned, commit messages should follow this basic format:

```
type(scope): <subject>
```

##### Type

Must be one of the following:

| Type    | Description  |
| ------- | -------------|
| `build` | Changes that affect Docker and/or CI configuration files
| `docs`  | Changes to documentation
| `feat`  | A brand new feature (**note**: causes `minor` version upgrade)
| `fix`   | A bug fix (**note**: causes `patch` version upgrade)
| `perf`  | A code change that refactors and/or improves performance (**note**: causes `patch` version upgrade)
| `test`  | Adding missing tests or correcting existing tests
| `chore` | General administrative tasks (e.g., license changes, editor config, etc.)

##### Scopes

The scope should be the name of the core component affected by the commit. It can be seen as a general subject tag for the commit. Scopes are not required, but strongly suggested.

Scopes can generally correspond with the Django applet that is being updated, such as `inspector` and `revisioner`.

##### Message

The subject should be a succinct description of the change. You should capitalize the first letter of the subject, but not include a dot (.) at the end. Please use present tense – e.g., "change" instead of "changed" or "changes".

Here's a good example:

```
refactor(inspector): Update Postgresql to use psycopg2-binary
```

