let socket = null;

const roomInput = document.querySelector("#room-input");
roomInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        const roomId = roomInput.value;

        startConnection(roomId);

        roomInput.value = "";
    }
});

const joinButton = document.querySelector("#join-btn");
joinButton.addEventListener("click",()=>{
    const roomId = roomInput.value;
    if(roomId !== ''){
        startConnection(roomId);
        roomInput.value = '';
    }
})

const chatBox = document.querySelector("#chat-box");
function displayChats(chat){
    const chatBubble = document.createElement("div");
    chatBubble.className = 'chat-bubble';
    chatBubble.textContent = chat;
    chatBox.appendChild(chatBubble);
}

const sendButton = document.querySelector("#send-btn");
const messageInput = document.querySelector("#message-input");
sendButton.addEventListener("click", ()=>{
    const content = messageInput.value;
    const message = {
        type : 'message',
        message : content
    }
    socket.send(JSON.stringify(message));
    displayChats(content);
    messageInput.value = '';
})


function startConnection(roomID) {
    if (socket !== null) {
        socket.close();
    }
    socket = new WebSocket("ws://localhost:8000");
    socket.onopen = () => {
        const message = {
            type : 'join',
            roomId : roomID
        }
        socket.send(JSON.stringify(message));
    };

    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        displayChats(message.message);
    }
}