export function isTrackableKey(key) {
  return typeof key === 'string' && (key === ' ' || key.length === 1);
}

export function registerKeyDown(pendingKeydowns, key, timestamp) {
  const updated = { ...pendingKeydowns };
  const queue = updated[key] ? [...updated[key]] : [];
  queue.push(timestamp);
  updated[key] = queue;
  return updated;
}

export function consumeKeyUp(pendingKeydowns, key, timestamp) {
  const updated = { ...pendingKeydowns };
  const queue = updated[key] ? [...updated[key]] : [];
  if (queue.length === 0) {
    return { pendingKeydowns: updated, keystroke: null };
  }

  const keyPressTime = queue.shift();
  if (queue.length === 0) {
    delete updated[key];
  } else {
    updated[key] = queue;
  }

  return {
    pendingKeydowns: updated,
    keystroke: {
      key,
      key_press_time: keyPressTime,
      key_release_time: timestamp,
    },
  };
}

export function getAnalysisWindow(keystrokes, size = 16) {
  if (keystrokes.length <= size) {
    return keystrokes;
  }
  return keystrokes.slice(keystrokes.length - size);
}
