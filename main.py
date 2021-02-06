import praw,config,re,requests,os
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
    def __init__(self,token,wait_time):
        self.last_post = ""
        self.wait_time = wait_time
        self.is_photo = False
        self.is_video = False
        self.is_gif = False
        self.nothing = False
        self.url = ""
        self.file = ""
        self.bot = Updater(token, use_context=True).bot
        self.chat = self.bot.getChat(config.channel).username
        self.caption = self.chat
        print(f"bot {self.bot.name} has started working!")
    
    def wait(self,method:str):
        print(f"waiting after method: {method}")
        sleep(self.wait_time)
        print("waiting has finished after method {method}")
        self.get_posts()
    
    def get_posts(self):
        while True:
    
            for sub in reddit.subreddit(config.CHANNEL_TO_TRACK).new(limit=3):
                if self.last_post == sub.title:
                    print("nothing new")
                    sleep(self.wait_time)
                self.url = str(sub.url)
    
                self.file = self.url.split("/")
                self.caption = f"{sub.title}\n\n@{self.chat}"
                if len(self.file) == 0:
                    self.file = re.findall("/(.*?)", self.url)
                self.file = self.file[-1]
                if self.file == "":
                    print("can't send this one! trying something else...")
                    self.nothing = True
                    continue
    
                self.last_post = sub.title
    
                try:
                    if self.url.endswith("gif"):
                        self.is_gif = True
                        break
                    elif self.url.endswith("jpg") or self.url.endswith("jpeg") or self.url.endswith("png"):
                        self.is_photo = True
                        break
    
                    elif self.url.lower().endswith("mov") or self.url.lower().endswith("mp4"):
                        self.is_video = True
                        break
    
                    else:
                        self.nothing = True
                        break
                except Exception as e:
                    print("ERROR at image download: " + str(e))
            try:
                if self.nothing:
                    print("unsupported format.. skipping...")
                    sleep(self.wait_time)
                    print("retrying now...")
                    self.get_posts()
                r = requests.get(self.url)
                print(self.file)
                with open(self.file,"wb") as f:
                    f.write(r.content)
    
                    if self.is_video:
                        self.bot.send_video(caption=self.caption,video=open(self.file,"rb"),chat_id=config.channel)
                        self.wait("VIDEO")
                    if self.is_gif:
                        self.bot.send_animation(caption=self.caption,animation=open(self.file,"rb"),chat_id=config.channel)
                        self.wait("GIF")
                    if self.is_photo:
                        self.bot.send_photo(caption=self.caption,chat_id=config.channel,photo=open(self.file,"rb"))
                        self.wait("PHOTO")
    
                print(self.file)
                print("removing " + self.file)
                os.system(f"rm -rf {self.file}")
    
            except Exception as e:
                print(f"ERROR:{e}")

def main():
    track = tracker(config.telegram_token,900)
    track.get_posts()

if __name__ == "__main__":
    main()
