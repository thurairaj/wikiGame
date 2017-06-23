import urllib
import json
from lxml import html



class WikiGameEngine:
    def __init__(self, maxhop=8):
        self.start = ""
        self.end = ""
        self.pool = []
        self.history = {}
        self.wiki_link = "https://en.wikipedia.org"
        self.maxhop = maxhop
        self.cache = {}

    def set_param(self, start, end):
        self.start = start
        self.end = end

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
        while self.pool :
            (prev, hop, current) = self.pool.pop(0)

            if prev_hop < hop:
                print prev_hop, hop
                if result_from_cache:
                    hop += self.retrive_result(result_from_cache)
                    return self.backtrack_hop(self.end, hop)

                prev_hop = hop
                print "hop change"

                if hop > self.maxhop:
                    break


            page = html.fromstring(urllib.urlopen(current).read())
            for a in  page.xpath('//div[@id="mw-content-text"]//a[@href]'):
                link = self.wiki_link + a.attrib["href"]

                if not (a.attrib["href"].startswith("/wiki") and a.text and link not in self.history):
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
            (end, text) = self.history[end]
            result.insert(0, {"index" : hop, "origin" : end, "text": text})

            hop -= 1

        print json.dumps(data)
        self.cache[(self.start, self.end)] = result

        return json.dumps(data)

    def retrive_result(self, key):
        print "untilize cache"
        history = self.cache[key]
        for i in range(0, len(history)-1, 1):
            row = history[i]
            nrow = history[i+1]

            self.history[nrow["origin"]] = (row["origin"], row["text"])

        row = history[-1]
        self.history[self.end] = (row["origin"], row["text"])
        return len(history)

    def ping(self):
        return "ok : "  + self.wiki_link