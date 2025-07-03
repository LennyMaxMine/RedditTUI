from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Static, Button
from datetime import datetime, timedelta
from utils.logger import Logger

class RateLimitScreen(Widget):
    def __init__(self, reddit_service):
        super().__init__()
        self.reddit_service = reddit_service
        self.logger = Logger()

    def compose(self) -> ComposeResult:
        self.logger.info("Composing rate limit screen")
        with Container(id="rate_limit_container"):
            with Vertical(id="rate_limit_content"):
                yield Static("Reddit API Rate Limit Information", classes="rate_title")
                with ScrollableContainer():
                    yield Static(id="current_usage")
                    yield Static(id="historical_usage")
                    yield Static(id="reset_info")
                    yield Static(id="recommendations")
                yield Button("Refresh", id="refresh_button")

    def on_mount(self) -> None:
        self.logger.info("Rate limit screen mounted")
        self.update_rate_info()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh_button":
            self.update_rate_info()

    def update_rate_info(self) -> None:
        self.logger.info("Updating rate limit information")
        try:
            if not self.reddit_service:
                self.logger.error("Reddit service is not initialized")
                self.query_one("#current_usage").update("Error: Reddit service not initialized")
                return

            current_usage_widget = self.query_one("#current_usage")
            historical_usage_widget = self.query_one("#historical_usage")
            reset_info_widget = self.query_one("#reset_info")
            recommendations_widget = self.query_one("#recommendations")

            rate_info = self.reddit_service.get_rate_limit_info()
            self.logger.info(f"Retrieved rate limit info: {rate_info}")

            remaining = rate_info.get('remaining', 0)
            used = rate_info.get('used', 0)
            reset_time = rate_info.get('time_until_reset', 0)
            total_calls = (remaining or 0) + (used or 0)

            self.logger.info(f"Rate limit stats - Remaining: {remaining}, Used: {used}, Reset time: {reset_time}")

            remaining_class = "rate_critical" if (remaining or 0) < 50 else "rate_warning" if (remaining or 0) < 200 else "rate_good"
            
            current_usage = f"""
[bold]Current Usage[/bold]
-----------------
Remaining API calls: [class={remaining_class}]{remaining}[/]
Used API calls: {used}
Total calls made: {total_calls}
"""
            current_usage_widget.update(current_usage)

            usage_percent = (used / total_calls) * 100 if total_calls > 0 else 0
            historical_usage = f"""
[bold]Historical Usage[/bold]
-------------------
Usage percentage: {usage_percent:.1f}%
Average calls per minute: {used / (reset_time / 60) if reset_time > 0 else 0:.1f}
"""
            historical_usage_widget.update(historical_usage)

            reset_time_str = str(timedelta(seconds=int(reset_time)))
            reset_info = f"""
[bold]Reset Information[/bold]
-------------------
Time until reset: {reset_time_str}
Next reset at: {(datetime.now() + timedelta(seconds=reset_time)).strftime('%H:%M:%S')}
"""
            reset_info_widget.update(reset_info)

            recommendations = "[bold]Recommendations[/bold]\n-------------------\n"
            if (remaining or 0) < 50:
                recommendations += "[class=rate_critical]⚠️ Critical: You are running low on API calls. Consider reducing your request frequency.[/]\n"
            elif (remaining or 0) < 200:
                recommendations += "[class=rate_warning]⚠️ Warning: You have less than 200 API calls remaining. Be mindful of your request frequency.[/]\n"
            else:
                recommendations += "[class=rate_good]✓ Good: You have plenty of API calls remaining.[/]\n"

            if reset_time < 300:
                recommendations += "[class=rate_warning]⚠️ Rate limit will reset soon. Consider waiting before making more requests.[/]\n"
            elif reset_time < 900:
                recommendations += "[class=rate_warning]ℹ️ Rate limit will reset in less than 15 minutes.[/]\n"

            recommendations_widget.update(recommendations)

        except Exception as e:
            self.logger.error(f"Error updating rate limit info: {str(e)}", exc_info=True)
            self.notify(f"Error updating rate limit info: {str(e)}", severity="error") 
