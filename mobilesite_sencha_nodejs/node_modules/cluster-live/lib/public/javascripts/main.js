
var cluster = new EventEmitter;

window.onload = function(){
  var socket = new io.Socket(window.location.hostname)
    , workers = {}
    , master = new Master;

  socket.connect();

  // relay events
  socket.on('message', function(obj){
    switch (obj.type) {
      case 'event':
        cluster.emit.apply(cluster, obj.args);
        break;
      default:
        var parts = obj.split(':')
          , worker = getWorkerById(parts[0]);

        worker.emit('request');
        worker.emit('stats', {
            connectionsActive: parts[2]
          , connectionsTotal: parts[3]
          , requestsTotal: parts[4]
        });
    }
  });

  // add / remove workers
  $('add-worker').on('click', function(){
    socket.send('add-worker');
    return false;
  });
  
  $('remove-worker').on('click', function(){
    socket.send('remove-worker');
    return false;
  });

  function getWorkerById(id) {
    return workers[id] = workers[id] || new Worker(id);
  }

  function getWorker(worker) {
    return getWorkerById(worker.id);
  }

  cluster.on('master closing', function(){
    utils.notify('master shutting down');
  });

  cluster.on('master restarting', function(){
    utils.notify('master restarting');
  });

  cluster.on('master change', function(_master){
    master.emit('change', _master);
  });

  cluster.on('worker change', function(_worker){
    var worker = getWorker(_worker);
    worker.emit('stats', _worker.stats);
  });

  cluster.on('worker killed', function(_worker){
    var worker = getWorker(_worker);
    utils.notify('worker #' + worker.id + ' killed');
    worker.stopReporting().overlay('killed');
  });

  cluster.on('worker exception', function(_worker, err){
    var worker = getWorker(_worker);
    utils.notify('worker #' + worker.id + ': ' + err.message);
  });

  cluster.on('worker removed', function(_worker){
    var worker = getWorker(_worker);
    utils.notify('worker #' + worker.id + ' removed');
    worker.remove();
    delete workers[worker.id];
  });
  
  cluster.on('worker spawned', function(_worker){
    var worker = getWorker(_worker);
    utils.notify('worker #' + worker.id + ' spawned');
    worker.emit('stats', _worker.stats);
    worker.startReporting().removeOverlay();
  });

  cluster.on('client connection', function(_worker){
    var worker = getWorker(_worker);
    worker.emit('stats', _worker.stats);
    worker.emit('connection');
  });
};