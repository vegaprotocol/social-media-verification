[![Python linters](https://github.com/vegaprotocol/social-media-verification/actions/workflows/python-linters.yml/badge.svg)](https://github.com/vegaprotocol/social-media-verification/actions/workflows/python-linters.yml)
[![Python tests](https://github.com/vegaprotocol/social-media-verification/actions/workflows/python-unit-tests.yml/badge.svg)](https://github.com/vegaprotocol/social-media-verification/actions/workflows/python-unit-tests.yml)
[![Deploy to Devnet](https://github.com/vegaprotocol/social-media-verification/actions/workflows/deploy-devnet.yml/badge.svg)](https://github.com/vegaprotocol/social-media-verification/actions/workflows/deploy-devnet.yml)
[![Deploy to Stagnet and Testnet](https://github.com/vegaprotocol/social-media-verification/actions/workflows/deploy.yml/badge.svg)](https://github.com/vegaprotocol/social-media-verification/actions/workflows/deploy.yml)
[![license](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

# Social Media Verification

This is an HTTP serverless application that searches Twitter for tweets containing specific text.

For each matched tweet, the script:
* extracts a public key and a signed message from the tweet,
* validates that the signature is for a message containing one word: user's handle (the username after @),
* if validation is successful, then the public key and user's handle are saved to a database,

The list of pairs: public-key + user-handle is available on the other endpoint.

## Deploying to Devnet and Stagnet/Testnet

The process is fully automated:
* once you merge your change onto `develop` branch it will automatically deploy to Devnet. (see [GitHub Workflow](.github/workflows/deploy-devnet.yml) for details)
* once you merge `develop` into `main` branch it will automatically deploy to Stagnet and Testnet. (see [GitHub Workflow](.github/workflows/deploy.yml) for details)

Important: Please note that all files from [src](src) directory are deployed, so be careful what you add/remove there.

## Local development

### Run linters

You must have Python3 along with flake8 and black installed.

```bash
make black
make flake8
```

### Run unit tests in Docker

```bash
make test-in-docker
```

### TDD

If you are TDD fan, then you will like this

```bash
make tdd
```

### VSCode remote development in docker

You can find config in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json).

### Run unit tests on your computer

```bash
# replace <venv> with your name
# create Python Virtual Environment
python3 -m venv <venv>
source <venv>/bin/activate

# install dependencies
python3 -m pip install -r src/requirements.txt
python3 -m pip install -r requirements-dev.txt

# Develop & run unit tests
make test

# exit Python Virtual Environment
deactivate
```

### Manual testing

You can manually test integration with Twitter and MongoDB with scripts in [tests/manual](tests/manual) directory. Remember to put proper credentials there.

* Example to test `/statistics` endpoint:
 - update MonboDB credentials in `tests/manual/smv_storage.py` (don't commit this change!!),
 - run `./tests/manual/statistics_handler.py`
