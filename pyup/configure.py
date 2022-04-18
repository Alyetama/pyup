from pathlib import Path

import yaml


def write_configuration():
    _options = [
        'FILSERVER_HOST', 'FILSERVER_USERNAME', 'FILESERVER_PORT',
        'FILESERVER_DATA_PATH', 'DEFAULT_DOMAIN_NAME',
        'MONGODB_CONNECTION_STRING'
    ]

    cfg_help = {
        'MONGODB_CONNECTION_STRING':
        'MongoDB connection string – '
        'e.g., mongodb://USERNAME:PASSWORD@HOST:PORT - default: '
        'mongodb://admin:password@127.0.0.1:27017',
        'DEFAULT_DOMAIN_NAME':
        'Domain name to use for URLs – default: 127.0.0.1',
        'FILESERVER_PORT':
        'Port on which caddy file server should be listening – default: 8081',
        'FILESERVER_DATA_PATH':
        'Path to the data directory – i.e., the directory mapped to /srv – '
        'default: ./caddy_data',
        'FILSERVER_HOST':
        'IP address of the remote server – only if the file server is remote; '
        'optional',
        'FILSERVER_USERNAME':
        'Username on the remote server – only if the file server is remote; '
        'optional'
    }

    options = {k: input(f'{k} ({cfg_help[k]}): ') for k in _options}

    if not options['FILSERVER_HOST'] and not options['FILSERVER_USERNAME']:
        if not options['FILESERVER_DATA_PATH']:
            Path(f'{Path().cwd()}/caddy_data').mkdir(exist_ok=True,
                                                     parents=True)
            options.update(
                {'FILESERVER_DATA_PATH': f'{Path().cwd()}/caddy_data'})
        else:
            Path(options['FILESERVER_DATA_PATH']).mkdir(exist_ok=True,
                                                        parents=True)

    if not options['FILESERVER_PORT']:
        options.update({'FILESERVER_PORT': '8081'})
    if not options['DEFAULT_DOMAIN_NAME']:
        options.update({'DEFAULT_DOMAIN_NAME': '127.0.0.1'})
    if not options['MONGODB_CONNECTION_STRING']:
        options.update({
            'MONGODB_CONNECTION_STRING':
            'mongodb://admin:password@127.0.0.1:27017'
        })

    config = [{'options': options}]

    with open(f'{Path().home()}/.pyup', 'w') as cfg:
        data = yaml.dump(config, cfg)


if __name__ == '__main__':
    write_configuration()
