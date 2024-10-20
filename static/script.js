const socket = io();
const usernameForm = document.getElementById('username-form');
const usernameInput = document.getElementById('username');
const setUsernameButton = document.getElementById('set-username');
const chatroom = document.getElementById('chatroom');
const form = document.getElementById('form');
const input = document.getElementById('input');
const messages = document.getElementById('messages');
const friendsList = document.getElementById('friends');

const colors = {};  // Store colors for each user

setUsernameButton.addEventListener('click', () => {
    const username = usernameInput.value.trim();
    if (username) {
        socket.emit('join', { username: username });
        usernameForm.style.display = 'none';
        chatroom.style.display = 'block';
    }
});

form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (input.value) {
        socket.emit('chat message', input.value);
        input.value = '';
    }
});

socket.on('chat message', (msg) => {
    const item = document.createElement('li');
    item.innerHTML = msg.replace(/(.*):/, `<span style="color:${getColor(msg.split(':')[0])};">${msg.split(':')[0]}:</span>`);
    messages.appendChild(item);
    window.scrollTo(0, document.body.scrollHeight);
});

socket.on('update friends list', (userList) => {
    friendsList.innerHTML = '';
    userList.forEach(user => {
        const li = document.createElement('li');
        li.textContent = user;
        li.style.color = getColor(user);  // Assign color to usernames
        friendsList.appendChild(li);
    });
});

// Function to assign a color to each username
function getColor(username) {
    if (!colors[username]) {
        colors[username] = '#' + Math.floor(Math.random() * 16777215).toString(16); // Generate random color
    }
    return colors[username];
}
