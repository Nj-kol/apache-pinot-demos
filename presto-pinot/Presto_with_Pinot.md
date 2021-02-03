
# Presto Docker

* To install Presto on docker, its best to do it in two rounds. This is because it we need some files 
  withing the Presto installation, which otherwise have to be created manually

## Round : 1

```bash
mkdir -p ${HOME}/volumes/presto/data
mkdir -p ${HOME}/volumes/presto/config

docker pull prestosql/presto:348

docker run -d \
--network sandbox \
--name presto-standalone \
-v ${HOME}/volumes/presto/data:/data/presto \
prestosql/presto:348
```

**Copy files from within docker container to host**

```bash
docker cp presto-standalone:/usr/lib/presto/default/etc ${HOME}/volumes/presto/config/etc
```

## Round : 2

Now that we have got all the necessary files from docker container to local, we can create the actual instance

```bash
docker container stop presto-standalone
docker container rm presto-standalone

docker run -d \
-p 30052:8080 \
--network sandbox \
--name presto-standalone \
-v ${HOME}/volumes/presto/config/etc:/usr/lib/presto/etc \
-v ${HOME}/volumes/presto/data:/data/presto \
prestosql/presto:348
```

## UI

http://localhost:30052/

user - admin

## Housekeeping

docker container logs presto-standalone

docker container stop presto-standalone
docker container rm presto-standalone

docker container restart presto-standalone

docker container exec -it presto-standalone bash

# Connect with Pinot

* The presto docker image comes out-of-the-box with the necessary plugins for Pinot, so nothing needs to be 
  installed additionally. Only some configurations needs to be tweaked

```bash
vim ${HOME}/volumes/presto/config/etc/catalog/pinot.properties
```

* Add the following lines

```
connector.name=pinot
pinot.controller-urls=pinot-controller:9000
```

Here `pinot-controller` is the name of the docker container running as a pinot controller

* Restart the presto container

```bash
docker container restart presto-standalone
```

* Connect to pinot

```bash
docker container exec -it presto-standalone presto --catalog pinot --schema default
```

```sql
presto:default> show tables;
presto:default> select * from transcript;
```

* Sample output

```bash
studentid | firstname | lastname | score | timestampinepoch | gender |  subject
-----------+-----------+----------+-------+------------------+--------+-----------
       200 | Lucy      | Smith    |   3.8 |    1570863600000 | Female | Maths
       200 | Lucy      | Smith    |   3.5 |    1571036400000 | Female | English
       201 | Bob       | King     |   3.2 |    1571900400000 | Male   | Maths
       202 | Nick      | Young    |   3.6 |    1572418800000 | Male   | Physics
```

* Alternatively, you can use the following steps 

```bash
docker container exec -it presto-standalone presto

presto> show catalogs;
presto> use pinot.default;
```

**Important Locations**

/usr/lib/presto/etc 

/data/presto/plugin

## Configuration

* Configuration is expected to be mounted to either to `/etc/presto` or `/usr/lib/presto/etc`
 (the latter takes precedence). 

  If neither of these exists then the default single node configuration will be used.

* The default configuration uses `/data/presto` as the default for `node.data-dir`. 

* Thus if using the default configuration and a mounted volume is desired for the data directory 
  it should be mounted to `/data/presto`

References
==========
https://github.com/prestosql/presto/tree/master/docker

https://prestodb.io/docs/current/connector/pinot.html