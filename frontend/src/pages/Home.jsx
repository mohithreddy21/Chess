import { useEffect, useState } from "react";

function Home(props) {
  const socketRef = props.socketRef;
  const [roomID, setRoomID] = useState(null);

  function handleCreateRoom(socket){
        const content = {
            type : 'create'
        }
        const message = JSON.stringify(content);
        socket.send(message);   
    }

    useEffect(()=>{
        if(!socketRef.current) return;
        socketRef.current.onmessage = (event)=>{
            const response = JSON.parse(event.data);
            if(response.type === 'room_created'){
                const roomId = response.message;
                setRoomID(roomId);
            }
        }
    },[socketRef.current])


  return (
    <div className="home">
      <div className="room-window">
        <h1>{roomID ? <p>{roomID}</p> : <p>No room yet</p>}</h1>
        <button className="btn-create" onClick={()=>handleCreateRoom(socketRef.current)}>Create Room</button>
        <div className="join-section">
          <input type="text" className="room-input" placeholder="Enter Room ID" />
          <button className="btn-join">Join Room</button>
        </div>
      </div>
    </div>
  )
}

export default Home