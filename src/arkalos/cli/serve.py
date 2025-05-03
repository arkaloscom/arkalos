import argparse
from arkalos.core.config import config
from arkalos.core.http import http_server
from arkalos.core.bootstrap import bootstrap

def run():
    bootstrap().run()

    parser = argparse.ArgumentParser(
        prog='arkalos',
        description='Arkalos CLI: Friendly framework for AI & Data'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 'serve' command: starts HTTP server
    serve_parser = subparsers.add_parser('serve', help='Start Arkalos HTTP API Server')
    serve_parser.add_argument(
        '--host',
        default=config('app.host', '127.0.0.1'),
        help='Host to bind to'
    )
    serve_parser.add_argument(
        '--port',
        type=int,
        default=int(config('app.port', 8000)),
        help='Port to listen on'
    )
    cur_env = config('app.env', '').lower()
    serve_parser.add_argument(
        '--reload',
        action='store_true',
        default=cur_env in ['local'],
        help='Enable auto-reload on code changes'
    )

    serve_parser.add_argument(
        '--workers', 
        type=int, 
        default=int(config('app.workers', 1)),
        help='Number of worker processes to run'
    )

    args = parser.parse_args()

    if args.command == 'serve':
        server = http_server()
        server.run(host=args.host, port=args.port, reload=args.reload, workers=args.workers)
    else:
        parser.print_help()
