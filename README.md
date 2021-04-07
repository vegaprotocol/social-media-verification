# Social Media Verification

This is a simple Python script that searches Twitter for tweets that contain an expected string. Once it finds a matching tweet, it attempts to extract a public key and signature from the end of the Tweet, verify the signature, and if it's valid, store the Twitter identity in MongoDB alongside the public key.

## Deploying to devnet and Fairground

The process is fully automated:
* once you merge your change onto `develop` branch it will automatically deploy to Devnet. (see [GitHub Workflow](.github/workflows/deploy-devnet.yml) for details)
* once you merge `develop` into `main` branch it will automatically deploy to Stagnet and Fairground. (see [GitHub Workflow](.github/workflows/deploy-fairground.yml) for details)

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

## Environment Setup

You will need Twitter API keys in your environment for the app to work. Look at `.env.sample` to see which variables are missing. Once you have them, you should rename `.env.sample` to `.env` and then you will be ready to try and start the app.

## Build & Running

The app should be built with Docker:

`docker build -t social-media-verification .`

Then start the containers via Docker compose:

`docker-compose up -d`

The following command will stop the app:

`docker-compose down`
