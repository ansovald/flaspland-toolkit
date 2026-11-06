  const state_TRAIN_ID = path_TRAIN_ID[step];
  train_TRAIN_ID.style.opacity = state_TRAIN_ID.opacity;
  train_TRAIN_ID_animate.setAttribute('dur', `${ms_per_step}ms`);
  train_TRAIN_ID_animate.setAttribute('keyPoints', `${state_TRAIN_ID.keyPoints}`);
  train_TRAIN_ID_animate.setAttribute('path', `${state_TRAIN_ID.motionPath}`);
  train_TRAIN_ID_animate.beginElement();
  train_TRAIN_ID_status.textContent = `Status: ${state_TRAIN_ID.status}`;
  train_TRAIN_ID_action.textContent = ` Action: ${state_TRAIN_ID.action}`;
  train_TRAIN_ID_pos.textContent = ` Position: [${state_TRAIN_ID.position}]`;
  // add signal logic: if "", add class "hide"; if "red" add class "red"; if "green" add class "green"
  train_TRAIN_ID_signal_group.classList.remove('hide', 'red', 'green');
  if (state_TRAIN_ID.signal === 'red') {
    train_TRAIN_ID_signal_group.classList.add('red');
  } else if (state_TRAIN_ID.signal === 'green') {
    train_TRAIN_ID_signal_group.classList.add('green');
  } else {
    train_TRAIN_ID_signal_group.classList.add('hide');
  }