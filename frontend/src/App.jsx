import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';
import Game from './pages/game';

const App = () => {
    return (
        <div className="App">
            <Router>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/game/:gameCode" element={<Game />} />
                </Routes>
            </Router>
        </div>
    );
};

export default App;
