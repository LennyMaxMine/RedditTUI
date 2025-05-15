import click
import requests

REDDIT_URL = "https://www.reddit.com/.json"

available_commands = [
    "showmainpage",
    "help",
    "exit"
]

@click.group(invoke_without_command=True)
@click.pass_context
def reddit_cli(ctx):
    if not ctx.invoked_subcommand:
        while True:
            try:
                command = input("\nuser@reddit-cli:~$ ").strip()
                if command.lower() == 'exit':
                    click.echo("Goodbye, hope to see you soon!")
                    break
                ctx.invoke(ctx.command.get_command(ctx, command))
            except Exception as e:
                click.echo(f"Error: {e}")

@reddit_cli.command()
def help():
    click.echo("Available commands:")
    click.echo("1. showmainpage - Show the main page of Reddit")
    click.echo("2. exit - Exit the application")

@reddit_cli.command()
@click.option('--limit', default=5, help='Number of posts to display')
def showmainpage(limit):
    headers = {'User-Agent': 'RedditCLI/0.1'}
    try:
        response = requests.get(REDDIT_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        posts = data['data']['children'][:limit]

        click.echo(f"\nTop {limit} posts from Reddit's front page:\n")
        for idx, post in enumerate(posts, start=1):
            title = post['data']['title']
            score = post['data']['score']
            url = post['data']['url']
            click.echo(f"{idx}. {title} (Score: {score})\n   {url}\n")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error fetching data: {e}")

if __name__ == '__main__':
    print(
"""██████╗ ███████╗██████╗ ██████╗ ██╗████████╗     ██████╗██╗     ██╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██╔════╝██║     ██║
██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║     ██║     ██║
██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ██║     ██║     ██║
██║  ██║███████╗██████╔╝██████╔╝██║   ██║       ╚██████╗███████╗██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝        ╚═════╝╚══════╝╚═╝""")
    print("                      Version 0.1 - Alpha\n\n")
    print("\nWelcome to Reddit CLI!")
    print("This command line interface of reddit was build with <3 in Germany by @lennymaxmine for the 2025 Hack Club Neighborhood.")
    print("This Project is still in its first few alpha hours, so please be patient with me. :D")
    print("For any bugs that occur or feedback that you may have, im always there in slack (@lenny) or on github (@lennymaxmine).")
    print("Hope you have a nice day and a great time using this cli!")
    print(f"\nAvailable commands: {', '.join(available_commands)}")
    print("Type 'exit' to quit the application & 'help' to see the available commands.\n")
    reddit_cli()