  const state_TRAIN_ID = path_TRAIN_ID[step];
  train_TRAIN_ID.style.opacity = state_TRAIN_ID.opacity;
  train_TRAIN_ID_animate.setAttribute('dur', `${ms_per_step}ms`);
  train_TRAIN_ID_animate.setAttribute('keyPoints', `${state_TRAIN_ID.keyPoints}`);
  train_TRAIN_ID_animate.setAttribute('path', `${state_TRAIN_ID.motionPath}`);
  train_TRAIN_ID_animate.beginElement();
  train_TRAIN_ID_status.textContent = `Status: ${state_TRAIN_ID.status}`;
  train_TRAIN_ID_action.textContent = ` Action: ${state_TRAIN_ID.action}`;
  train_TRAIN_ID_pos.textContent = ` Position: [${state_TRAIN_ID.position}]`;
