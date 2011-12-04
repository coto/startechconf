
/*!
 * cluster-live
 * Copyright(c) 2011 TJ Holowaychuk <tj@vision-media.ca>
 * MIT Licensed
 */

/**
 * Module dependencies.
 */

var os = require('os')
  , utils = require('./utils');

/**
 * Export plugin.
 */

module.exports = live;

/**
 * Library version.
 */

exports.version = '0.0.3';

/**
 * Enable with the given `port`, `host` and `options`.
 *
 * @param {Number|Object} port or options
 * @param {String|Object} host or options
 * @param {Object} options
 * @return {Function}
 * @api public
 */

function live(port, host, options) {
  // juggle arguments
  if ('object' == typeof port) options = port, port = null;
  if ('object' == typeof host) options = host, host = null;
  if (null == port) port = 8888; 

  function live(master) {
    if (!master.stats) throw new Error('cluster-live requires the stats() plugin');
    if (!master.lightRequestStats) throw new Error('cluster-live requires stats() "lightRequests"');
    if (!master.connectionStats) throw new Error('cluster-live requires stats() "connections"');

    // setup app
    var app = require('./app')(options);
    app.listen(port, host);

    // websockets
    var sockets = [];
    app.io.on('connection', function(sock){
      // maintain array of clients
      var len = sockets.push(sock);
      sock.id = len - 1;

      sock.on('disconnect', function(){
        sockets.splice(sock.id, 1);
      });

      sock.on('message', function(msg){
        switch (msg) {
          case 'add-worker':
            master.spawn(1);
            sockets.emit('master change', stripMaster(master));
            break;
          case 'remove-worker':
            master.remove(1);
            sockets.emit('master change', stripMaster(master));
            break;
        }
      });

      // "emit" an event

      sock.trigger = function(){
        this.send({
            type: 'event'
          , args: utils.toArray(arguments)
        });
      };

      // emit "master change" to initialize master data
      sock.trigger('master change', stripMaster(master));

      // emit "worker change" event to initialize
      // existing workers with the new client
      master.children.forEach(function(worker){
        sock.trigger('worker change', stripWorker(worker));
      });
    });

    // "emit" event to all clients

    sockets.emit = function(event){
      for (var i = 0, len = sockets.length; i < len; ++i) {
        sockets[i].trigger.apply(sockets[i], arguments);
      }
    };

    // master process data
    master.os = {
      cpus: os.cpus().length
    };

    // cluster events

    master.on('client connection', function(worker){
      sockets.emit('client connection', stripWorker(worker));
    });

    master.on('client light request', function(worker, request){
      app.io.broadcast([
          worker.id
        , request
        , worker.stats.connectionsActive
        , worker.stats.connectionsTotal
        , worker.stats.requestsTotal
        ].join(':'));
    });

    master.on('worker removed', function(worker){
      sockets.emit('worker removed', stripWorker(worker));
    });

    master.on('worker killed', function(worker){
      sockets.emit('master change', stripMaster(master));
      sockets.emit('worker killed', stripWorker(worker));
    });

    master.on('worker exception', function(worker, err){
      sockets.emit('worker exception', stripWorker(worker), stripError(err));
    });
    
    master.on('worker', function(worker){
      sockets.emit('worker spawned', stripWorker(worker));
    });

    // close cluster-live server down
    master.on('restarting', function(){
      sockets.emit('master restarting');
      if (app.fd) app.close();
    });

    master.on('closing', function(){
      sockets.emit('master closing');
      if (app.fd) app.close();
    });
  }

  return live;
};

/**
 * Prep error for JSON.
 */

function stripError(err) {
  return {
    message: err.message
  };
}

/**
 * Prep master for JSON.
 */

function stripMaster(master) {
  return {
      stats: master.stats
    , state: master.state
    , startup: master.startup
    , env: master.env
    , os: master.os
    , workers: master.children.length
  }
}

/**
 * Prep work for JSON.
 */

function stripWorker(worker) {
  return {
      id: worker.id
    , stats: worker.stats
  }
};