import click

from pypinfo.core import build_query, create_client, parse_query_result, tabulate
from pypinfo.db import get_credentials, set_credentials
from pypinfo.fields import (
    Project, Date, Month, Year, Country, Version, PythonVersion, Percent3,
    Percent2, Installer, InstallerVersion, SetuptoolsVersion, System,
    SystemRelease, Implementation, ImplementationVersion, OpenSSLVersion,
    Distro, DistroVersion, CPU
)

CONTEXT_SETTINGS = {
    'max_content_width': 300
}
COMMAND_MAP = {
    'project': Project,
    'version': Version,
    'pyversion': PythonVersion,
    'percent3': Percent3,
    'percent2': Percent2,
    'impl': Implementation,
    'impl-version': ImplementationVersion,
    'openssl': OpenSSLVersion,
    'date': Date,
    'month': Month,
    'year': Year,
    'country': Country,
    'installer': Installer,
    'installer-version': InstallerVersion,
    'setuptools-version': SetuptoolsVersion,
    'system': System,
    'system-release': SystemRelease,
    'distro': Distro,
    'distro-version': DistroVersion,
    'cpu': CPU,
}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('project', required=False)
@click.argument('fields', nargs=-1, required=False)
@click.option('--run/--test', default=True, help='--test simply prints the query.')
@click.option('--auth', '-a', help='Path to Google credentials JSON file.')
@click.option('--timeout', '-t', type=int, default=120000,
              help='Milliseconds. Default: 120000 (2 minutes)')
@click.option('--limit', '-l', help='Maximum number of query results. Default: 20')
@click.option('--days', '-d', help='Number of days in the past to include. Default: 30')
@click.option('--start-date', '-sd', help='Must be negative. Default: -31')
@click.option('--end-date', '-ed', help='Must be negative. Default: -1')
@click.option('--where', '-w', help='WHERE conditional. Default: file.project = "project"')
@click.option('--order', '-o', help='Field to order by. Default: download_count')
@click.pass_context
def pypinfo(ctx, project, fields, run, auth, timeout, limit, days,
            start_date, end_date, where, order):
    """Valid fields are:\n
    project | version | pyversion | percent3 | percent2 | impl | impl-version |\n
    openssl | date | month | year | country | installer | installer-version |\n
    setuptools-version | system | system-release | distro | distro-version | cpu
    """
    if auth:
        set_credentials(auth)
        click.echo('Credentials location set to "{}".'.format(get_credentials()))
        return

    if project is None and not fields:
        click.echo(ctx.get_help())
        return

    parsed_fields = []
    for field in fields:
        parsed = COMMAND_MAP.get(field)
        if parsed is None:
            raise ValueError('"{}" is an unsupported field.'.format(field))
        parsed_fields.append(parsed)

    built_query = build_query(
        project, parsed_fields, limit=limit, days=days, start_date=start_date,
        end_date=end_date, where=where, order=order
    )

    if run:
        client = create_client(get_credentials())
        query = client.run_sync_query(built_query)
        query.timeout_ms = timeout
        query.run()
        click.echo(tabulate(parse_query_result(query)))
    else:
        click.echo(built_query)
