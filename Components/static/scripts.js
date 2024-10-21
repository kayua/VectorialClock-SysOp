document.getElementById('send-button').addEventListener('click', function() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;

    const addressInput = document.getElementById('address-input'); // Corrigido para pegar o valor correto
    const address_input = addressInput.value; // Obtenha o valor do campo de endereço

    if (message && address_input) { // Verifica se ambos os campos têm valor
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            // Corrigido para usar `&` ao invés de `,`
            body: `message=${encodeURIComponent(message)}&address=${encodeURIComponent(address_input)}`,
        }).then(response => response.json())
          .then(data => {
              console.log(data);
              const messageBox = document.getElementById('message-box');
              messageBox.innerHTML += `<p><strong>Enviado: </strong> ${messageInput.value }</p>`;
              messageInput.value = ''; // Limpa o campo de entrada
              updateStatusBar('Mensagem enviada', '#4CAF50');
          })
          .catch(error => {
              console.error('Erro:', error);
              updateStatusBar('Erro ao enviar mensagem', '#f44336'); // Atualiza a barra de status em caso de erro
          });
    } else {
        updateStatusBar('Por favor, preencha ambos os campos', '#f44336'); // Alerta se os campos estiverem vazios
    }
});

function updateStatusBar(message, backgroundColor) {
    const statusBar = document.getElementById('status-bar');
    statusBar.innerText = message;
    statusBar.style.backgroundColor = backgroundColor;

    setTimeout(() => {
        statusBar.innerText = 'Pronto';
        statusBar.style.backgroundColor = '#2196F3'; // Cor original da barra de status
    }, 3000);
}

// Polling para novas mensagens
setInterval(function() {
    fetch('/receive_message')
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                const messageBox = document.getElementById('message-box');
                const timestamp = new Date().toLocaleString();
                messageBox.innerHTML += `<p><strong>Recebido: </strong> ${data.message}</p>`;
                messageBox.scrollTop = messageBox.scrollHeight; // Rolagem automática para o fundo
                updateStatusBar('Mensagem recebida', '#2196F3');
            }
        })
        .catch(error => {
            console.error('Erro:', error); // Exibe erro no console se ocorrer
        });
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
        .catch(error => {
            console.error('Erro:', error); // Exibe erro no console se ocorrer
        });
}, 1000);