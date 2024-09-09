# Ouroboros
Middleware which communicates with the robots using RabbitMQ.

## Setup
Requires `python >= 3.11`
1. `python -m venv venv`
2. `./venv/Script/activate`
3. `pip install -r requirements/dev.txt`

### Azure
1. [Install the azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
2. `az login`

## Running
```
faststream run server:app --reload
```

## Testing
```
pytest
```
