import click
import requests
import praw
import qrcode

REDDIT_URL = "https://www.reddit.com/.json"

available_commands = [
    "showmainpage",
    "help",
    "exit",
    "login"
]

reddit_instance = None

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
    click.echo("2. login - Login to your Reddit account")
    click.echo("3. exit - Exit the application")

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

@reddit_cli.command()
@click.option('--client-id', prompt=True, help='Your Reddit app client ID')
@click.option('--client-secret', prompt=True, hide_input=True, help='Your Reddit app client secret')
@click.option('--username', prompt=True, help='Your Reddit username')
@click.option('--password', prompt=True, hide_input=True, help='Your Reddit password')
def login(client_id, client_secret, username, password):
    global reddit_instance
    try:
        try:
            with open('cookies.lenny', 'r') as f:
                overwrite_choice = click.prompt("You are already logged in. Do you want to overwrite your current login?", type=click.Choice(['y', 'n']))
                if overwrite_choice == 'y':
                    pass
                else:
                    return
        except FileNotFoundError:
            pass
        if client_id is None or client_secret is None:
            click.echo("\n")
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data("https://www.reddit.com/prefs/apps")
            qr.make(fit=True)
            qr_console = qr.print_ascii(invert=True)
            click.echo(qr_console)
            click.echo("")

            click.echo("To get your client ID and client secret, follow these steps:\n")
            click.echo("1. Go to https://www.reddit.com/prefs/apps or scan the qr code above.")
            click.echo('2. Click on "are you a developer? create an app...".')
            click.echo("3. Fill in the form with the following details:")
            click.echo("   - 'name': Cli.")
            click.echo("   - 'app type': Choose 'script'.")
            click.echo("   - 'description': You can leave this blank.")
            click.echo("   - 'about url': You can leave this blank.")
            click.echo("   - 'redirect uri': Type 'http://localhost:8080'.")
            click.echo("4. After creating the app, you will see the client ID and the client secret.\n")

        if username == None:
            username = click.prompt("Please enter your reddit username")
        if password == None:
            password = click.prompt("Please enter your reddit password")
        if client_id == None:
            client_id = click.prompt("Please enter your client id")
        if client_secret == None:
            client_secret = click.prompt("Please enter your client secret")

        reddit_instance = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent='RedditCLI/0.1'
        )
        # Test the login by fetching the user's info
        reddit_instance.user.me()
        click.echo("")
        click.echo("Login successful! You are now logged in.")
        save_login = click.prompt("Should this login data be locally saved under ./cookies.lenny for the next time?", type=click.Choice(['y', 'n']))
        if save_login == 'y':
            with open('cookies.lenny', 'w') as f:
                f.write(f"{client_id}\n{client_secret}\n{username}\n{password}")
            click.echo("Login data saved successfully.")

    except Exception as e:
        click.echo(f"Login failed: {e}")

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


    try: 
        with open('cookies.lenny', 'r') as f:
            lines = f.readlines()
            client_id = lines[0].strip()
            client_secret = lines[1].strip()
            username = lines[2].strip()
            password = lines[3].strip()
            reddit_instance = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent='RedditCLI/0.1'
            )

        print("Welcome back, " + reddit_instance.user.me().name + "!")
    except:
        None

    reddit_cli()