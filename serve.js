// Tiny local web server for the games: node serve.js  ->  http://localhost:8080/zombie-arcade.html
// (Needed so the game can load models/zombie.glb; browsers block that for pages opened straight from disk.)
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, port = process.env.PORT || 8080;
const types = { '.html': 'text/html', '.js': 'text/javascript', '.glb': 'model/gltf-binary', '.gltf': 'model/gltf+json',
  '.bin': 'application/octet-stream', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.fbx': 'application/octet-stream' };
http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split('?')[0]);
  const file = path.join(root, rel === '/' ? 'zombie-arcade.html' : rel);
  if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) { res.writeHead(404); return res.end('not found'); }
    // no-cache: the browser must check for a newer version every time (so you never play an old copy of the game)
    res.writeHead(200, { 'Content-Type': types[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': st.size,
                         'Cache-Control': 'no-cache', 'Last-Modified': st.mtime.toUTCString() });
    fs.createReadStream(file).pipe(res);
  });
}).listen(port, '127.0.0.1', () => console.log(`Zombie Alley running at http://localhost:${port}/zombie-arcade.html`));
