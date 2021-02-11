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
        self.last_post_title = ""
        self.caption = ""
        self.file = ""
        self.url = ""
        self.is_photo = False
        self.is_gif = False
        self.nothing = False
        self.is_video = False
        self.wait_time = wait_time
        self.bot = Updater(token, use_context=True).bot
        self.chat = self.bot.get_chat(config.channel).username

    def wait(self, method: str):
        print(f"waiting after method: {method} for: {int(self.wait_time / 60)} minutes")
        print("resetting the values!")
        self.reset_values()
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
            url:str = post.url
            file = self.extract_file_name(post.url)
            print("AT_GET_POSTS: FileName: " + file)
            if len(file) == 0:
                continue
            posts.update({post.title:url})
            return posts

    def reset_values(self):
        self.nothing = False
        self.is_gif = False
        self.is_photo = False
        self.is_video = False
        self.url = ""
        self.file = ""

    def parse_posts(self):
        posts = self.get_posts(3)
        for title,url in posts.items():
            url:str = url
            if title == self.last_post_title:
                self.wait("NOTHING NEW")
            self.last_post_title = title
            file = self.extract_file_name(url)
            self.file = file
            self.url = url
            self.caption = f"{title}\n\n@{self.chat}"
            if file.endswith(".jepg") or file.endswith(".jpg") or file.endswith(".png"):
                self.is_photo = True
                break
            elif file.endswith(".gif"):
                self.is_gif = True
                break
            elif file.endswith(".mp4"):
                self.is_video = True
                break
            else:
                self.nothing = True
                continue
        try:
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
            elif self.is_video:
                self.bot.send_video (
                    caption=self.caption,
                    chat_id=config.channel,
                    video=open(self.file,"rb")
                )
                self.wait("VIDEO")
            else:
                self.wait("NOTHING")

            print("removing " + self.file)
            os.system(f"rm -rf {self.file}")

        except Exception as e:
            print(f"ERROR:{e}")


def main():
    track = tracker(config.telegram_token, 900)
    while True:
        track.parse_posts()


if __name__ == "__main__":
    main()
