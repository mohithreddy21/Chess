import { useState, useEffect, useRef } from "react";


function useWebSocket(){
    const [isConnected, setIsConnected] = useState(false)
    const socketRef = useRef(null);
    useEffect(()=>{
        const socket = new WebSocket('ws://localhost:8000');
        socketRef.current = socket;
        return () => socket.close()
    },[])

    return {socketRef : socketRef.current}
}

export default useWebSocket;