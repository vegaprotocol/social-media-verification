# Social Media Verification

This is a simple Python script that searches Twitter for tweets that contain an expected string. Once it finds a matching tweet, it attempts to extract a public key and signature from the end of the Tweet, verify the signature, and if it's valid, store the Twitter identity in MongoDB alongside the public key.

## Environment Setup

You will need Twitter API keys in your environment for the app to work. Look at `.env.sample` to see which variables are missing. Once you have them, you should rename `.env.sample` to `.env` and then you will be ready to try and start the app.

## Build & Running

The app should be built with Docker:

`docker build -t social-media-verification .`

Then start the containers via Docker compose:

`docker-compose up -d`

The following command will stop the app:

`docker-compose down`
