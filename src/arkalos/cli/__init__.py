import sys
import importlib

import arkalos.core.logger.log as Log
from arkalos.core.bootstrap import bootstrap

RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'

ENABLED_COMMANDS = {
    'init': 'Init the Arkalos starter project with the base folder structure and configuration.',
    'serve': 'Start Arkalos HTTP API Server.',
    'migrate': 'Run database migrations. (Optionally, provide a version to migrate).',
    'migrate:dwh': 'Run data warehouse migrations. (Optionally, provide a version to migrate).',
    'rollback': 'Rollbacks last database version\'s migrations.',
    'rollback:dwh': 'Rollbacks last data warehouse version\'s migrations.',
    'make:mw': 'Generate a new middleware class',
    'make:mig': 'Generate a new Database migration file. Provide a table name.',
    'make:mig:dwh': 'Generate a new Data Warehouse migration file. Provide a table name with optional namespace.'
}

def show_help():
    print()
    print(BLUE + 'Arkalos')
    print('The Python Framework for AI & Data Artisans')
    print('Copyright (c) 2025 Mev-Rael')
    print('v0.7.0 (Beta 7)')
    print()
    print("Available commands:" + RESET)
    for command in ENABLED_COMMANDS:
        print(f"  {GREEN}{command}{RESET} - {ENABLED_COMMANDS[command]}")
    print()
    print(f"{BLUE}Use '{GREEN}uv run arkalos <command>{BLUE}' to run a command.{RESET}")
    print()

def run_command(command):
    if command in ENABLED_COMMANDS:
        module = importlib.import_module(f'arkalos.cli.{command.replace(':', '_')}')
        module.run()
    else:
        print()
        print(f"Command '{command}' is not available. Please use a valid command.")
        print()

def main():
    try:
        if len(sys.argv) < 2:
            show_help()
            return
        
        command = sys.argv[1]
        if command != 'init':
            bootstrap().register()
        Log.logger()
        
        run_command(command)
    except Exception as e:
        Log.exception(e)



if __name__ == "__main__":
    main()
