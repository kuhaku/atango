var fs          = require('fs');
var http        = require('http');
var querystring = require('querystring');
var execsyncs = require('/usr/local/lib/node_modules/execsyncs');

http.createServer(function(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  var text = querystring.parse(req.url.slice(1)).text;
  if ( errCheck(text === undefined, 'Invalid parameters', res) ) return;
  console.log('query: ' + text);
  var result = execsyncs('bash /work/atango/bin/ojtalk.sh -q true -m ' + text);
  fs.readFile('/tmp/out.wav', 'binary', function(err, file) {
  if (errCheck(err, 'Error at reading file', res)){
      return;
  }
  res.writeHead(200, {'Content-Type': 'audio/wav'});
  res.write(file, 'binary');
  res.end();
  });
}).listen(12000);

function errCheck(err, msg, res) {
  if (err) {
    res.writeHead(400, {'Content-Type': 'text/plain'});
    res.write(msg);
    res.end();
    return true;
  }
  return false;
}

process.on('uncaughtException', function (err) {
  console.log('Error: ' + err);
});
