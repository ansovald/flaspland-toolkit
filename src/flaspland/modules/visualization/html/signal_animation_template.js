  const signal_SIGNAL_ID_state = signal_SIGNAL_ID_data[step];
  signal_SIGNAL_ID.classList.remove('red', 'green', 'off')
  if (signal_SIGNAL_ID_state === 'red') {
      signal_SIGNAL_ID.classList.add('red')
  } else if (signal_SIGNAL_ID_state === 'green') {
      signal_SIGNAL_ID.classList.add('green')
  } else if (signal_SIGNAL_ID_state === 'off') {
      signal_SIGNAL_ID.classList.add('off')
  }
