
# cluster-live

  Realtime administration and statistics for cluster

## Installation

    $ npm install cluster-live

## Usage

 Cluster live requires that `stats()` is used, enabling connection and "light request" statistics. The `lightRequests` option simply enables light-weight request statistics better suited for realtime reporting.

     var cluster = require('cluster'), live = require('cluster-live');
     
     cluster(server)
       .set('workers', 6)
       .use(cluster.debug())
       .use(cluster.stats({ connections: true, lightRequests: true }))
       .use(live())
       .listen(3000);

## Options

  Pass an object such as `live({ port: 8889 })`, with one or more of the following options:
  
    - `port`  defaults to `8888`
    - `host`  hostname
    - `user`  basicAuth username
    - `pass`  basicAuth password

 When running in production you should use `NODE_ENV=production`, after which the user/pass are required.

## Examples

 First start the example application and cluster-live:
 
     $ node examples/basic.js

  Visit _http://localhost:8888_ in your browser, and execute the following command to simulate some requests:
  
     $ watch --interval=0.1 curl http://localhost:3000/

## Screenshots

![request graphs](http://f.cl.ly/items/0E0e0Q1a3j1r3r353G1Y/Screenshot.png)

## License 

(The MIT License)

Copyright (c) 2011 TJ Holowaychuk &lt;tj@vision-media.ca&gt;

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
