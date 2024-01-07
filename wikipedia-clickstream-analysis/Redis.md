### Redis CLI

Login to Redis Shell

```shell
docker exec -it redis-stack redis-cli
```

Redis Commands :

```shell
## Create a new bloom filter
BF.RESERVE whitelisted_linktypes 0.001 100

## Add allowed linl types
BF.MADD whitelisted_linktypes link external

## Check for existence
BF.EXISTS whitelisted_linktypes link
BF.EXISTS whitelisted_linktypes external
```