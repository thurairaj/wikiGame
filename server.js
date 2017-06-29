var express = require('express');
var rp = require('request-promise');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const pythonHost = "http://192.168.0.12:8080";

var cache = {}


var app = express();
app.use(express.static('public'));

app.get('/', function (req, res) {
   res.sendFile( __dirname + "/" + "index.htm" );
})

app.get('/check_result', (req,res) => {
	var start = req.query.start;
	var end = req.query.end;
	var regex = /https:\/\/[a-z]{2}\.wikipedia\.org\/wiki\/.*/g;
	var response = {}

	if(!(start && end)){
		response.status = "ERROR";
		response.message = "Please provide both start and end url"
		res.end(JSON.stringify(response));
		return;
	}

	start.replace("http://", "https://");
	end.replace("http://", "https://");

	if(!(start.match(regex) && end.match(regex))){
		response.status = "ERROR";
		response.message = "Please provide both start and end wikipedia url"
		res.end(JSON.stringify(response));
		return;
	}

	var cache_result = cache[[start, end]] ;
	if(cache_result && cache_result.status == "SUCCESS" ){
		return _wiki_response(cache_result, res);
	}else if(cache_result && cache_result.status == "PENDING" ){
		res.set('Content-Type', 'application/json');
		res.end(JSON.stringify(cache_result));
		return
	}else{
		res.set('Content-Type', 'application/json');
		res.end(JSON.stringify({status : "ERROR", result : []}));
		return
	}
});

app.get('/crawl', (req,res) => {
	var start = req.query.start;
	var end = req.query.end;
	var regex = /https:\/\/[a-z]{2}\.wikipedia\.org\/wiki\/.*/g;
	var response = {}

	if(!(start && end)){
		response.status = "ERROR";
		response.message = "Please provide both start and end url"
		res.end(JSON.stringify(response));
		return;
	}

	start.replace("http://", "https://");
	end.replace("http://", "https://");

	if(!(start.match(regex) && end.match(regex))){
		response.status = "ERROR";
		response.message = "Please provide both start and end wikipedia url"
		res.end(JSON.stringify(response));
		return;
	}

	var cache_result = cache[[start, end]] ;
	
	if(cache_result && cache_result.status == "SUCCESS" ){
		return _wiki_response(cache_result, res);
	}

	cache[[start, end]] = {result:[], status: "PENDING"}
	var callPython = pythonHost + "/crawl?start=" + start + "&end=" + end;

	rp({
		url : callPython, 
		method : "GET",
		simple : false
	})
	.then(value => {
		value = JSON.parse(value);
		promiseList = [];
		console.log("update cache");
		cache[[start, end]] = value;
		setTimeout(() => {
			delete cache[[start, end]]
		}, 60000 * 10);
	})
	.catch(() => {
		delete cache[[start, end]]
	})

	res.set('Content-Type', 'application/json');
	res.end(JSON.stringify({result : "PENDING"}));
	return
	
})

app.get('/wiki/:id', (req, res) => {
	console.log(req.params);
	res.redirect('https://en.wikipedia.org/wiki/' + req.params.id);
})

var _wiki_response = (value, res) => {
	promiseList = [];
	
	value.result.map( data => {
		options = {uri : data.origin, simple : false}
		promiseList[data.index - 1] = rp(options);
	})

	Promise.all(promiseList).then(values => {
		console.log("wiki pages");
		values.map((dom, index) => {
			console.log("promises pass!");
			
			var current_request = value.result[index];
			var doc = new JSDOM(dom).window.document;
			var acceptableElement = ["table", "div", "h1", "h2", "h3", "h4", "h5", "p"]

            var keyword = current_request.next_link.match(/\/wiki\/.*/);
            keyword = "[href='" + current_request.next_link.substr(keyword.index) + "']";

			var aImg = doc.querySelector(".image > img");
			var justImg = doc.querySelector("img.image");
			var imgUrl = aImg ? aImg.src : justImg ?  justImg.src : "";
			var element = doc.querySelector(keyword)
			element.className += " highlight"
			var para = element;
			var node = "";
			var className = "";


			while(para && !(acceptableElement.includes(node))){
				para = para.parentElement;
				node = para.nodeName.toLowerCase()
				//exclusion
				className = para.className
				if (node === "div" && (className.indexOf("note") > -1 || className.indexOf("plainlist") > -1)){
					node = "";
				}
			}


			current_request.thumbnail = imgUrl;
			current_request.snippet = para.outerHTML;
			current_request.page_title = doc.title.replace(" - Wikipedia", "");
			current_request.summary = doc.querySelector(".mw-parser-output p").innerHTML;
		})

		res.set('Content-Type', 'application/json');
		res.end(JSON.stringify(value));
		return
	})
}


var server = app.listen(8081, function () {   
   console.log("Example app listening at 8081")
})