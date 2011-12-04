
/**
 * Chart options.
 */

var chartOptions = {
  grid: {
      strokeStyle: 'rgba(0,0,0,0.1)'
    , fillStyle: 'white'
    , verticalSections: 6
    , lineWidth: 1
    , millisPerLine: 1000
  },
  labels: {
    fillStyle: 'rgba(0,0,0,0.5)'
  }
};

/**
 * Initialize a `Worker` with the given `id`.
 *
 * @param {Number} id
 */

function Worker(id) {
  var self = this;
  EventEmitter.call(this);
  this.id = id;
  this.requests = 0;
  this.connections = 0;
  this.chart = new SmoothieChart(chartOptions);
  this.requestSeries = new TimeSeries;
  this.connectionSeries = new TimeSeries;
  this.view = new WorkerView(this);

  // series
  this.chart.addTimeSeries(this.requestSeries, { strokeStyle: 'rgba(0,0,0,0.5)' });
  this.chart.addTimeSeries(this.connectionSeries, { strokeStyle: '#00D0FA' });

  // requests
  this.on('request', function(req){
    ++self.requests;
  });

  // connections
  this.on('connection', function(req){
    ++self.connections;
  });

  // stat changes
  this.on('stats', function(stats){
    self.stats = stats;
    self.view.render();
  });

  // render interval
  this.startReporting();
};

/**
 * Inherit from `EventEmitter.prototype`.
 */

Worker.prototype = Object.create(EventEmitter.prototype);

/**
 * Apply overlay `msg`.
 *
 * @param {String} msg
 * @return {Worker} for chaining
 */

Worker.prototype.overlay = function(msg){
  this.view.overlay(msg);
  return this;
};

/**
 * Remove overlay.
 *
 * @return {Worker} for chaining
 */

Worker.prototype.removeOverlay = function(){
  this.view.removeOverlay();
  return this;
};

/**
 * Stop reporting.
 *
 * @return {Worker} for chaining
 */

Worker.prototype.stopReporting = function(){
  clearInterval(this.interval);
  return this;
};

/**
 * Start reporting.
 *
 * @return {Worker} for chaining
 */

Worker.prototype.startReporting = function(){
  this.interval = setInterval(function(self){
    self.requestSeries.append(+new Date, self.requests);
    self.connectionSeries.append(+new Date, self.connections);
    self.view.render();
    self.requests = self.connections = 0;
  }, 500, this);
  return this;
};

/**
 * Remove the worker's representation.
 *
 * @return {Worker} for chaining
 */

Worker.prototype.remove = function(){
  this.stopReporting();
  this.view.remove();
  return this;
};

/**
 * Initialize a new `WorkerView` for the given `worker`.
 *
 * @param {Worker} worker
 */

function WorkerView(worker) {
  View.call(this, 'worker', worker);
  var workers = $('workers')
    , canvas = document.createElement('canvas')
    , chart = worker.chart
    , el = this.el;

  // add view to the DOM
  workers.appendChild(el);

  // chart
  canvas.width = 300;
  canvas.height = 100;
  this.on('render', function(){
    el.getElementsByClassName('chart')[0].appendChild(canvas);
    chart.streamTo(canvas, 1500);
  });
}

/**
 * Inherit from `View.prototype`.
 */

WorkerView.prototype = Object.create(View.prototype);

/**
 * Remove the worker view.
 */

WorkerView.prototype.remove = function(){
  this.el.parentNode.removeChild(this.el);
};