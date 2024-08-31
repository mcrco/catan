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
    const [gameState, setGameState] = useState({})

    const handleReadyButton = async () => {
        const response = await fetch('/api/player_ready', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_code: gameCode, username: username }),
        });

        const data = await response.json();
        setUserId(data.user_id);
        setReady(true);
        socket.emit('player_ready', { user_id: data.user_id, game_code: gameCode });
        socket.on('game_update', (data) => {
            console.log(data);
            setGameState(data);
        })
    }

    const handleStartGameButton = async () => {
        const response = await fetch('/api/start_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, game_code: gameCode }),
        })

        const data = await response.json();
        if (data.success) {
            console.log('Game started.');
        } else {
            console.log('Failed to start game.');
        }
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

            {
                gameState.players &&
                <ul>
                    {gameState.players.map((player, index) => (
                        <li key={index}>{player}</li>
                    ))}
                </ul>
            }

            {gameState.scores &&
                <ul>
                    {gameState.scores.map((player, index) => (
                        <li key={index}>{player}: </li>
                    ))}
                </ul>
            }

            {username === gameState.host && !gameState.scores &&
                <button onClick={handleStartGameButton}>Start Game</button>
            }
        </div >
    );
}

export default Game;

