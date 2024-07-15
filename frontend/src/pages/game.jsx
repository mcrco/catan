import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { io } from 'socket.io-client';
import * as PIXI from 'pixi.js';

const socket = io();

function Game() {
    const { gameCode } = useParams();
    const [players, setPlayers] = useState([]);

    useEffect(() => {
        socket.emit('join_game', { game_code: gameCode, username: 'Player' });

        socket.on('player_joined', (data) => {
            setPlayers((prevPlayers) => [...prevPlayers, data.username]);
        });

        const app = new PIXI.Application({ width: 800, height: 600 });
        document.body.appendChild(app.view);

        const graphics = new PIXI.Graphics();
        graphics.beginFill(0xde3249);
        graphics.drawRect(50, 50, 100, 100);
        graphics.endFill();
        app.stage.addChild(graphics);

        return () => {
            app.destroy(true, true);
        };
    }, [gameCode]);

    return (
        <div>
            <h1>Game Code: {gameCode}</h1>
            <h2>Players:</h2>
            <ul>
                {players.map((player, index) => (
                    <li key={index}>{player}</li>
                ))}
            </ul>
        </div>
    );
}

export default Game;

