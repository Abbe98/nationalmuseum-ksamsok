# Nationalmuseum K-samsök

An OAI-PMH endpoint implemented over Nationalmuseum's REST API. Only a subset of OAI-PMH is implemented and in its current state it is not compatible with K-samsök's harvester.

## Development

With [pipenv](https://pipenv.readthedocs.io/en/latest/).

```bash
pipenv install
pipenv run flask run
```

## Deployment

The dockerfile within this repository can be used for deployment behind a webserver such as Nginx or Apache which would act as a reverse proxy. You will however need to update the variables in `.env`, in particular `BASEURL`(The URL exposed to the public) and `ADMINEMAIL`. 

Running with Docker:

```bash
docker build . -t oai-pmh
docker run -d -p 5000:5000 --restart=always --env-file=.env oai-pmh
```
