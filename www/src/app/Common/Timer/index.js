import React, { useState, useEffect } from 'react';

const Timer = ({ isActive }) => {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    let interval = null;
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(seconds => seconds + 1);
      }, 100);
    } else if (!isActive && seconds !== 0) {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isActive, seconds]);

  return (
    <div className="timer">
      {(seconds / 10).toFixed(2)}s
    </div>
  );
};

Timer.defaultProps = {
  isActive: true
}

export default Timer;
