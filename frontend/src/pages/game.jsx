import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { io } from 'socket.io-client';
import * as PIXI from 'pixi.js';

const socket = io();

function Game() {
    const { gameCode } = useParams();
    const [username, setUsername] = useState('');
    const [userId, setUserId] = useState('')
    const [ready, setReady] = useState(false);
    const [players, setPlayers] = useState([]);

    const handleReadyButton = () => {
        socket.emit('join_game', { game_code: gameCode, username: username });

        socket.on('player_joined', (data) => {
            setUserId(data.player.userId)
            setPlayers(data.players);
            setReady(true)
        });
    }

    if (!ready) {
        return (
            <div>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter username"
                />
                <button onClick={handleReadyButton}>Ready</button>
            </div>
        );
    }

    return (
        <div>
            <h1>Game Code: {gameCode}</h1>
            <h2>Players:</h2>
            <ul>
                {players.map((player, index) => (
                    <li key={index}>{player.username}</li>
                ))}
            </ul>
        </div>
    );
}

export default Game;

