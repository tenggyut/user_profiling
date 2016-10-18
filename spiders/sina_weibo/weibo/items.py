# -*- coding: utf-8 -*-

from scrapy import Item, Field
import time
import datetime

def paresDate(dateString):
    if len(dateString.strip()) <= 0:
        return -1l
    else:
        return int(time.mktime(datetime.datetime.strptime(dateString, "%I:%M %p - %d %b %Y").timetuple()))


class WeiboAccountInfo(Item):
    account_id = Field()
    nickname = Field()
    profile_img = Field()
    gender = Field()
    birthday = Field()
    intro = Field()
    cur_location = Field()
    post_count = Field()
    follower_count = Field()
    following_count = Field()
    like_count = Field()
    join_date = Field()
    verified = Field()
    verified_reason = Field()
    tags = Field()
    qq = Field()
    email = Field()
    site = Field()
    sexorientation = Field()
    marriage = Field()

    def rowkey(self):
        return self["account_id"]

    def table_name(self):
        return "weibo:account_info"

class WeiboPost(Item):
    post_id = Field()
    user_id = Field()
    user_nickname = Field()
    content = Field()
    post_date = Field()
    location = Field()
    tags = Field()
    post_type = Field()
    endpoint = Field()
    upvote_count = Field()
    reply_count = Field()
    forward_count = Field()

    def rowkey(self):
        return self["post_id"]

    def table_name(self):
        return "weibo:post"

class LikeItem(Item):
    user_id = Field()
    item_type = Field()
    title = Field()
    desc = Field()
    pic = Field()
    url = Field()
    upvote_count = Field()

    def rowkey(self):
        return self["post_id"]

    def table_name(self):
        return "weibo:likes"     

class WeiboLink(Item):
    linker_id = Field()
    linkee_id = Field()
    link_type = Field()
    link_date = Field()
    link_content_id = Field()

    def rowkey(self):
        return self["linkee_id"] + ",#," + self["link_type"] + ",#," + self["linker_id"] + self["link_date"]

    def table_name(self):
        return "weibo:link"