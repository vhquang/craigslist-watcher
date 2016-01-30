var host = 'https://losangeles.craigslist.org';
var link = 'https://losangeles.craigslist.org/search/sss?sort=date&max_price=240&min_price=100';
var fileName = 'item.json';

var system = require("system");
var fs = require('fs');

var debug = false;


function log (msg, line, source) {
  debugLog('--------------------');
  debugLog('  Remote console:' + msg);
}

function debugLog() {
  if (window.debug) {
    var log = "";
    for (var i = 0; i < arguments.length; i++){
      log += arguments[i].toString() + " ";
    }
    console.log(log);
  }
}

function trace(msg, trace) {
  console.log('error on page' + msg);
  trace.forEach(function(item) {
    console.log('  ', item.file, ':', item.line);
  });
}


var webPage = require("webpage").create();
webPage.settings.userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " +
  "Chrome/31.0.1637.2 Safari/537.36";
webPage.settings.resourceTimeout = 30000; // 30 seconds
webPage.onError = trace;
webPage.onConsoleMessage = log;

var result = {};


function getItems(link) {
  webPage.open(link, function(status) {
    if (status === 'success') {

      result = webPage.evaluate(function(craigslistHost) {
        var scrapResult = {};
        $('.row[data-pid]').each(function(idx, item) {
          var row = $(item);
          var id = row.attr('data-pid');
          var price = row.find('a span.price').text().replace('$', '');
          var hdrlnk = row.find('a.hdrlnk');
          var title = hdrlnk.text();
          var link = hdrlnk.attr('href');
          var time = row.find('time').attr('datetime');
          if (link.indexOf('//') === 0) {
            link = 'https:' + link;
          } else {
            link = craigslistHost + link;
          }
          scrapResult[id] = {
            "id": id,
            "repost_id": row.attr('data-repost-of'),
            "price": price,
            "link": link,
            "title": title,
            "time": time
          }
        });
        return scrapResult;
      }, host);

    } else {
      console.error(status);
    }

    finish();
  });
}


function finish() {
  console.log(Object.keys(result).length);
  fs.write(fileName, JSON.stringify(result), 'w');
  phantom.exit();
}


// phantomjs --ignore-ssl-errors=true --web-security=no --ssl-protocol=tlsv1  cl.js
(function main() {
  var args = system.args;

  if (args.length === 1) {
    console.log('Run with default');
    console.log('link', link);
    console.log('output file', fileName)
    getItems(link);
  } else {
    link = args[1];
    fileName = args[2];
    getItems(link);
  }
})()
