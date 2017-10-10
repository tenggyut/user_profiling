import scrapy
import re
import json
import requests
import codecs
import traceback
from my_spiders.items import WeiboAccountInfo, WeiboPost, WeiboLink, LikeItem
from scrapy.selector import Selector

class WeiboSpider(scrapy.Spider):
    name = "weibo"
    start_urls = []

    def __init__(self):
        with open("seeds") as f:
            for line in f:
                if not line.strip().startswith("#") and len(line) > 0:
                    self.start_urls.append("http://m.weibo.cn/u/%s" % line.strip())

    def parse(self, response):
        return self.extractAccountInfo(response)

    def extractAccountInfo(self, response):
        informationItems = WeiboAccountInfo()
        raw_json = json.loads(response.xpath("//script[1]/text()").extract()[1].split("window.$render_data = ")[1].replace("'","\"").replace(";", ""))
        page_json = raw_json["stage"]["page"]
        informationItems["account_id"] = page_json[1]["id"]
        informationItems["nickname"] = page_json[1]["name"]
        informationItems["profile_img"] = page_json[1]["avatar_hd"]

        if page_json[1]["ta"] == u'\u4ed6':
            informationItems["gender"] = "male" 
        else:
            informationItems["gender"] = "female"

        informationItems["intro"] = page_json[1]["description"]
        informationItems["post_count"] = page_json[1]["mblogNum"]
        informationItems["follower_count"] = page_json[1]["fansNum"]
        informationItems["following_count"] = page_json[1]["attNum"]
        informationItems["like_count"] = page_json[1]["favourites_count"]
        informationItems["join_date"] = page_json[1]["created_at"]
        informationItems["verified"] = page_json[1]["verified"]
        informationItems["verified_reason"] = page_json[1]["verified_reason"]

        r = requests.get("http://weibo.cn/%s/info" % informationItems["account_id"], cookies=response.request.cookies)

        if r.status_code == 200:
            selector = Selector(text=r.content)
            text1 = ";".join(selector.xpath('body/div[@class="c"]/text()').extract())
            birthday = re.findall(u'\u751f\u65e5[:|\uff1a](.*?);', text1) 
            place = re.findall(u'\u5730\u533a[:|\uff1a](.*?);', text1)
            sexorientation = re.findall(u'\u6027\u53d6\u5411[:|\uff1a](.*?);', text1)
            marriage = re.findall(u'\u611f\u60c5\u72b6\u51b5[:|\uff1a](.*?);', text1)
            tmp_gender = re.findall(u'\u6027\u522b[:|\uff1a](.*?);', text1)

            if birthday:
                try:
                    birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
                    informationItems["birthday"] = birthday - datetime.timedelta(hours=8)
                except Exception:
                    pass

            if place:
                informationItems["cur_location"] = place[0]
            
            if sexorientation and tmp_gender:
                if sexorientation[0] == tmp_gender[0]:
                    informationItems["sexorientation"] = "gay"
                else:
                    informationItems["sexorientation"] = "heterosexual"
            if marriage:
                informationItems["marriage"] = marriage[0]

        tags_r = requests.get("http://weibo.cn/account/privacy/tags/?uid=%s" % informationItems["account_id"], cookies=response.request.cookies)
        if tags_r.status_code == 200:
            tags_selector = Selector(text=tags_r.content)
            informationItems["tags"] = ",".join(tags_selector.xpath("//a[contains(@href, '/search/?keyword')]/text()").extract())

        yield informationItems

        #qq = page_json[1]["name"]
        #email = page_json[1]["name"]
        #site = page_json[1]["name"]

        containerId = raw_json["common"]["containerid"]
        
        weibo_url = "http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO&page=1" % containerId
        yield scrapy.Request(url= weibo_url, callback=self.extractPosts)

        follower_url = "http://m.weibo.cn/page/json?containerid=%s_-_FANS&accountId=%s&page=1" % (containerId, page_json[1]["id"])
        yield scrapy.Request(url= follower_url, callback=self.extractFollowersOrFollowings)
        
        following_url = "http://m.weibo.cn/page/json?containerid=%s_-_FOLLOWERS&accountId=%s&page=1" % (containerId, page_json[1]["id"])
        yield scrapy.Request(url= following_url, callback=self.extractFollowersOrFollowings)

        like_weibo_url = "http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_LIKE_WEIBO&accountId=%s&page=1" % (containerId, page_json[1]["id"])
        yield scrapy.Request(url= like_weibo_url, callback=self.extractLikesWiebo)

        like_img_url = "http://m.weibo.cn/page/json?containerid=103003index%s_-_photo_like_l&accountId=%s&page=1" % (page_json[1]["id"], page_json[1]["id"])
        yield scrapy.Request(url= like_img_url, callback=self.extractLikesImg)

        like_place_url = "http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_LIKE_PLACE&accountId=%s&page=1" % (containerId, page_json[1]["id"])
        yield scrapy.Request(url= like_img_url, callback=self.extractLikesPlacesAndAudioAndMovie)

        like_audio_url = "http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_LIKE_AUDIO&accountId=%s&page=1" % (containerId, page_json[1]["id"])
        yield scrapy.Request(url= like_audio_url, callback=self.extractLikesPlacesAndAudioAndMovie)

        like_movie_url = "http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_LIKE_MOVIE&accountId=%s&page=1" % (containerId, page_json[1]["id"])
        yield scrapy.Request(url= like_movie_url, callback=self.extractLikesPlacesAndAudioAndMovie)
        
    def extractPosts(self, response):
        posts_json = json.loads(response.body)

        try:
            for post_card_json in posts_json["cards"][0]["card_group"]:
                post = WeiboPost()
                post_json = post_card_json["mblog"]
                post["post_id"] = post_json["idstr"]
                post["user_id"] = str(post_json["user"]["id"])
                post["user_nickname"] = post_json["user"]["screen_name"]
                post["content"] = post_json["text"]
                post["post_date"] = str(post_json["created_timestamp"])

                hot_tags = []
                for hot_tag in post_json["hot_weibo_tags"]:
                    hot_tags.append(hot_tag["tag_name"])
                
                post["tags"] = ",".join(hot_tags)

                if "retweeted_status" in post_json:
                    post["post_type"] = "retweet"
                    next_account_url = "http://m.weibo.cn/u/%s" % str(post_json["retweeted_status"]["user"]["id"])
                    yield scrapy.Request(url= next_account_url, callback=self.parse)
                
                    retweet_link_item = WeiboLink()
                    retweet_link_item["linkee_id"] = post["user_id"]
                    retweet_link_item["linker_id"] = str(post_json["retweeted_status"]["user"]["id"])
                    retweet_link_item["link_type"] = "retweet"
                    retweet_link_item["link_date"] = post["post_date"]
                    retweet_link_item["link_content_id"] = post["post_id"]
                    yield retweet_link_item

                else:
                    post["post_type"] = "direct"

                post["endpoint"] = post_json["source"]
                post["upvote_count"] = str(post_json["like_count"])
                post["reply_count"] = str(post_json["comments_count"])
                post["forward_count"] = str(post_json["reposts_count"])
            
                img_url_template = "http://ww4.sinaimg.cn/large/%s.jpg"
                pic_urls = []
                for pic_id in post_json["pic_ids"]:
                    pic_urls.append(img_url_template % pic_id)

                post["pics"] = ",".join(pic_urls)

                yield post

                comment_url = "http://m.weibo.cn/single/rcList?format=cards&id=%s&type=comment&hot=0&page=1" % post["post_id"]
                yield scrapy.Request(url= comment_url, callback=self.extractReplies)
        except KeyError:
            traceback.print_exc()
            self.logger.warning("no posts")
        
        if posts_json["cards"][0]["mod_type"] == "mod/pagelist":
            cur_page = int(response.url.split("page=")[1].strip())
            next_page = cur_page + 1
            yield scrapy.Request(url= response.url.replace("page=" + str(cur_page), "page=" + str(next_page)), callback=self.extractPosts)

    def extractReplies(self, response):
        replies_json = json.loads(response.body)

        try:
            for post_json in replies_json[-1]["card_group"]:
                post = WeiboPost()
                post["post_id"] = str(post_json["id"])
                post["user_id"] = str(post_json["user"]["id"])
                post["user_nickname"] = post_json["user"]["screen_name"]
                post["content"] = post_json["text"]
                post["post_date"] = str(post_json["created_at"])
                post["post_type"] = "reply"

                post["endpoint"] = post_json["source"]
                post["upvote_count"] = str(post_json["like_counts"])
                post["reply_count"] = "0"
                post["forward_count"] = "0"

                if "reply_id" in post_json:
                    reply_link_item = WeiboLink()
                    reply_link_item["linkee_id"] = post["user_id"]
                    reply_link_item["linker_id"] = "linker_id_placeholder"
                    reply_link_item["link_type"] = "reply"
                    reply_link_item["link_date"] = post["post_date"]
                    reply_link_item["link_content_id"] = post_json["reply_id"]
                    yield reply_link_item

                yield post
        except KeyError:
            traceback.print_exc()
            self.logger.warning("no replies")
        
        if replies_json[-1]["mod_type"] == "mod/pagelist":
            cur_page = int(response.url.split("page=")[1].strip())
            next_page = cur_page + 1
            yield scrapy.Request(url= response.url.replace("page=" + str(cur_page), "page=" + str(next_page)), callback=self.extractReplies)


    def extractFollowersOrFollowings(self, response):
        followers_json = json.loads(response.body)
        account_id = re.findall('accountId=(\d+)', response.url)[0]

        if "FANS" in response.url:
            linkee_key = "linkee_id"
            linker_key = "linker_id"
        else:
            linkee_key = "linker_id"
            linker_key = "linkee_id" 

        try:
            for follower_json in followers_json["cards"][0]["card_group"]:
                follower_id = str(follower_json["user"]["id"])

                follower_link_item = WeiboLink()
                follower_link_item[linkee_key] = follower_id
                follower_link_item[linker_key] = account_id
                follower_link_item["link_type"] = "following"
                follower_link_item["link_date"] = ""
                follower_link_item["link_content_id"] = ""
                yield follower_link_item

                follower_url = "http://m.weibo.cn/u/%s" % follower_id
                yield scrapy.Request(url = follower_url, callback = self.parse)
        except KeyError:
            traceback.print_exc()
            self.logger.warning("no follower or friend")

        if followers_json["cards"][0]["mod_type"] == "mod/pagelist":
            cur_page = int(response.url.split("page=")[1].strip())
            next_page = cur_page + 1
            yield scrapy.Request(url= response.url.replace("page=" + str(cur_page), "page=" + str(next_page)), callback=self.extractFollowersOrFollowings)


    def extractLikesWiebo(self, response):
        like_weibos_json = json.loads(response.body)
        account_id = re.findall('accountId=(\d+)', response.url)[0]

        try:
            for like_card_json in like_weibos_json["cards"][0]["card_group"]:
                like_json = like_card_json["mblog"]
                like_weibo_user_id = str(like_json["user"]["id"])

                like_weibo_link_item = WeiboLink()
                like_weibo_link_item["linkee_id"] = account_id
                like_weibo_link_item["linker_id"] = like_weibo_user_id
                like_weibo_link_item["link_type"] = "like_weibo"
                like_weibo_link_item["link_date"] = ""
                like_weibo_link_item["link_content_id"] = like_json["idstr"]
                yield like_weibo_link_item

                like_weibo_user_url = "http://m.weibo.cn/u/%s" % like_weibo_user_id
                yield scrapy.Request(url = like_weibo_user_url, callback = self.parse)
        except KeyError:
            traceback.print_exc()
            self.logger.warning("no liked weibo")

        if like_weibos_json["cards"][0]["mod_type"] == "mod/pagelist":
            cur_page = int(response.url.split("page=")[1].strip())
            next_page = cur_page + 1
            yield scrapy.Request(url= response.url.replace("page=" + str(cur_page), "page=" + str(next_page)), callback=self.extractLikesWiebo)

    def extractLikesImg(self, response):
        like_imgs_json = json.loads(response.body)
        account_id = re.findall('accountId=(\d+)', response.url)[0]

        try:
            for like_img_json in like_imgs_json["cards"][0]["card_group"][0]["pics"]:

                like_item = LikeItem()
                like_item["item_type"] = "img"
                like_item["pic"] = like_img_json["pic_ori"]
                like_item["user_id"] = account_id
                yield like_item
        except KeyError:
            traceback.print_exc()
            self.logger.warning("no like imgs")

        if like_imgs_json["cards"][0]["mod_type"] == "mod/pagelist":
            cur_page = int(response.url.split("page=")[1].strip())
            next_page = cur_page + 1
            yield scrapy.Request(url= response.url.replace("page=" + str(cur_page), "page=" + str(next_page)), callback=self.extractLikesImg)

    def extractLikesPlacesAndAudioAndMovie(self, response):
        like_places_json = json.loads(response.body)
        account_id = re.findall('accountId=(\d+)', response.url)[0]

        if "AUDIO" in response.url:
            item_type = "audio"
        elif "PLACE" in response.url:
            item_type = "place"
        else:
            item_type = "movie"

        try:
            for like_place_json in like_places_json["cards"][0]["card_group"]:

                like_item = LikeItem()
                like_item["item_type"] = item_type
                like_item["title"] = like_place_json["title_sub"]
                like_item["desc"] = like_place_json["desc1"]
                like_item["pic"] = like_place_json["pic"]
                like_item["url"] = like_place_json["scheme"]
                like_item["upvote_count"] = re.findall(u'(\d+)\u4eba\u8d5e\u8fc7', like_place_json["desc2"])
                like_item["user_id"] = account_id
                yield like_item
        except KeyError:
            traceback.print_exc()
            self.logger.warning("no liked items")

        if like_places_json["cards"][0]["mod_type"] == "mod/pagelist":
            cur_page = int(response.url.split("page=")[1].strip())
            next_page = cur_page + 1
            yield scrapy.Request(url= response.url.replace("page=" + str(cur_page), "page=" + str(next_page)), callback=self.extractLikesPlacesAndAudioAndMovie)
