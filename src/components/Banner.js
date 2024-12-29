import React from 'react';
import { Modal, Button } from 'react-bootstrap';

const Banner = ({ win, word }) => {
    return (
        <Modal.Dialog className="banner" centered>
            <Modal.Header style={{ borderBottom: 'none' }}>
                <Modal.Title>{win ? 'Congratulations!' : 'Game Over!'}</Modal.Title>
            </Modal.Header>

            <Modal.Body>
                <p style={{ color: 'black' }}>{win ? 'You guessed the word!' : `The word was ${word}.`}</p>
            </Modal.Body>

            <Modal.Footer style={{ borderTop: 'none' }}>
                <Button variant="secondary" onClick={() => window.location.reload()}>
                    Play Again
                </Button>
            </Modal.Footer>
        </Modal.Dialog>
    );
};

export default Banner;
