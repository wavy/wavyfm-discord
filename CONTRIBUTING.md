# Contributing

Thanks for your interest in contributing to the wavy.fm Discord bot! The project is still in its early stages, so we
apologize if this document is skipping some important stuff. If you have any questions, you can reach out via the GitHub
issues on this repository, or through [Discord](https://wavy.fm/discord).

This project is maintained officially by wavy.fm and by the Developer Working Group.

## Creating environment

You can use either `pipenv` or `virtualenv` to initialize the developer environment. I personally prefer pipenv for
this.

```bash
# Pipenv creates the environment and fetches the dependencies
pipenv install --dev
pipenv shell
```

```bash
# Alternatively, using virtualenv
virtualenv venv
./venv/bin/activate
pip install -e .
pip install flake8
```

## Run lint

To run the linting tool, use

```bash
# With pipenv
pipenv run lint

# With virtualenv
flake8 . --count --show-source --statistics
```
