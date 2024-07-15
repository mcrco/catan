import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
    const [gameCode, setGameCode] = useState('');
    const navigate = useNavigate();

    const createGame = async () => {
        const response = await fetch('/api/create_game', { method: 'POST' });
        const data = await response.json();
        navigate(`/game/${data.game_code}`);
    };

    const joinGame = async () => {
        const response = await fetch('/api/join_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_code: gameCode }),
        });
        const data = await response.json();
        if (data.success) {
            navigate(`/game/${gameCode}`);
        } else {
            alert(data.message);
        }
    };

    return (
        <div>
            <button onClick={createGame}>Create Game</button>
            <input
                type="text"
                value={gameCode}
                onChange={(e) => setGameCode(e.target.value)}
                placeholder="Enter game code"
            />
            <button onClick={joinGame}>Join Game</button>
        </div>
    );
}

export default Home;

