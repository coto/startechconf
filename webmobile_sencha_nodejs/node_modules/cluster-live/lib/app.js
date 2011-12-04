
/*!
 * cluster-live - app
 * Copyright(c) 2011 TJ Holowaychuk <tj@vision-media.ca>
 * MIT Licensed
 */

/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , stylus = require('stylus')
  , io = require('socket.io');

/**
 * Initialize an Express application with the given `options`.
 *
 * @param {Object} options
 * @return {express.HTTPServer}
 * @api private
 */

module.exports = function(options){
  options = options || {};
  var app = module.exports = express.createServer();

  // configuration

  app.configure(function(){
    app.set('view engine', 'jade');
    app.set('views', __dirname + '/views');
  });

  app.configure('development', function(){
    app.use(stylus.middleware({ src: __dirname + '/public' }));
    app.use(express.static(__dirname + '/public'));
  });

  app.configure('production', function(){
    var day = 86400000;
    if (!options.user) throw new Error('username required');
    if (!options.pass) throw new Error('password required');
    app.use(express.basicAuth(options.user, options.pass));
    app.use(stylus.middleware({ src: __dirname + '/public', compress: true }));
    app.use(express.static(__dirname + '/public', { maxAge: day * 30 }));
  });

  // routes

  app.get('/', routes.index);

  // socket.io

  var socket = app.io = io.listen(app, { log: false });

  return app;
};