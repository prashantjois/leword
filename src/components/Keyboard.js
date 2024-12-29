import React from 'react';
import { Button } from 'react-bootstrap';

const Keyboard = ({ onLetter, onDelete, onEnter }) => {
    const keys = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '⌫'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
    ];

    const renderKey = (key) => {
        if (key === '⌫') {
            return (
                <Button
                    variant="outline-secondary"
                    className="key wide-key"
                    key={key}
                    onClick={onDelete}
                >
                    {key}
                </Button>
            );
        }
        return (
            <Button
                variant="outline-secondary"
                className="key"
                key={key}
                onClick={() => onLetter(key.toLowerCase())}
            >
                {key}
            </Button>
        );
    };

    return (
        <div className="keyboard">
            {keys.map((row, rowIndex) => (
                <div className="keyboard-row" key={rowIndex}>
                    {row.map(renderKey)}
                </div>
            ))}
            <div className="keyboard-row">
                <Button className="key" onClick={onEnter}>Submit Guess</Button>
            </div>
        </div>
    );
};

export default Keyboard;
