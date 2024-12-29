import React, { useState } from 'react';
import { Container, Alert } from 'react-bootstrap';
import Keyboard from './Keyboard';
import Confetti from './Confetti';
import Banner from './Banner';
import { wordsList } from '../words';

const GameBoard = ({ targetWord }) => {
    const [usedWords, setUsedWords] = useState([]);
    const [guesses, setGuesses] = useState(Array(6).fill(''));
    const [currentGuess, setCurrentGuess] = useState('');
    const [currentRow, setCurrentRow] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [win, setWin] = useState(false);
    const [showInvalidWordWarning, setShowInvalidWordWarning] = useState(false);

    const handleInput = (letter) => {
        if (!gameOver && currentGuess.length < 5) {
            const newGuess = currentGuess + letter.toUpperCase();
            setCurrentGuess(newGuess);
            const updatedGuesses = [...guesses];
            updatedGuesses[currentRow] = newGuess;
            setGuesses(updatedGuesses);
        }
    };

    const handleDelete = () => {
        if (!gameOver && currentGuess.length > 0) {
            const newGuess = currentGuess.slice(0, -1);
            setCurrentGuess(newGuess);
            const updatedGuesses = [...guesses];
            updatedGuesses[currentRow] = newGuess;
            setGuesses(updatedGuesses);
        }
    };

    const handleSubmit = () => {
        if (!gameOver && currentGuess.length === 5) {
            if (currentGuess === targetWord) {
                setWin(true);
                setGameOver(true);
            } else {
                if (!wordsList.includes(currentGuess)) {
                    // Show a warning if the word is not in the word list
                    setShowInvalidWordWarning(true);
                    return;
                }
                setShowInvalidWordWarning(false);
                const updatedGuesses = [...guesses];
                updatedGuesses[currentRow] = currentGuess;
                setGuesses(updatedGuesses);
                if (currentRow === 5) {
                    setGameOver(true);
                }
                setCurrentGuess('');
                setCurrentRow((prev) => prev + 1);
            }
        }
    };

    return (
        <Container className="game-board">
            {showInvalidWordWarning && <Alert variant="warning">Word not in list. Try again!</Alert>}
            {win && <Confetti />}
            {(win || (gameOver && currentRow >= 6)) && <Banner win={win} word={targetWord} />}
            <div className="grid">
                {guesses.map((guess, rowIndex) => (
                    <div key={rowIndex} className="row mb-2">
                        {Array.from({ length: 5 }).map((_, colIndex) => {
                            const guessedLetter = guess[colIndex];
                            const letter = (guessedLetter || '').padEnd(5);
                            const color = rowIndex < currentRow ? getTileColor(guessedLetter, colIndex) : 'white';
                            const guessCss = rowIndex === currentRow ? (guessedLetter ? 'has-letter' : '') : '';
                            return (
                                <div
                                    className={`tile ${color} ${guessCss}` }
                                    key={colIndex}
                                >
                                    {letter || ''}
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>
            <Keyboard
                onLetter={handleInput}
                onDelete={handleDelete}
                onEnter={handleSubmit}
            />
        </Container>
    );

    function getTileColor(letter, index) {
        if (!letter) return 'white';
        if (targetWord[index] === letter) return 'green';
        if (targetWord.includes(letter)) return 'yellow';
        return 'gray';
    }
};

export default GameBoard;
