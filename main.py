import praw, config, re, requests, os
from time import sleep
from telegram.ext import *

reddit = praw.Reddit(
    client_id=config.reddit_client,
    client_secret=config.reddit_secret,
    user_agent='<console:bot_lol:0.0.1 by /u/cytoly>',
    username=config.username,
    password=config.reddit_password
)


class tracker:
    def __init__(self, token, wait_time):
        self.wait_time = wait_time
        self.is_photo = False
        self.is_gif = False
        self.nothing = False
        self.last_post_title = ""
        self.url = ""
        self.file = ""
        self.caption = ""
        self.bot = Updater(token, use_context=True).bot
        self.chat = self.bot.getChat(config.channel).username
        print(f"bot {self.bot.name} has started working!")

    def wait(self, method: str):
        print(f"waiting after method: {method}")
        sleep(self.wait_time)
        print(f"waiting has finished after method {method}")
        self.parse_posts()

    @staticmethod
    def extract_file_name(url:str) -> str:
        file = url.split("/")
        if len(file) == 0:
            file = re.findall("/(.*?)", url)
        file = file[-1]
        return file

    def get_posts(self,max_posts:int) -> dict:
        posts = {}
        for post in reddit.subreddit(config.CHANNEL_TO_TRACK).new(limit=max_posts):
            file = self.extract_file_name(post.url)
            if len(file) == 0:
                continue
            posts.update({post.title:post.url})
        return posts

    def parse_posts(self):
        while True:
            posts = self.get_posts(3)
            for title,url in posts.items():
                url:str = url
                if title == self.last_post_title:
                    self.wait("NOTHING NEW")
                file = self.extract_file_name(url)
                self.file = file
                self.url = url
                self.last_post_title = title
                self.caption = f"{title}\n\n@{self.chat}"
                if file.endswith("jepg") or file.endswith("jpg") or file.endswith("png"):
                    self.is_photo = True
                    break
                elif file.endswith("gif"):
                    self.is_gif = True
                    break
                else:
                    self.nothing = True
                    continue
            try:
                if self.nothing:
                    self.wait("UNSUPPORTED")
                request = requests.get(self.url)
                with open(self.file, "wb") as f:
                    f.write(request.content)

                if self.is_gif:
                    self.bot.send_animation(
                        caption=self.caption,
                        animation=open(self.file, "rb"),
                        chat_id=config.channel
                    )
                    self.wait("GIF")

                elif self.is_photo:
                    self.bot.send_photo(
                        caption=self.caption,
                        chat_id=config.channel,
                        photo=open(self.file, "rb")
                    )
                    self.wait("PHOTO")

                print(self.file)
                print("removing " + self.file)
                os.system(f"rm -rf {self.file}")

            except Exception as e:
                print(f"ERROR:{e}")


def main():
    track = tracker(config.telegram_token,900)
    print(f"{track.bot.username} has started")
    track.parse_posts()


if __name__ == "__main__":
    main()
