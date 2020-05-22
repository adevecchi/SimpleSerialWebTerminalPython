(function() {

    const socket = new WebSocket('ws://localhost:8080/ws');
     
    socket.onopen = function () {  
      console.log('connected'); 
    }; 

    socket.onmessage = function (message) {
      var received_data = $('#received-data');

      if (message.data == 'Port name not found.') {
        $('#cmd-port').text('Open Port').removeClass('btn-danger').addClass('btn-success');
      }
      received_data.val(message.data + '\n' + received_data.val());
    };

    socket.onclose = function () {
      console.log('disconnected'); 
    };

    const sendMessage = function (message) {
      socket.send(JSON.stringify(message))
    };

    $('#cmd-port').on('click', function (evt) {
      var cmd = $(this).text(),
          port = $('#port').val();

      if (cmd == 'Open Port') {
        if (port.length < 4) {
            alertify.set('notifier', 'position', 'top-right');
            alertify.error('Port Name invalid.');
            return false;
        }
        $(this).text('Close Port').removeClass('btn-success').addClass('btn-danger');
        sendMessage({ method: 'open', args: { port: port, baudrate: $('#baudrate').val(), msg: 'Port is opened' } });
      }
      else {
          $(this).text('Open Port').removeClass('btn-danger').addClass('btn-success');
          sendMessage({ method: 'close', args: { msg: 'Port is closed' } })
      }
    });

    $('#message').on('keydown', function (evt) {
      if (evt.keyCode == 13) {
        $('#send-message').trigger('click');
        return false;
      }  
    });

    $('#send-message').on('click', function (evt) {
        sendMessage({ method: 'send', args: { data: $('#message').val(), msg: false } });
    });

    $('#clear').on('click', function(evt) {
        $('#received-data').val('');
    });

})();