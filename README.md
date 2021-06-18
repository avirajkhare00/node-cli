# Node CLI

![Build and publish](https://github.com/skalenetwork/node-cli/workflows/Build%20and%20publish/badge.svg)
![Test](https://github.com/skalenetwork/node-cli/workflows/Test/badge.svg)
[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

SKALE Node CLI, part of the SKALE suite of validator tools, is the command line to setup, register and maintain your SKALE node.

## Table of Contents

1.  [Installation](#installation)
2.  [CLI usage](#cli-usage)  
    2.1 [Top level commands](#top-level-commands)  
    2.2 [Node](#node-commands)  
    2.3 [Wallet](#wallet-commands)  
    2.4 [sChains](#schain-commands)  
    2.5 [Health](#health-commands)  
    2.6 [SSL](#ssl-commands)  
    2.7 [Logs](#logs-commands)  
    2.8 [Resources allocation](#resources-allocation-commands)  
    2.9 [Validate](#validate-commands)  
3.  [Exit codes](#exit-codes)
4.  [Development](#development)

## Installation

-   Prerequisites

Ensure that the following package is installed: **docker**, **docker-compose** (1.27.4+)

-   Download the executable

```shell
VERSION_NUM={put the version number here} && sudo -E bash -c "curl -L https://github.com/skalenetwork/node-cli/releases/download/$VERSION_NUM/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
```

For versions `<1.1.0`:

```shell
VERSION_NUM=0.0.0 && sudo -E bash -c "curl -L https://skale-cli.sfo2.cdn.digitaloceanspaces.com/skale-$VERSION_NUM-`uname -s`-`uname -m` >  /usr/local/bin/skale"
```

-   Apply executable permissions to the downloaded binary:

```shell
chmod +x /usr/local/bin/skale
```

-   Test the installation

```shell
skale --help
```

## CLI usage

### Top level commands

#### Info

Print build info

```shell
skale info
```

#### Version

Print version number

```shell
skale version
```

Options:

-   `--short` - prints version only, without additional text.

### Node commands

> Prefix: `skale node`

#### Node information

Get base info about SKALE node

```shell
skale node info
```

Options:

`-f/--format json/text` - optional

#### Node initialization

Initialize a SKALE node on current machine

> :warning: **Please avoid re-initialization**: First run `skale node info` to confirm current state of intialization.

```shell
skale node init [ENV_FILE]
```

Arguments:

- `ENV_FILE` - path to .env file (required parameters are listed in the `skale init` command)

You should specify the following environment variables:

-   `SGX_SERVER_URL` - SGX server URL
-   `DISK_MOUNTPOINT` - disk mount point for storing sChains data
-   `DOCKER_LVMPY_STREAM` - stream of `docker-lvmpy` to use
-   `CONTAINER_CONFIGS_STREAM` - stream of `skale-node` to use
-   `IMA_ENDPOINT` - IMA endpoint to connect
-   `ENDPOINT` - RPC endpoint of the node in the network where SKALE Manager is deployed
-   `MANAGER_CONTRACTS_ABI_URL` - URL to SKALE Manager contracts ABI and addresses
-   `IMA_CONTRACTS_ABI_URL` - URL to IMA contracts ABI and addresses
-   `FILEBEAT_URL` - URL to the Filebeat log server


Optional variables:

-   `TG_API_KEY` - Telegram API key
-   `TG_CHAT_ID` - Telegram chat ID
-   `MONITORING_CONTAINERS` - will enable monitoring containers (`filebeat`, `cadvisor`, `prometheus`)

#### Node initialization from backup

Restore SKALE node on another machine

```shell
skale node restore [BACKUP_PATH] [ENV_FILE]
```

Arguments:

- `BACKUP_PATH` - path to the archive with backup data generated by `skale node backup` command
- `ENV_FILE` - path to .env file (required parameters are listed in the `skale init` command)

#### Node backup

Generate backup file to restore SKALE node on another machine

```shell
skale node backup [BACKUP_FOLDER_PATH] [ENV_FILE]
```

Arguments:

- `BACKUP_FOLDER_PATH` - path to the folder where the backup file will be saved


#### Node Registration

```shell
skale node register
```

Required arguments:

-   `--ip` - public IP for RPC connections and consensus
-   `--domain`/`-d` - SKALE node domain name
-   `--name` - SKALE node name

Optional arguments:

-   `--port` - public port - beginning of the port range for node SKALE Chains (default: `10000`)

#### Node update

Update SKALE node on current machine

```shell
skale node update [ENV_FILEPATH]
```

Options:

-   `--yes` - remove without additional confirmation

Arguments:

- `ENV_FILEPATH` - path to env file where parameters are defined

You can also specify a file with environment variables
which will update parameters in env file used during skale node init.

#### Node turn-off

Turn-off SKALE node on current machine and optionally set it to the maintenance mode

```shell
skale node turn-off
```

Options:

-   `--maintenance-on` - set SKALE node into maintenance mode before turning off
-   `--yes` - remove without additional confirmation

#### Node turn-on

Turn on SKALE node on current machine and optionally disable maintenance mode

```shell
skale node turn-on [ENV_FILEPATH]
```

Options:

-   `--maintenance-off` - turn off maintenance mode after turning on the node
-   `--yes` - remove without additional confirmation

Arguments:

- `ENV_FILEPATH` - path to env file where parameters are defined

You can also specify a file with environment variables
which will update parameters in env file used during skale node init.

#### Node maintenance

Set SKALE node into maintenance mode

```shell
skale node maintenance-on
```

Options:

-   `--yes` - set without additional confirmation

Switch off maintenance mode

```shell
skale node maintenance-off
```

#### Domain name

Set SKALE node domain name

```shell
skale node set-domain
```

Options:

- `--domain`/`-d` - SKALE node domain name
-   `--yes` - set without additional confirmation

### Wallet commands

> Prefix: `skale wallet`

Commands related to Ethereum wallet associated with SKALE node

#### Wallet information

```shell
skale wallet info
```

Options:

`-f/--format json/text` - optional

#### Wallet setting

Set local wallet for the SKALE node

```shell
skale wallet set --private-key $ETH_PRIVATE_KEY
```

#### Send ETH tokens

Send ETH tokens from SKALE node wallet to specific address

```shell
skale wallet send [ADDRESS] [AMOUNT]
```

Arguments:

-   `ADDRESS` - Ethereum receiver address
-   `AMOUNT` - Amount of ETH tokens to send

Optional arguments:

`--yes` - Send without additional confirmation

### sChain commands

> Prefix: `skale schains`

#### SKALE Chain list

List of SKALE Chains served by connected node

```shell
skale schains ls
```

#### SKALE Chain configuration

```shell
skale schains config SCHAIN_NAME
```

#### SKALE Chain DKG status

List DKG status for each SKALE Chain on the node

```shell
skale schains dkg
```

#### SKALE Chain info

Show information about SKALE Chain on node

```shell
skale schains info SCHAIN_NAME
```

Options:

-   `--json` - Show info in JSON format

#### SKALE Chain repair

Turn on repair mode for SKALE Chain

```shell
skale schains repair SCHAIN_NAME
```

### Health commands

> Prefix: `skale health`

#### SKALE containers

List all SKALE containers running on the connected node

```shell
skale health containers
```

Options:

-   `-a/--all` - list all containers (by default - only running)

#### sChains healthchecks

Show health check results for all SKALE Chains on the node

```shell
skale health schains
```

Options:

-   `--json` - Show data in JSON format

#### SGX

Status of the SGX server. Returns the SGX server URL and connection status.

```shell
$ skale health sgx

SGX server status:
┌────────────────┬────────────────────────────┐
│ SGX server URL │ https://0.0.0.0:1026/      │
├────────────────┼────────────────────────────┤
│ Status         │ CONNECTED                  │
└────────────────┴────────────────────────────┘
```

### SSL commands

> Prefix: `skale ssl`

#### SSL Status

Status of the SSL certificates on the node

```shell
skale ssl status
```

Admin API URL: \[GET] `/api/ssl/status`

#### Upload certificates

Upload new SSL certificates

```shell
skale ssl upload
```

##### Options

-   `-c/--cert-path` - Path to the certificate file
-   `-k/--key-path` - Path to the key file
-   `-f/--force` - Overwrite existing certificates

Admin API URL: \[GET] `/api/ssl/upload`


#### Check ssl certificate

Check ssl certificate be connecting to healthcheck ssl server

```shell
skale ssl check
```

##### Options

-   `-c/--cert-path` - Path to the certificate file (default: uploaded using `skale ssl upload` certificate)
-   `-k/--key-path` - Path to the key file (default: uploaded using `skale ssl upload` key)
-   `--type/-t` - Check type (`openssl` - openssl cli check, `skaled` - skaled-based check, `all` - both)
-   `--port/-p` - Port to start healthcheck server (defualt: `4536`)
-   `--no-client` - Skip client connection (only make sure server started without errors)

### Logs commands

> Prefix: `skale logs`

#### CLI Logs

Fetch node CLI logs:

```shell
skale logs cli
```

Options:

-   `--debug` - show debug logs; more detailed output

#### Dump Logs

Dump all logs from the connected node:

```shell
skale logs dump [PATH]
```

Optional arguments:

-   `--container`, `-c` - Dump logs only from specified container


### Resources allocation commands

> Prefix: `skale resources-allocation`

#### Show allocation file

Show resources allocation file:

```shell
skale resources-allocation show
```
#### Generate/update

Generate/update allocation file:

```shell
skale resources-allocation generate [ENV_FILE]
```

Arguments:

- `ENV_FILE` - path to .env file (required parameters are listed in the `skale init` command)

Options:

-   `--yes` - generate without additional confirmation
-   `-f/--force` - rewrite allocation file if it exists

### Validate commands

> Prefix: `skale validate`

#### Validate abi

Check whether ABI files contain valid JSON data

```shell
skale validate abi
```

Options:

-   `--json` - show validation result in json format 

## Exit codes

Exit codes conventions for SKALE CLI tools

- `0` - Everything is OK
- `1` - General error exit code
- `3` - Bad API response**
- `4` - Script execution error**
- `5` - Transaction error*
- `6` - Revert error*
- `7` - Bad user error**
- `8` - Node state error**

`*` - `validator-cli` only  
`**` - `node-cli` only

## Development

### Setup repo

#### Install development dependencies

```shell
pip install -e .[dev]
```

##### Add flake8 git hook

In file `.git/hooks/pre-commit` add:

```shell
#!/bin/sh
flake8 .
```

### Debugging

Run commands in dev mode:

```shell
ENV=dev python main.py YOUR_COMMAND
```

### Setting up Travis

Required environment variables:

-   `ACCESS_KEY_ID` - DO Spaces/AWS S3 API Key ID
-   `SECRET_ACCESS_KEY` - DO Spaces/AWS S3 Secret access key
-   `GITHUB_EMAIL` - Email of GitHub user
-   `GITHUB_OAUTH_TOKEN` - GitHub auth token

## Contributing

**If you have any questions please ask our development community on [Discord](https://discord.gg/vvUtWJB).**

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## License

[![License](https://img.shields.io/github/license/skalenetwork/node-cli.svg)](LICENSE)

Copyright (C) 2018-present SKALE Labs
