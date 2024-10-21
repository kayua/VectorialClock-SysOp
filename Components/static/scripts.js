document.getElementById('send-button').addEventListener('click', function() {

    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;
    const addressInput = document.getElementById('address-input');
    const address_input = addressInput.value;

    if (message && address_input) {

        fetch('/send_message', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded', },
           body: `message=${encodeURIComponent(message)}&address=${encodeURIComponent(address_input)}`,
           }).then(response => response.json())
           .then(data => {

              const messageBox = document.getElementById('message-box');
              messageBox.innerHTML += `<p><strong>Enviado: </strong> ${messageInput.value }</p>`;
              messageInput.value = '';
              updateStatusBar('Mensagem enviada', '#4CAF50');

          })
          .catch(error => { updateStatusBar('Erro ao enviar mensagem', '#f44336'); });

            } else {

            updateStatusBar('Por favor, preencha ambos os campos', '#f44336');

        }

    });

function updateStatusBar(message, backgroundColor) {

    const statusBar = document.getElementById('status-bar');
    statusBar.innerText = message;
    statusBar.style.backgroundColor = backgroundColor;

    setTimeout(() => {
        statusBar.innerText = 'Pronto';
        statusBar.style.backgroundColor = '#2196F3';
    }, 3000);

}

setInterval(function() {
    fetch('/receive_message')
        .then(response => response.json())
        .then(data => {

            if (data.message) {

                const messageBox = document.getElementById('message-box');
                const timestamp = new Date().toLocaleString();
                messageBox.innerHTML += `<p><strong>Recebido: </strong> ${data.message}</p>`;
                messageBox.scrollTop = messageBox.scrollHeight;
                updateStatusBar('Mensagem recebida', '#2196F3');

            }

        })
        .catch(error => {});

    }, 2000);


setInterval(function() {

    fetch('/get_id')
        .then(response => response.json())
        .then(data => {

            if (data.pid) {

                const pid = document.getElementById('pid-text');
                pid.innerHTML = `<h3 style='margin-top: -3px;'> ${data.pid}</h3>`;

            }
        })
        .catch(error => {});

    }, 1000);