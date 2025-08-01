const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const socket = io();

let mySnake = { x: 100, y: 100, dir: 'right', color: 'lime' };
let enemies = {};

document.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp') mySnake.dir = 'up';
    else if (e.key === 'ArrowDown') mySnake.dir = 'down';
    else if (e.key === 'ArrowLeft') mySnake.dir = 'left';
    else if (e.key === 'ArrowRight') mySnake.dir = 'right';
});

setInterval(() => {
    moveSnake(mySnake);
    socket.emit('player_input', mySnake);
}, 100);

socket.on('game_state', data => {
    enemies = data;
    delete enemies[socket.id];
    drawGame();
});

function moveSnake(snake) {
    const speed = 10;
    if (snake.dir === 'up') snake.y -= speed;
    if (snake.dir === 'down') snake.y += speed;
    if (snake.dir === 'left') snake.x -= speed;
    if (snake.dir === 'right') snake.x += speed;
}

function drawGame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = mySnake.color;
    ctx.fillRect(mySnake.x, mySnake.y, 10, 10);
    for (let id in enemies) {
        let e = enemies[id];
        ctx.fillStyle = 'red';
        ctx.fillRect(e.x, e.y, 10, 10);
    }
}