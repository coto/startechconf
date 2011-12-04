var events = require('events')
  , httpAgent = require('http-agent')
  , jsdom = require('jsdom');

function ScrappyDo(opts) {
  events.EventEmitter.call(this);
  opts = opts || {};
  this.base = opts.base || 'sofsis.cl';
  this.cache = opts.cache || false;
  this.cacheExpire = opts.cache || 24;
  this.debug = opts.debug || false;
  this.scripts = opts.scripts || ['jquery-1.6.1.min.js'];
  this.data = {base: this.base};

  this.agent = httpAgent.create(this.base);

  me = this;
  this.agent.addListener('stop', function() {
    me.emit('end', me.data);
  });

}

ScrappyDo.prototype = new events.EventEmitter;

ScrappyDo.prototype.get = function(path, cb) {

  me = this;

  //httpAgent doesnt like the first slash
  path[0] == '/'? path = path.slice(1): undefined

  me.debug && console.log('path: ', path);

  this.agent._unvisited.push(path);
  this.agent.addListener('next', function(err, agent) {

    if (err) throw new Error(err);

    me.debug && console.log('  -> got response.');

    jsdom.env({
        html: agent.body
      , scripts: me.scripts
    }, function(err, window) {
      var $ = window.jQuery;
      cb && cb(me.data, $);
      agent.next();
      //me.agent.removeListener(listen);
    });
  });
}

ScrappyDo.prototype.do = function() {
  this.agent.start();
};

module.exports.create = function(opts) {
 return new ScrappyDo(opts);
}

module.exports.ScrappyDo = ScrappyDo;
