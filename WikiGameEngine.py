import urllib
import json
from lxml import html

class WikiGameEngine:
    def __init__(self,memCache=None, maxhop=8):
        self.start = ""
        self.end = ""
        self.pool = []
        self.history = {}
        self.wiki_link = "https://en.wikipedia.org"
        self.maxhop = maxhop
        self.cache = memCache
        print "memCache", memCache

    def set_param(self, start, end):
        self.start = start.replace(" ", "_")
        self.end = end.replace(" ", "_")

    def initialization(self):
        if not (self.start and self.end):
            return 0

        self.pool = [("", 0, self.start)]
        self.history = {self.start: ("", "")}
        return 1

    def crawl(self):
        print "Searching for " + self.end

        if not self.initialization():
            return ""
        prev_hop = 0
        result_from_cache = None

        # found the result from cache
        if (self.start, self.end) in self.cache:
            return self.backtrack_hop(self.end, self.retrive_result((self.start, self.end)))


        while self.pool :
            #get the first element from the pool
            (prev, hop, current) = self.pool.pop(0)

            if prev_hop < hop:
                print prev_hop, hop
                if result_from_cache:
                    return self.backtrack_hop(self.end, hop + self.retrive_result(result_from_cache))
                if hop > self.maxhop:
                    break
                prev_hop = hop

            page = html.fromstring(urllib.urlopen(current).read())

            for a in  page.xpath('//div[@id="mw-content-text"]//a[@href]'):

                link = self.wiki_link + a.attrib["href"]

                if not (a.attrib["href"].startswith("/wiki") and link not in self.history):
                    continue

                self.history[link] = (current, a.text)
                self.pool.append((current, hop+1, link))

                if link == self.end:
                    return self.backtrack_hop(self.end, hop+1)

                if (link, self.end) in self.cache:
                    if result_from_cache :
                        if len(self.cache[result_from_cache]) > len(self.cache[(link, self.end)]):
                            result_from_cache = (link, self.end)
                    else:
                        result_from_cache = (link, self.end)

        return "no_result"

    def backtrack_hop(self, end, hop):
        data = {"result" : []}
        result = data["result"]

        while hop > 0:
            next_link = end
            (end, text) = self.history[end]
            result.insert(0, {"index" : hop, "origin" : end, "next_text": text, "next_link" : next_link})
            hop -= 1

        print json.dumps(data)
        length_of_result = len(result)
        for i in range(0, length_of_result):
            cur = result[i]
            self.cache[(self.start, cur["next_link"])] = result[0:i+1]

        data["status"] = "SUCCESS"
        return json.dumps(data)

    def retrive_result(self, key):
        print "untilize cache"
        history = self.cache[key]
        for i in range(0, len(history)-1, 1):
            row = history[i]
            nrow = history[i+1]

            self.history[nrow["origin"]] = (row["origin"], row["next_text"])

        row = history[-1]
        self.history[self.end] = (row["origin"], row["next_text"])
        return len(history)

    def ping(self):
        return "ok : "  + self.wiki_link