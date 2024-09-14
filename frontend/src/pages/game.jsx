import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { io } from 'socket.io-client';
import * as PIXI from 'pixi.js';
import CatanBoard from '../components/board';

const socket = io();

function Game() {
    const { gameCode } = useParams();
    const [username, setUsername] = useState('');
    const [userId, setUserId] = useState('')
    const [ready, setReady] = useState(false);
    const [gameState, setGameState] = useState({})
    
    const handleReadyButton = async () => {
        const response = await fetch('/api/join_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ gameCode: gameCode, username: username}),
        });

        const data = await response.json();
        if (data.success) {
            setUserId(data.userId);
            setReady(true);
            socket.emit('player_ready', { userId: data.userId, gameCode: gameCode });
            socket.on('game_update', (data) => {
                console.log(data);
                setGameState(data);
            })
        } else {
            alert(data.message);
        }
    }

    const handleStartGameButton = async () => {
        socket.emit('start_game', { userId: userId, gameCode: gameCode });
    }
    
    const handleRollButton = async() => {
        socket.emit('roll_dice', {userId: userId, gameCode: gameCode})
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
                        <li key={index}>{player.name}</li>
                    ))}
                </ul>
            }

            {gameState && gameState.currentTurn >= 0 &&
                <div>
                    {/* <CatanBoard board={gameState.board} /> */}
                    <h2>Players and Points:</h2>
                    <ul>
                        {gameState.players.map((player, index) => (
                            <li key={index}>{player.name}: {player.points} points, {player.numResources} resources</li>
                        ))}
                    </ul>

                    <h2>Player Resources:</h2>
                        {Object.keys(gameState.resources).map((resource, index) => (
                            <li key={index}>{resource}: {gameState.resources[resource]}</li>
                        ))}

                    <h2> Roll: </h2>
                    {gameState.roll[0]}, {gameState.roll[1]}

                    {gameState.playerTurn == username && 
                        <button onClick={handleRollButton}>
                            Roll Dice
                        </button>
                    }
                </div>
            }

            {username === gameState.host && !gameState.board &&
                <button onClick={handleStartGameButton}>Start Game</button>
            }
        </div >
    );
}

export default Game;

