document.addEventListener('DOMContentLoaded', () => {
    const chatSocket = io.connect('http://127.0.0.1:5000/chat');

    if (location.pathname.includes('/chat')) {
        console.log('Sending message to server...');
        chatSocket.emit('client_connected', 'Hello server!');
    }

    chatSocket.on('connect', () => {
        console.log('Connected to chat namespace');
    });
});

