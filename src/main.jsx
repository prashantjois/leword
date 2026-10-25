import { StrictMode, useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import candidateWordsRaw from '../data/candidate-words.txt?raw'
import './styles.css'

const WORD_LENGTH = 5
const MAX_GUESSES = 6
const WORDS = candidateWordsRaw
  .split(/\s+/)
  .map((word) => word.trim().toLowerCase())
  .filter((word) => word.length === WORD_LENGTH)

const KEY_ROWS = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
const EMPTY_STATS = { played: 0, wins: 0, streak: 0, bestStreak: 0 }
const COMPLETED_WORDS_KEY = 'leword-completed-words'
const COMPLETED_WORD_TTL = 1000 * 60 * 60 * 24 * 30 * 6
const CURRENT_ANSWER_KEY = 'leword-current-answer'
const CURRENT_GAME_KEY = 'leword-current-game'
const FIREWORK_COLORS = ['#7a9a46', '#c9a84d', '#d67c62', '#6d9ab8', '#b477a9', '#e29a54']

function scoreGuess(guess, answer) {
  const result = Array(WORD_LENGTH).fill('absent')
  const remaining = [...answer]

  for (let index = 0; index < WORD_LENGTH; index += 1) {
    if (guess[index] === answer[index]) {
      result[index] = 'correct'
      remaining[index] = null
    }
  }

  for (let index = 0; index < WORD_LENGTH; index += 1) {
    if (result[index] === 'correct') continue
    const matchIndex = remaining.indexOf(guess[index])
    if (matchIndex !== -1) {
      result[index] = 'present'
      remaining[matchIndex] = null
    }
  }

  return result
}

function getRandomWord(completedWords = []) {
  const completed = new Set(completedWords.map(({ word }) => word))
  const availableWords = WORDS.filter((word) => !completed.has(word))
  const wordPool = availableWords.length ? availableWords : WORDS
  return wordPool[Math.floor(Math.random() * wordPool.length)]
}

function loadStats() {
  try {
    return { ...EMPTY_STATS, ...JSON.parse(localStorage.getItem('leword-stats')) }
  } catch {
    return EMPTY_STATS
  }
}

function loadCompletedWords() {
  try {
    const cutoff = Date.now() - COMPLETED_WORD_TTL
    const savedWords = JSON.parse(localStorage.getItem(COMPLETED_WORDS_KEY))
    const activeWords = Array.isArray(savedWords)
      ? savedWords.filter(({ word, completedAt }) => WORDS.includes(word) && completedAt > cutoff)
      : []
    localStorage.setItem(COMPLETED_WORDS_KEY, JSON.stringify(activeWords))
    return activeWords
  } catch {
    return []
  }
}

function loadGameState(completedWords) {
  try {
    const savedState = JSON.parse(localStorage.getItem(CURRENT_GAME_KEY))
    const validGuesses = Array.isArray(savedState?.guesses)
      && savedState.guesses.length <= MAX_GUESSES
      && savedState.guesses.every((guess) => typeof guess === 'string' && guess.length === WORD_LENGTH)
    const validCurrent = typeof savedState?.current === 'string' && savedState.current.length <= WORD_LENGTH
    const validAnswer = typeof savedState?.answer === 'string'
      && WORDS.includes(savedState.answer)
      && !completedWords.some(({ word }) => word === savedState.answer)

    if (validAnswer && validGuesses && validCurrent) {
      return savedState
    }

    const savedAnswer = localStorage.getItem(CURRENT_ANSWER_KEY)
    if (savedAnswer && !completedWords.some(({ word }) => word === savedAnswer) && WORDS.includes(savedAnswer)) {
      return { answer: savedAnswer, guesses: [], current: '' }
    }
  } catch {
    // Fall back to a newly selected word when storage is unavailable.
  }
  return { answer: getRandomWord(completedWords), guesses: [], current: '' }
}

function CheatPage() {
  const answer = localStorage.getItem(CURRENT_ANSWER_KEY)

  return (
    <main className="app-shell cheat-page">
      <div className="cheat-card">
        <p className="section-kicker">Le Word · cheat</p>
        <h2>The word is<br /><em>{answer ? answer.toUpperCase() : 'not set yet'}</em></h2>
        <p className="cheat-note">This reveals the answer for the active round.</p>
        <a className="new-game-button cheat-link" href={import.meta.env.BASE_URL}>Back to game <span>↗</span></a>
      </div>
    </main>
  )
}

function Fireworks() {
  const bursts = [
    ['12%', '22%'], ['31%', '39%'], ['51%', '16%'], ['72%', '30%'],
    ['88%', '19%'], ['23%', '68%'], ['68%', '63%'],
  ]

  return (
    <div className="fireworks" aria-hidden="true">
      {bursts.map(([left, top], burstIndex) => (
        <div className="firework-burst" key={`${left}-${top}`} style={{ '--burst-left': left, '--burst-top': top }}>
          {Array.from({ length: 16 }).map((_, sparkIndex) => (
            <span
              className="spark"
              key={sparkIndex}
              style={{
                '--spark-angle': `${sparkIndex * 22.5}deg`,
                '--spark-color': FIREWORK_COLORS[(sparkIndex + burstIndex) % FIREWORK_COLORS.length],
                '--spark-delay': `${burstIndex * 0.18}s`,
              }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

function App() {
  const [completedWords, setCompletedWords] = useState(loadCompletedWords)
  const [initialGame] = useState(() => loadGameState(completedWords))
  const [answer, setAnswer] = useState(initialGame.answer)
  const [guesses, setGuesses] = useState(initialGame.guesses)
  const [current, setCurrent] = useState(initialGame.current)
  const [message, setMessage] = useState('')
  const [warning, setWarning] = useState('')
  const [stats, setStats] = useState(loadStats)
  const [showHelp, setShowHelp] = useState(false)

  const gameOver = guesses.length >= MAX_GUESSES || guesses.some((guess) => guess === answer)
  const won = guesses.at(-1) === answer

  useEffect(() => {
    localStorage.setItem(CURRENT_ANSWER_KEY, answer)
    localStorage.setItem(CURRENT_GAME_KEY, JSON.stringify({ answer, guesses, current }))
  }, [answer, guesses, current])

  const keyboardState = useMemo(() => {
    const state = {}
    guesses.forEach((guess) => {
      scoreGuess(guess, answer).forEach((status, index) => {
        const letter = guess[index]
        const previous = state[letter]
        if (status === 'correct' || (status === 'present' && previous !== 'correct')) state[letter] = status
        else if (!previous) state[letter] = status
      })
    })
    return state
  }, [guesses, answer])

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Enter') submitGuess()
      else if (event.key === 'Backspace') setCurrent((value) => value.slice(0, -1))
      else if (/^[a-zA-Z]$/.test(event.key)) addLetter(event.key)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  })

  useEffect(() => {
    if (!warning) return undefined
    const timeout = window.setTimeout(() => setWarning(''), 1800)
    return () => window.clearTimeout(timeout)
  }, [warning])

  function addLetter(letter) {
    if (gameOver) return
    setMessage('')
    setCurrent((value) => (value.length < WORD_LENGTH ? value + letter.toLowerCase() : value))
  }

  function submitGuess() {
    if (gameOver) return
    if (current.length !== WORD_LENGTH) {
      setMessage('Five letters, please.')
      return
    }
    if (!WORDS.includes(current)) {
      setWarning('That word is not in the word list.')
      return
    }
    const nextGuesses = [...guesses, current]
    setGuesses(nextGuesses)
    setCurrent('')
    if (current === answer) finishGame(true, nextGuesses.length)
    else if (nextGuesses.length === MAX_GUESSES) finishGame(false, nextGuesses.length)
  }

  function finishGame(isWin, guessCount) {
    const nextStats = {
      played: stats.played + 1,
      wins: stats.wins + (isWin ? 1 : 0),
      streak: isWin ? stats.streak + 1 : 0,
      bestStreak: isWin ? Math.max(stats.bestStreak, stats.streak + 1) : stats.bestStreak,
    }
    setStats(nextStats)
    localStorage.setItem('leword-stats', JSON.stringify(nextStats))
    setCompletedWords((currentWords) => {
      const nextWords = [...currentWords.filter(({ word }) => word !== answer), { word: answer, completedAt: Date.now() }]
      localStorage.setItem(COMPLETED_WORDS_KEY, JSON.stringify(nextWords))
      return nextWords
    })
    setMessage(isWin ? `Solved in ${guessCount}/${MAX_GUESSES}.` : `The word was ${answer.toUpperCase()}.`)
  }

  function startNewGame() {
    setAnswer(getRandomWord(completedWords))
    setGuesses([])
    setCurrent('')
    setMessage('')
  }

  return (
    <main className="app-shell">
      {won && <Fireworks />}
      {warning && <div className="warning-toast" role="alert">{warning}</div>}
      <header className="topbar">
        <div className="brand-lockup">
          <img className="brand-mark" src={`${import.meta.env.BASE_URL}le-word-logo.png`} alt="Le Word logo" />
          <div>
            <p className="eyebrow">A little word game</p>
            <h1>Le Word</h1>
          </div>
        </div>
        <div className="top-actions">
          <button className="icon-button" onClick={() => setShowHelp(true)} aria-label="How to play">?</button>
          <button className="new-game-button" onClick={startNewGame}>New word <span>↗</span></button>
        </div>
      </header>

      <section className="intro-row">
        <div>
          <h2>Find the word<br /><em>in six tries.</em></h2>
        </div>
      </section>

      <section className="game-card" aria-label="Le Word game">
        <div className="game-meta"><span>{guesses.length}/{MAX_GUESSES} guesses</span><span className="meta-dot">•</span><span>5 letters</span></div>
        <div className="board" role="grid" aria-label="Guess board" tabIndex="0">
          {Array.from({ length: MAX_GUESSES }).map((_, rowIndex) => {
            const guess = guesses[rowIndex]
            const isCurrent = rowIndex === guesses.length && !gameOver
            const statuses = guess ? scoreGuess(guess, answer) : []
            return <div className={`row ${isCurrent ? 'current-row' : ''}`} role="row" key={rowIndex}>
              {Array.from({ length: WORD_LENGTH }).map((__, letterIndex) => {
                const letter = guess?.[letterIndex] ?? (isCurrent ? current[letterIndex] : '')
                const status = statuses[letterIndex]
                return <div className={`tile ${status ?? ''} ${letter ? 'filled' : ''}`} role="gridcell" key={letterIndex}>{letter?.toUpperCase()}</div>
              })}
            </div>
          })}
        </div>
        <div className="message" aria-live="polite">{message || ' '}</div>
        <div className="keyboard" aria-label="Keyboard">
          {KEY_ROWS.map((row, rowIndex) => <div className={`key-row letter-row ${rowIndex === 2 ? 'letter-row-actions' : ''}`} key={row}>
            {rowIndex === 2 && <button className="key wide guess-key" onClick={submitGuess}>Guess</button>}
            {row.split('').map((letter) => <button className={`key ${keyboardState[letter] ?? ''}`} onClick={() => addLetter(letter)} key={letter}>{letter}</button>)}
            {rowIndex === 2 && <button className="key wide backspace-key" aria-label="Backspace" onClick={() => setCurrent((value) => value.slice(0, -1))}>⌫</button>}
          </div>)}
        </div>
      </section>

      <section className="stats-strip" aria-label="Your stats">
        <div><strong>{stats.played}</strong><span>Played</span></div>
        <div><strong>{stats.played ? Math.round((stats.wins / stats.played) * 100) : 0}%</strong><span>Win rate</span></div>
        <div><strong>{stats.streak}</strong><span>Current streak</span></div>
        <div><strong>{stats.bestStreak}</strong><span>Best streak</span></div>
      </section>

      <footer><span>Made for a five-minute break.</span></footer>

      {showHelp && <div className="modal-backdrop" onClick={() => setShowHelp(false)}>
        <section className="help-modal" onClick={(event) => event.stopPropagation()}>
          <button className="close-button" onClick={() => setShowHelp(false)} aria-label="Close">×</button>
          <p className="section-kicker">The rules</p>
          <h2>How to play</h2>
          <p>Guess the five-letter word in six tries. After each guess, the tiles reveal how close you are.</p>
          <div className="legend"><span className="legend-tile correct">W</span><span>Correct letter, correct spot</span></div>
          <div className="legend"><span className="legend-tile present">O</span><span>Letter is in the word, wrong spot</span></div>
          <div className="legend"><span className="legend-tile absent">R</span><span>Letter is not in the word</span></div>
          <p className="small-note">Repeated letters count only as many times as they appear in the answer.</p>
        </section>
      </div>}
    </main>
  )
}

const requestedPath = new URLSearchParams(window.location.search).get('route') || window.location.pathname
const isCheatPage = requestedPath.replace(/\/+$/, '').endsWith('/cheat')
createRoot(document.getElementById('root')).render(<StrictMode>{isCheatPage ? <CheatPage /> : <App />}</StrictMode>)
