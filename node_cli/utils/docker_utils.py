#   -*- coding: utf-8 -*-
#
#   This file is part of node-cli
#
#   Copyright (C) 2021 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
import itertools
import os
import logging

import docker
from docker.client import DockerClient
from docker.models.containers import Container

from node_cli.utils.helper import run_cmd, str_to_bool
from node_cli.configs import (
    COMPOSE_PATH,
    REMOVED_CONTAINERS_FOLDER_PATH,
    SGX_CERTIFICATES_DIR_NAME,
    SKALE_DIR
)


logger = logging.getLogger(__name__)

SCHAIN_REMOVE_TIMEOUT = 60
IMA_REMOVE_TIMEOUT = 20

MAIN_COMPOSE_CONTAINERS = ('skale-api', 'bounty', 'skale-admin')
BASE_COMPOSE_SERVICES = (
    'transaction-manager',
    'skale-admin',
    'skale-api',
    'bounty',
    'nginx',
    'redis',
    'watchdog',
    'filebeat'
)
MONITORING_COMPOSE_SERVICES = ('node-exporter', 'advisor')
NOTIFICATION_COMPOSE_SERVICES = ('celery',)
COMPOSE_TIMEOUT = 10

DOCKER_DEFAULT_STOP_TIMEOUT = 20

DOCKER_DEFAULT_HEAD_LINES = 400
DOCKER_DEFAULT_TAIL_LINES = 10000

COMPOSE_SHUTDOWN_TIMEOUT = 40


def docker_client() -> DockerClient:
    return docker.from_env()


def get_sanitized_container_name(container_info: dict) -> str:
    return container_info['Names'][0].replace('/', '', 1)


def get_containers(container_name_filter=None, _all=True) -> list:
    return docker_client().containers.list(all=_all)
    return docker_client().containers.list(all=_all, filters={'name': container_name_filter})


def get_all_schain_containers(_all=True) -> list:
    return docker_client().containers.list(all=_all, filters={'name': 'skale_schain_*'})


def get_all_ima_containers(_all=True) -> list:
    return docker_client().containers.list(all=_all, filters={'name': 'skale_ima_*'})


def remove_dynamic_containers():
    logger.info('Removing sChains containers')
    rm_all_schain_containers()
    logger.info('Removing IMA containers')
    rm_all_ima_containers()


def rm_all_schain_containers():
    schain_containers = get_all_schain_containers()
    remove_containers(schain_containers, stop_timeout=SCHAIN_REMOVE_TIMEOUT)


def rm_all_ima_containers():
    ima_containers = get_all_ima_containers()
    remove_containers(ima_containers, stop_timeout=IMA_REMOVE_TIMEOUT)


def remove_containers(containers, stop_timeout):
    for container in containers:
        safe_rm(container, stop_timeout=stop_timeout)


def safe_rm(container: Container, stop_timeout=DOCKER_DEFAULT_STOP_TIMEOUT, **kwargs):
    """
    Saves docker container logs (last N lines) in the .skale/node_data/log/.removed_containers
    folder. Then stops and removes container with specified params.
    """
    container_name = container.name
    logger.info(
        f'Stopping container: {container_name}, timeout: {stop_timeout}')
    container.stop(timeout=stop_timeout)
    backup_container_logs(container)
    logger.info(f'Removing container: {container_name}, kwargs: {kwargs}')
    container.remove(**kwargs)
    logger.info(f'Container removed: {container_name}')


def backup_container_logs(
    container: Container,
    head: int = DOCKER_DEFAULT_HEAD_LINES,
    tail: int = DOCKER_DEFAULT_TAIL_LINES
) -> None:
    logger.info(f'Going to backup container logs: {container.name}')
    logs_backup_filepath = get_logs_backup_filepath(container)
    save_container_logs(container, logs_backup_filepath, tail)
    logger.info(
        f'Old container logs saved to {logs_backup_filepath}, tail: {tail}')


def save_container_logs(
    container: Container,
    log_filepath: str,
    head: int = DOCKER_DEFAULT_HEAD_LINES,
    tail: int = DOCKER_DEFAULT_TAIL_LINES
) -> None:
    separator = b'=' * 80 + b'\n'
    tail_lines = container.logs(tail=tail)
    lines_number = len(io.BytesIO(tail_lines).readlines())
    head = min(lines_number, head)
    log_stream = container.logs(stream=True, follow=True)
    head_lines = b''.join(itertools.islice(log_stream, head))
    with open(log_filepath, 'wb') as out:
        out.write(head_lines)
        out.write(separator)
        out.write(tail_lines)


def get_logs_backup_filepath(container: Container) -> str:
    container_index = sum(1 for f in os.listdir(REMOVED_CONTAINERS_FOLDER_PATH)
                          if f.startswith(f'{container.name}-'))
    log_file_name = f'{container.name}-{container_index}.log'
    return os.path.join(REMOVED_CONTAINERS_FOLDER_PATH, log_file_name)


def ensure_volume(name: str, size: int, dutils=None):
    dutils = dutils or docker_client()
    if is_volume_exists(name, dutils=dutils):
        logger.info(f'Volume with name {name} already exits')
        return
    logger.info(f'Creating volume - size: {size}, name: {name}')
    driver_opts = {'size': str(size)}
    volume = dutils.volumes.create(
        name=name,
        driver='lvmpy',
        driver_opts=driver_opts
    )
    return volume


def is_volume_exists(name: str, dutils=None):
    dutils = dutils or docker_client()
    try:
        dutils.volumes.get(name)
    except docker.errors.NotFound:
        return False
    return True


def compose_rm(env={}):
    logger.info('Removing compose containers')
    run_cmd(
        cmd=(
            'docker-compose',
            '-f', COMPOSE_PATH,
            'down',
            '-t', str(COMPOSE_SHUTDOWN_TIMEOUT),
        ),
        env=env
    )
    logger.info('Compose containers removed')


def compose_pull():
    logger.info('Pulling compose containers')
    run_cmd(
        cmd=('docker-compose', '-f', COMPOSE_PATH, 'pull'),
        env={
            'SKALE_DIR': SKALE_DIR
        }
    )


def compose_build():
    logger.info('Building compose containers')
    run_cmd(
        cmd=('docker-compose', '-f', COMPOSE_PATH, 'build'),
        env={
            'SKALE_DIR': SKALE_DIR
        }
    )


def get_up_compose_cmd(services):
    return ('docker-compose', '-f', COMPOSE_PATH, 'up', '-d', *services)


def compose_up(env):
    logger.info('Running base set of containers')

    if 'SGX_CERTIFICATES_DIR_NAME' not in env:
        env['SGX_CERTIFICATES_DIR_NAME'] = SGX_CERTIFICATES_DIR_NAME

    run_cmd(cmd=get_up_compose_cmd(BASE_COMPOSE_SERVICES), env=env)
    if str_to_bool(env.get('MONITORING_CONTAINERS', '')):
        logger.info('Running monitoring containers')
        run_cmd(cmd=get_up_compose_cmd(MONITORING_COMPOSE_SERVICES), env=env)
    if 'TG_API_KEY' in env and 'TG_CHAT_ID' in env:
        logger.info('Running containers for Telegram notifications')
        run_cmd(cmd=get_up_compose_cmd(NOTIFICATION_COMPOSE_SERVICES), env=env)


def docker_prune(all_artifacts=False):
    logger.info('Removing unused docker artifacts')
    cmd = ['docker', 'system', 'prune']
    if all_artifacts:
        cmd.append('-af')
    run_cmd(cmd=cmd)
