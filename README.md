# ylechatscraper
An utility script for scraping the community chat feed from a past YLE stream.

Here's an example of the data obtained using this tool:
https://www.kaggle.com/datasets/juhaniastikainen/yle-election-night-chat-logs

The data contains the following information for each message:
* Comment ID (as seen in YLE's api)
* Creation Time (the time the message was sent to YLE)
* Acception Time (the time YLE's moderation team approved the message to be seen)
* Likes (the amount of likes the comment received from others)
* Role (the role of the message author (writer / user, could be others))
* Chat user's ID
* Chat user's nickname (The user's chosen display name)
* The content of the message.
* The ID of the message being replied to, if applicable.
