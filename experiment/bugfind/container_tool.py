"""Serve one MCP tool, `run`, that runs a bash command in a task's Docker container.

Claude Code starts this server over stdio. Messages are JSON-RPC 2.0, one per line:

    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "run", "arguments": {"command": "ls"}}}

The container is started with `--network none`, and the command runs as the host user in /testbed,
the bind mount of the task's working copy.

Usage:
    $ python3 container_tool.py <container id>
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


COMMAND_TIMEOUT_S = 600
OUTPUT_LIMIT_CHARS = 30_000
PROTOCOL_VERSION = '2025-06-18'
TESTBED_PATH = '/opt/conda/envs/testbed/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
TOOL = {
    'name': 'run',
    'description': (
        "Run a bash command in the repository's Docker container, in /testbed. /testbed has the same files as "
        "the current directory. The repository's Python environment is on PATH. The container has no network "
        f'access. A command is stopped after {COMMAND_TIMEOUT_S} s, and only the last {OUTPUT_LIMIT_CHARS} '
        'characters of output are returned.'
    ),
    'inputSchema': {
        'type': 'object',
        'properties': {'command': {'type': 'string', 'description': 'the bash command'}},
        'required': ['command'],
    },
}


def main() -> int:
    container = sys.argv[1]
    for line in sys.stdin:
        request = json.loads(line)
        if 'id' not in request:
            continue
        response = {'jsonrpc': '2.0', 'id': request['id'], **answerRequest(request, container)}
        sys.stdout.write(json.dumps(response) + '\n')
        sys.stdout.flush()
    return 0


def answerRequest(request: dict[str, object], container: str) -> dict[str, object]:
    """Answer one JSON-RPC request with a result member or an error member.

    Raises:
        Nothing. A malformed call gets a JSON-RPC error.
    """
    params = request.get('params')
    params = params if isinstance(params, dict) else {}
    match request.get('method'):
        case 'initialize':
            return {
                'result': {
                    'protocolVersion': params.get('protocolVersion', PROTOCOL_VERSION),
                    'capabilities': {'tools': {}},
                    'serverInfo': {'name': 'container', 'version': '1'},
                },
            }
        case 'tools/list':
            return {'result': {'tools': [TOOL]}}
        case 'tools/call':
            arguments = params.get('arguments')
            command = arguments.get('command') if isinstance(arguments, dict) else None
            if params.get('name') != TOOL['name'] or not isinstance(command, str):
                return {'error': {'code': -32602, 'message': 'expected the run tool with a string command'}}
            output, exit_code = runInContainer(container, command)
            return {'result': {'content': [{'type': 'text', 'text': output}], 'isError': exit_code != 0}}
        case 'ping':
            return {'result': {}}
        case _:
            return {'error': {'code': -32601, 'message': f'unknown method {request.get("method")}'}}


def runInContainer(container: str, command: str) -> tuple[str, int]:
    completed = subprocess.run(
        buildExecCommand(container, command),
        capture_output=True,
        text=True,
        errors='replace',
        check=False,
    )
    output = (completed.stdout + completed.stderr)[-OUTPUT_LIMIT_CHARS:]
    return f'{output}\n[exit code {completed.returncode}]', completed.returncode


def buildExecCommand(container: str, command: str) -> list[str]:
    # verify.py resolves the lint venv under HOME. The venv is mounted under the host's home path, so HOME
    # is that path. The host user can't write there in the container, so pylint and mypy caches go to /tmp
    return [
        'docker', 'exec', '-w', '/testbed',
        '-u', f'{os.getuid()}:{os.getgid()}',
        '-e', f'PATH={TESTBED_PATH}',
        '-e', f'HOME={Path.home()}',
        '-e', 'XDG_CACHE_HOME=/tmp/cache',
        '-e', 'PYLINTHOME=/tmp/cache/pylint',
        '-e', 'MYPY_CACHE_DIR=/tmp/cache/mypy',
        container,
        'timeout', '-k', '10', str(COMMAND_TIMEOUT_S), 'bash', '-c', command,
    ]  # fmt: skip


if __name__ == '__main__':
    sys.exit(main())
