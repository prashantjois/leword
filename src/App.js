import './App.css';

import GameBoard from './components/GameBoard';
import { wordsList } from './words';

function App() {
  const word = getRandomWord();
  return (
    <div className="App">
      <div className="App-container">
        <h1>Le Word</h1>
        <GameBoard targetWord={word}/>
      </div>
    </div>
  );
}

function getRandomWord() {
  const index = Math.floor(Math.random() * wordsList.length);
  const word = wordsList[index];
  return word;
}

export default App;
