"""
YleChatScraper.py

A command line tool for scraping live chat logs from past chat streams.
See more: https://chat.yle.fi/

"""
import requests
from rich.console import Console
from rich.prompt import Prompt
from datetime import datetime

class YleChatScraper:
    def __init__(self):
        # These are the client credentials used by the official Yle widget.
        self.app_key = "96647595e47c00b5d3ff13ad2bfff831"
        self.app_id  = "livefeed_chat_widget_prod"
        self.chat_endpoint = "https://chat-backend.api.yle.fi"
        self.version = "0.1"
        
        # Initialize the rich console for pretty output
        self.console = Console()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"YleChatScraper/{self.version} (python-requests/{requests.__version__}; +)"
        })
        self.params = {
            "app_key": self.app_key,
            "app_id": self.app_id
        }
        
        self.messages = []
        
    def start_process(self):
        self.log_message(
            [
                ""
                "[turquoise2][bold]Yle Chat Scraper[/bold]",
                "[turquoise2]by Juhani Astikainen",
                "",
                "[turquoise2]To get started, please provide the URL of the chat stream you want to scrape.",
                "",
                "[turquoise2]Here's some examples:",
                "[turquoise2]* umk24 [deep_sky_blue4](chat.yle.fi/umk24)",
                "[turquoise2]* presidentinvaalit24 [deep_sky_blue4](chat.yle.fi/presidentinvaalit24)",
                "",
            ]
        )

        self.url = Prompt().ask()
        self.livefeed_id = self.get_livefeed_id(self.url)

        if self.livefeed_id is None:
            self.log_error("Failed to get the internal stream ID from the page.")
            exit()

        # Stream found, carry on
        self.log_message(
            [
                f"[turquoise2]Found chat feed with ID:[/turquoise2] [deep_sky_blue4]{self.livefeed_id}"
            ]
        )
        
        # We have to go backwards in time to get all the messages - starting from here.
        current_timestamp = self.convert_unix_to_timestamp(datetime.now())
        
        while True:
            # Make a request to the chat API to get the latest messages
            messages = self.get_some_messages_before(current_timestamp)
            self.messages.extend(messages)
            self.log_message(
                [
                    f"[turquoise2]Scraped {len(self.messages)} total messages from the chat feed."
                ]
            )
            if len(messages) == 0:
                break
            
            last_message = messages[-1]
            current_timestamp = last_message["creationTime"]

        dump_file = open(f"YleChat_{self.url}.csv", "a+", encoding="utf-8")
        dump_file.write("comment_id,creation_time,acception_time,likes,author_type,author_id,author_nickname,content,reply_to_comment_id\n")
        
        for message in self.messages:
            quote_id = None
            
            try:
                quote_id = message["quote"]["quoteId"]
            except KeyError:
                pass
            
            dump_file.write(
                f"{message['commentId']}," +
                f"{message['creationTime']}," +
                f"{message['acceptionTime']}," +
                f"{message['likes']}," +
                f"{message['role']}," +
                f"{message['chatUser']['id']}," +
                f"{self.csv_sanitize(message['chatUser']['nick'])}," +
                f"{self.csv_sanitize(message['content'])}," +
                f"{quote_id}\n"
            )
            
        dump_file.close()
        
        self.log_message(
            [
                f"[medium_spring_green]Chat feed scraped successfully. Messages saved to YleChat_{self.url}.csv"
            ]
        )
            
    def get_some_messages_before(self, time):
        """Gets an unspecific amount of messages from the chat stream before a specific time, in reverse order.

        Args:
            time (string): String in ISO 8601 format.

        Returns:
            list[obj]: A list of message objects (dict)
        """
        message_request = self.session.get(
            f"{self.chat_endpoint}/v1/chats/{self.livefeed_id}/comments/before/{time}",
            params=self.params
        )
        return message_request.json()
    
    def log_error(self, error):
        """Logs a styled error to the console.

        Args:
            error (string): The error string.
        """
        self.console.print(f"[red][bold]Oops![/bold] {error}") 

    def log_message(self, messages):
        """Logs a styled message to the console.

        Args:
            messages (list[string]): The messages to log.
        """
        for message in messages:
            self.console.print(f"   {message}")
    
    def get_livefeed_id(self, stream_url):
        """Gets the livefeed ID from the chat stream URL by creating and scraping the stream page's HTML.

        Args:
            stream_url (string): The URL of the chat stream.
            
        Returns:
            string: The livefeed ID of the chat stream.
        """
        try:
            stream_page_html = requests.get(f"https://chat.yle.fi/{stream_url}").text
            livefeed_id = stream_page_html.split('<div id="yle-livefeed" data-id="')[1].split('"')[0]
        except (requests.ConnectionError):
            self.log_error(f"https://chat.yle.fi/{stream_url} could not be reached. Please check the URL and try again.") 
            return None
        except IndexError:
            return None

        
        return livefeed_id
    
    def parse_timestamp(self, timestamp_str):
        """Parses an ISO 8601 timestamp string into a datetime object.
        
        Args:
            timestamp_str (string): The ISO 8601 timestamp string to parse
        
        Returns:
            datetime: The parsed datetime object.
        """
        # Use strptime to parse the string into a datetime object
        timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.strptime(timestamp_str, timestamp_format)

    def convert_unix_to_timestamp(self, timestamp_obj):
        """Converts a timestamp to a stringified ISO 8601 format.

        Args:
            timestamp_obj (datetime): The timestamp object.

        Returns:
            string: The stringified ISO 8601 timestamp.
        """
        # Use strftime to convert the datetime object into a formatted string
        return timestamp_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def csv_sanitize(self, string):
        """Sanitizes a string for CSV output.

        Args:
            string (string): The string to sanitize.

        Returns:
            string: The sanitized string.
        """
        return string.replace(",", "").replace("\n", " ").replace("\"", "'")
    
if __name__ == "__main__":
    scraper = YleChatScraper()
    scraper.start_process()
