# CONTRIBUTING

Contributions are very welcome. Please don't hesitate to submit an issue or a PR.

If you'd like to submit code, please comment on an existing issue to have it assigned to you or make a new one. I'm happy to accept improvements, but just be aware there's no guarantee your new feature will be merged without some prior discussion to ensure it fits within the existing goals of the project. This also helps prevent accidental duplicate work.

Happy coding!

### Commit guidelines

Generally, small and frequent commits are preferred. This makes review much simpler and reduces the chance for merge conflicts and makes bugs and regressions easier to isolate. Several clear and focused commits for a PR are much preferred over large commits. Thanks =)

## Submitting a PR

Before submitting a PR, please verify that all linting and code formatting rules are applied and all tests pass.

### Linting and formatting manually

At the time of this writing, the following are the linters and formatters being used.
- ruff
- djlint
- mypy

The easiest way to manually execute all the required linting and code formatting is to run `just pre-commit`. Or simply `pre-commit` if you've already activated your Python virtual environment. You may, of course, run the various linters individually, but you will need to refer to their documentation for instructions are how to do so.

### Running tests

The project's test suite can be run via `pytest`.
TODO: document fixtures and django client-side testing

## AI policy

I'm aware that many developers are moving towards using AI assistants and tools to write their code. While I'm staunchly against generative AI in almost every way, I don't want that to prevent people from offering potential improvements to this software. However if you do use such tools, there are a few strict requirements.

1. All commits written _or_ assisted by one of these tools __MUST__ include the following in the final line of the commit message: "This commit was created or assisted by a generative AI tool". You may optionally provide a comma-separated list of the particular assistant(s) used like so: "This commit was created or assisted by a generative AI tool: Claude, Github Copilot, etc.". Failure to do so means any such commits will __NOT__ be merged, and any past and future commits from the author will receive increased scrutiny.
2. Regardless of the use of AI tools or not, commits are expected to be reasonably sized (e.g. 1-200 lines) perhaps with the exception of some large refactor taking place. This will be especially enforced upon commits assisted by generative AI tools.
3. While AI assisted code __MAY__ be accepted, absolute __NO__ AI generated art will be accepted into the project. If you would like to contribute any art (e.g. icons, backgrounds, designs, etc.) please do so with your own skills, or commission an artist for the desired work.
