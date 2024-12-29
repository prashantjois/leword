import React from 'react';
import ReactConfetti from 'react-confetti';

const Confetti = () => {
    const width = window.innerWidth;
    const height = window.innerHeight;

    return <ReactConfetti width={width} height={height} />;
};

export default Confetti;
