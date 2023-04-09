document.addEventListener('DOMContentLoaded', () => {
    const gameSocket = io.connect('ws://127.0.0.1:5000/game');
    
    gameSocket.on('connect', () => {
        console.log('Connected to game namespace');
        gameSocket.emit('move', { x: 1, y: 2 });
    });
});