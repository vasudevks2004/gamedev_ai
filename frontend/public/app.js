// Thangan — Personal GameDev AI Companion Client Logic

let activeMode = 'auto';
let isVoiceRecording = false;
let lastInputWasVoice = false;
let speechRecognition = null;
let screenStream = null;

// DOM Elements
const chatStream = document.getElementById('chat-stream');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const typingIndicator = document.getElementById('typing-indicator');
const pttBtn = document.getElementById('ptt-btn');
const voiceHudBtn = document.getElementById('voice-hud-btn');
const screenShareBtn = document.getElementById('screen-share-btn');
const screenPreviewBar = document.getElementById('screen-preview-bar');
const screenVideo = document.getElementById('screen-video');
const closeScreenBtn = document.getElementById('close-screen-btn');

// Left Task Panel & Right MiniBot Panel
const taskPanel = document.getElementById('task-panel');
const toggleTaskPanelBtn = document.getElementById('toggle-task-panel-btn');
const minibotPanel = document.getElementById('minibot-panel');
const toggleMinibotBtn = document.getElementById('toggle-minibot-btn');

// Task Breakdown Elements
const taskTitleDisplay = document.getElementById('task-title-display');
const overallTaskPct = document.getElementById('overall-task-pct');
const overallTaskFill = document.getElementById('overall-task-fill');
const topicChartContainer = document.getElementById('topic-chart-container');
const checklistCountDisplay = document.getElementById('checklist-count-display');
const taskItemsContainer = document.getElementById('task-items-container');

// Assign Task Modal
const assignTaskBtn = document.getElementById('assign-task-btn');
const assignTaskModal = document.getElementById('assign-task-modal');
const closeAssignTaskBtn = document.getElementById('close-assign-task-btn');
const cancelAssignTaskBtn = document.getElementById('cancel-assign-task-btn');
const assignTaskForm = document.getElementById('assign-task-form');

// MiniBot Elements
const tipsContainer = document.getElementById('tips-container');
const refreshTipsBtn = document.getElementById('refresh-tips-btn');
const minibotMessages = document.getElementById('minibot-messages');
const minibotForm = document.getElementById('minibot-form');
const minibotInput = document.getElementById('minibot-input');

// Context & Settings Modals
const quickContextPill = document.getElementById('quick-context-pill');
const contextModal = document.getElementById('context-modal');
const closeContextModalBtn = document.getElementById('close-context-modal-btn');
const cancelContextBtn = document.getElementById('cancel-context-btn');
const contextForm = document.getElementById('context-form');

const settingsModal = document.getElementById('settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const closeSettingsModalBtn = document.getElementById('close-settings-modal-btn');
const cancelSettingsBtn = document.getElementById('cancel-settings-btn');
const settingsForm = document.getElementById('settings-form');

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
  await fetchStatus();
  await fetchContext();
  await loadActiveTask();
  await loadMiniBotTips();
  setupEventListeners();
  setupSpeechRecognition();
});

// Fetch Status
async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) return;
    const data = await res.json();
    console.log('[Thangan Companion Ready]', data);
  } catch (err) {
    console.warn('Status check failed:', err);
  }
}

// Fetch Context
async function fetchContext() {
  try {
    const res = await fetch('/api/context');
    if (!res.ok) return;
    const ctx = await res.json();
    document.getElementById('pill-project').textContent = ctx.project_name || 'ShooterGame';
    document.getElementById('pill-file').textContent = ctx.current_file || 'WeaponComponent.cpp';
  } catch (err) {
    console.error('Failed to load context:', err);
  }
}

// Load Active Task & Topic Chart
async function loadActiveTask() {
  try {
    const res = await fetch('/api/task/active');
    if (!res.ok) return;
    const taskData = await res.json();
    renderTaskData(taskData);
  } catch (err) {
    console.error('Failed to load task:', err);
  }
}

function renderTaskData(data) {
  taskTitleDisplay.textContent = data.task_name;
  const pct = data.overall_progress || 0;
  overallTaskPct.textContent = `${pct}%`;
  overallTaskFill.style.width = `${pct}%`;

  // Render Topic Breakdown Chart
  topicChartContainer.innerHTML = '';
  const breakdown = data.topic_breakdown || {};
  const topicEntries = Object.entries(breakdown);

  if (topicEntries.length === 0) {
    topicChartContainer.innerHTML = '<div style="font-size:11px; color:#64748b;">No topic data</div>';
  } else {
    topicEntries.forEach(([topicName, stats]) => {
      const row = document.createElement('div');
      row.className = 'topic-row';

      const tagClass = getTopicClass(topicName);
      const fillGradient = getTopicGradient(topicName);

      row.innerHTML = `
        <div class="topic-meta">
          <span class="topic-tag ${tagClass}">${topicName}</span>
          <span class="topic-val">${stats.completed}/${stats.total} (${stats.percent}%)</span>
        </div>
        <div class="topic-track">
          <div class="topic-fill" style="width: ${stats.percent}%; background: ${fillGradient};"></div>
        </div>
      `;
      topicChartContainer.appendChild(row);
    });
  }

  // Render Checklist
  taskItemsContainer.innerHTML = '';
  const items = data.items || [];
  const completedCount = items.filter(i => i.completed).length;
  checklistCountDisplay.textContent = `${completedCount}/${items.length}`;

  items.forEach(item => {
    const itemRow = document.createElement('div');
    itemRow.className = `task-item-row ${item.completed ? 'done' : ''}`;
    
    const tagClass = getTopicClass(item.category);
    
    itemRow.innerHTML = `
      <input type="checkbox" class="task-checkbox" ${item.completed ? 'checked' : ''} data-id="${item.id}" />
      <span class="task-title-text">${item.title}</span>
      <span class="topic-tag ${tagClass}">${item.category}</span>
      <button class="delete-task-btn" title="Remove task" data-id="${item.id}">
        <i class="fa-solid fa-xmark"></i>
      </button>
    `;

    const checkbox = itemRow.querySelector('.task-checkbox');
    checkbox.addEventListener('change', async (e) => {
      e.stopPropagation();
      await toggleTaskItem(item.id);
    });

    const deleteBtn = itemRow.querySelector('.delete-task-btn');
    deleteBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      await deleteTaskItem(item.id);
    });

    itemRow.addEventListener('click', async (e) => {
      if (e.target.tagName !== 'INPUT' && !e.target.closest('.delete-task-btn')) {
        checkbox.checked = !checkbox.checked;
        await toggleTaskItem(item.id);
      }
    });

    taskItemsContainer.appendChild(itemRow);
  });
}

async function toggleTaskItem(itemId) {
  try {
    const res = await fetch('/api/task/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId })
    });
    if (!res.ok) return;
    const updated = await res.json();
    renderTaskData(updated);
  } catch (err) {
    console.error('Failed to toggle task:', err);
  }
}

async function addTaskItem(title, category) {
  try {
    const res = await fetch('/api/task/item/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, category })
    });
    if (!res.ok) return;
    const updated = await res.json();
    renderTaskData(updated);
  } catch (err) {
    console.error('Failed to add task item:', err);
  }
}

async function deleteTaskItem(itemId) {
  try {
    const res = await fetch('/api/task/item/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId })
    });
    if (!res.ok) return;
    const updated = await res.json();
    renderTaskData(updated);
  } catch (err) {
    console.error('Failed to delete task item:', err);
  }
}

function getTopicClass(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('unreal')) return 'unreal';
  if (cat.includes('blender')) return 'blender';
  if (cat.includes('c++')) return 'cpp';
  if (cat.includes('blueprint')) return 'blueprints';
  if (cat.includes('anim')) return 'animation';
  return 'unreal';
}

function getTopicGradient(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('unreal')) return 'linear-gradient(90deg, #0284c7, #38bdf8)';
  if (cat.includes('blender')) return 'linear-gradient(90deg, #ea580c, #fb923c)';
  if (cat.includes('c++')) return 'linear-gradient(90deg, #16a34a, #4ade80)';
  if (cat.includes('blueprint')) return 'linear-gradient(90deg, #06b6d4, #67e8f9)';
  if (cat.includes('anim')) return 'linear-gradient(90deg, #9333ea, #c084fc)';
  return 'linear-gradient(90deg, #0070f3, #00dfd8)';
}

// Load Contextual MiniBot Tips
async function loadMiniBotTips() {
  try {
    const res = await fetch('/api/minibot/suggest', { method: 'POST' });
    if (!res.ok) return;
    const data = await res.json();
    renderMiniBotTips(data.tips || []);
  } catch (err) {
    console.error('Failed to load tips:', err);
  }
}

function renderMiniBotTips(tips) {
  tipsContainer.innerHTML = '';
  tips.forEach(t => {
    const div = document.createElement('div');
    div.className = 'tip-item';
    div.innerHTML = `
      <i class="fa-solid ${t.icon} tip-icon"></i>
      <div class="tip-content">
        <strong>${t.title}</strong>
        <p>${t.tip}</p>
      </div>
    `;
    tipsContainer.appendChild(div);
  });
}

// Setup Event Listeners
function setupEventListeners() {
  // Panel Toggles
  toggleTaskPanelBtn.addEventListener('click', () => {
    taskPanel.classList.toggle('collapsed');
    toggleTaskPanelBtn.classList.toggle('active');
  });

  toggleMinibotBtn.addEventListener('click', () => {
    minibotPanel.classList.toggle('collapsed');
    toggleMinibotBtn.classList.toggle('active');
  });

  // Mode Selection Tags
  document.querySelectorAll('.mode-tag').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.mode-tag').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeMode = btn.dataset.mode;
    });
  });

  // Prompt Chips
  document.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const prompt = btn.dataset.prompt;
      if (prompt) {
        chatInput.value = prompt;
        sendMessage(prompt);
      }
    });
  });

  // Main Chat Form
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (msg) {
      sendMessage(msg);
      chatInput.value = '';
    }
  });

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // Assign Task Modal
  assignTaskBtn.addEventListener('click', () => assignTaskModal.style.display = 'flex');
  closeAssignTaskBtn.addEventListener('click', () => assignTaskModal.style.display = 'none');
  cancelAssignTaskBtn.addEventListener('click', () => assignTaskModal.style.display = 'none');

  assignTaskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskName = document.getElementById('input-new-task-name').value.trim();
    const taskDesc = document.getElementById('input-new-task-desc').value.trim();
    if (!taskName) return;

    try {
      const res = await fetch('/api/task/assign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_name: taskName, description: taskDesc })
      });
      if (res.ok) {
        const updated = await res.json();
        renderTaskData(updated);
        await fetchContext();
        await loadMiniBotTips();
        assignTaskModal.style.display = 'none';
        assignTaskForm.reset();
        appendMessage('assistant', `I have mapped out the roadmap and created the topic progress chart for **${taskName}**! You can track your progress on the left panel.`, 'planning');
      }
    } catch (err) {
      alert('Error assigning task: ' + err);
    }
  });

  // MiniBot Form & Inquiries
  refreshTipsBtn.addEventListener('click', loadMiniBotTips);

  document.querySelectorAll('.quick-inq-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.dataset.q;
      if (q) askMiniBot(q);
    });
  });

  minibotForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = minibotInput.value.trim();
    if (q) {
      askMiniBot(q);
      minibotInput.value = '';
    }
  });

  // Context Modal
  quickContextPill.addEventListener('click', () => {
    document.getElementById('input-project-name').value = document.getElementById('pill-project').textContent;
    document.getElementById('input-current-file').value = document.getElementById('pill-file').textContent;
    contextModal.style.display = 'flex';
  });

  closeContextModalBtn.addEventListener('click', () => contextModal.style.display = 'none');
  cancelContextBtn.addEventListener('click', () => contextModal.style.display = 'none');

  contextForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      project_name: document.getElementById('input-project-name').value,
      engine: document.getElementById('input-engine-version').value,
      current_task: document.getElementById('input-current-task').value,
      current_file: document.getElementById('input-current-file').value,
      recent_error: document.getElementById('input-recent-error').value.trim() || null
    };
    try {
      await fetch('/api/context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      await fetchContext();
      await loadMiniBotTips();
      contextModal.style.display = 'none';
    } catch (err) {
      alert('Error updating context: ' + err);
    }
  });

  // Settings Modal
  settingsBtn.addEventListener('click', () => settingsModal.style.display = 'flex');
  closeSettingsModalBtn.addEventListener('click', () => settingsModal.style.display = 'none');
  cancelSettingsBtn.addEventListener('click', () => settingsModal.style.display = 'none');

  settingsForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      active_provider: document.getElementById('select-provider').value,
      ollama_model: document.getElementById('input-ollama-model').value,
      ollama_base_url: document.getElementById('input-ollama-url').value
    };
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      await fetchStatus();
      settingsModal.style.display = 'none';
    } catch (err) {
      alert('Error updating settings: ' + err);
    }
  });

  // Screen Share, Vision & PTT
  screenShareBtn.addEventListener('click', toggleScreenShare);
  closeScreenBtn.addEventListener('click', stopScreenShare);
  const inspectFrameBtn = document.getElementById('inspect-frame-btn');
  if (inspectFrameBtn) inspectFrameBtn.addEventListener('click', () => performScreenInspection("Inspect this screen for errors and what's wrong."));
  pttBtn.addEventListener('click', toggleVoice);
  voiceHudBtn.addEventListener('click', toggleVoice);

  // Inline Add Subtask Form
  const inlineAddTaskForm = document.getElementById('inline-add-task-form');
  if (inlineAddTaskForm) {
    inlineAddTaskForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('inline-task-input');
      const catSelect = document.getElementById('inline-task-category');
      const title = input.value.trim();
      if (title) {
        await addTaskItem(title, catSelect.value);
        input.value = '';
      }
    });
  }

  // New Modals: Study Dashboard, Resources, Project Scanner
  setupNewModals();
}

// Ask Right MiniBot
async function askMiniBot(question) {
  // Append user inquiry
  appendMiniBotMsg('user', question);

  try {
    const res = await fetch('/api/minibot/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    if (!res.ok) throw new Error('Failed to reach minibot');
    const data = await res.json();
    appendMiniBotMsg('bot', data.answer);
  } catch (err) {
    appendMiniBotMsg('bot', '⚠️ Error contacting Thangan Mini.');
  }
}

function appendMiniBotMsg(role, text) {
  const div = document.createElement('div');
  div.className = `minibot-msg ${role}`;
  div.innerHTML = `
    <span class="sender">${role === 'user' ? 'Ashwin' : 'Thangan Mini'}:</span>
    <p>${renderMarkdown(text)}</p>
  `;
  minibotMessages.appendChild(div);
  minibotMessages.scrollTop = minibotMessages.scrollHeight;
}

// Send Main Chat Message
async function sendMessage(text) {
  appendMessage('user', text, activeMode);
  setTyping(true);

  // If screen sharing is active and question asks about screen or errors, route through Screen Vision
  const textLower = text.toLowerCase();
  const asksAboutScreen = screenStream && (
    textLower.includes("what's wrong") || 
    textLower.includes("what is wrong") || 
    textLower.includes("look at") || 
    textLower.includes("screen") || 
    textLower.includes("error") || 
    textLower.includes("inspect") ||
    textLower.includes("why is this failing") ||
    textLower.includes("why is this crashing")
  );

  if (asksAboutScreen) {
    await performScreenInspection(text, false);
    setTyping(false);
    return;
  }

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, mode: activeMode })
    });

    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const data = await res.json();
    appendMessage('assistant', data.reply, data.mode);

    if ((lastInputWasVoice || isVoiceRecording) && 'speechSynthesis' in window) {
      speakResponse(data.reply);
      lastInputWasVoice = false;
    }
  } catch (err) {
    appendMessage('assistant', `⚠️ Connection Notice: Could not reach mentor backend (${err.message}). Make sure the backend server is active on port 8000.`, 'error');
  } finally {
    setTyping(false);
  }
}

function appendMessage(role, text, mode) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-message ${role}-message`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-bolt"></i>';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const header = document.createElement('div');
  header.className = 'bubble-header';
  
  const senderName = document.createElement('span');
  senderName.className = 'author';
  senderName.textContent = role === 'user' ? 'Ashwin' : 'Thangan';

  const modeBadge = document.createElement('span');
  modeBadge.className = `badge mode-badge ${mode || 'teaching'}`;
  modeBadge.textContent = (mode || 'auto').toUpperCase();

  header.appendChild(senderName);
  header.appendChild(modeBadge);

  if (role === 'assistant') {
    const speakBtn = document.createElement('button');
    speakBtn.className = 'speech-read-btn';
    speakBtn.title = 'Listen to Thangan';
    speakBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
    speakBtn.addEventListener('click', () => speakResponse(text));
    header.appendChild(speakBtn);
  }

  const timeSpan = document.createElement('span');
  timeSpan.className = 'time';
  timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  header.appendChild(timeSpan);

  const body = document.createElement('div');
  body.className = 'bubble-text';
  body.innerHTML = renderMarkdown(text);

  bubble.appendChild(header);
  bubble.appendChild(body);

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(bubble);

  chatStream.appendChild(msgDiv);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function renderMarkdown(md) {
  if (!md) return '';
  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/```([a-zA-Z0-9_\-]+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre><code class="language-${lang || 'cpp'}">${code}</code></pre>`;
    })
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/^### (.*$)/gim, '<h4>$1</h4>')
    .replace(/^## (.*$)/gim, '<h3>$1</h3>')
    .replace(/^# (.*$)/gim, '<h2>$1</h2>')
    .replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  return `<p>${html}</p>`.replace(/<p><\/p>/g, '');
}

function setTyping(isTyping) {
  const spinner = typingIndicator.querySelector('i');
  if (isTyping) {
    spinner.style.display = 'inline-block';
    typingIndicator.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Thangan Thinking...';
  } else {
    spinner.style.display = 'none';
    typingIndicator.textContent = 'Ready';
  }
}

// Web Speech API
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  speechRecognition = new SpeechRecognition();
  speechRecognition.continuous = false;
  speechRecognition.interimResults = false;
  speechRecognition.lang = 'en-US';

  speechRecognition.onstart = () => {
    isVoiceRecording = true;
    pttBtn.classList.add('recording');
    document.getElementById('voice-btn-text').textContent = 'Listening...';
    voiceHudBtn.classList.add('active');
  };

  speechRecognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
    lastInputWasVoice = true;
    sendMessage(transcript);
  };

  speechRecognition.onerror = (event) => {
    console.error('Speech error:', event.error);
    stopVoice();
  };

  speechRecognition.onend = () => {
    stopVoice();
  };
}

function toggleVoice() {
  if (!speechRecognition) {
    alert('Voice input requires a browser supporting Web Speech Recognition (Chrome / Edge).');
    return;
  }
  if (isVoiceRecording) {
    speechRecognition.stop();
    stopVoice();
  } else {
    try {
      speechRecognition.start();
    } catch (e) {
      console.warn('Speech start error:', e);
    }
  }
}

function stopVoice() {
  isVoiceRecording = false;
  pttBtn.classList.remove('recording');
  document.getElementById('voice-btn-text').textContent = 'Voice';
  voiceHudBtn.classList.remove('active');
}

function speakResponse(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();

  // Clean out code blocks, markdown headings, citations, and symbols for natural spoken audio
  let spoken = text
    .replace(/```[\s\S]*?```/g, '')             // strip code blocks completely
    .replace(/`([^`]+)`/g, '$1')                 // inline code to spoken words
    .replace(/^#{1,6}\s*([^\n]+)/gm, '$1.')      // headings to sentences
    .replace(/\*\*([^*]+)\*\*/g, '$1')           // bold markers
    .replace(/\*([^*]+)\*/g, '$1')               // italic markers
    .replace(/>\s*([^\n]+)/gm, '$1')             // blockquotes
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')     // markdown links to text
    .replace(/^[-*•]\s+/gm, '')                  // bullets
    .replace(/^\d+\.\s+/gm, '')                  // numbered lists
    .replace(/\s+/g, ' ')                        // multiple spaces
    .trim();

  if (!spoken) return;

  // Speak the conversational essence (up to 2 sentences or 220 chars) so Thangan sounds natural
  const sentenceMatches = spoken.match(/[^.!?]+[.!?]+/g);
  let summary = '';
  if (sentenceMatches && sentenceMatches.length > 0) {
    summary = sentenceMatches.slice(0, 2).join(' ').trim();
  }
  if (!summary || summary.length < 15) {
    summary = spoken.slice(0, 200).trim();
  }
  if (summary.length > 240) {
    summary = summary.slice(0, 235) + '...';
  }

  const utterance = new SpeechSynthesisUtterance(summary);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  // Pick a smooth natural voice if available
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => 
    v.lang.startsWith('en') && (
      v.name.includes('Natural') || 
      v.name.includes('Google') || 
      v.name.includes('Aria') || 
      v.name.includes('David') ||
      v.name.includes('Jenny')
    )
  ) || voices.find(v => v.lang.startsWith('en'));

  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  window.speechSynthesis.speak(utterance);
}

// Screen Sharing
async function toggleScreenShare() {
  if (screenStream) {
    stopScreenShare();
    return;
  }
  try {
    screenStream = await navigator.mediaDevices.getDisplayMedia({
      video: { cursor: "always" },
      audio: false
    });
    screenVideo.srcObject = screenStream;
    screenPreviewBar.style.display = 'flex';
    screenShareBtn.classList.add('active');
    document.getElementById('screen-btn-text').textContent = 'Screen Active';

    screenStream.getVideoTracks()[0].addEventListener('ended', () => {
      stopScreenShare();
    });
  } catch (err) {
    console.warn('Screen share canceled or unsupported:', err);
  }
}

function stopScreenShare() {
  if (screenStream) {
    screenStream.getTracks().forEach(track => track.stop());
    screenStream = null;
  }
  screenVideo.srcObject = null;
  screenPreviewBar.style.display = 'none';
  screenShareBtn.classList.remove('active');
  document.getElementById('screen-btn-text').textContent = 'Screen';
}

// Frame Capture from active video stream
function captureScreenFrame() {
  if (!screenVideo || !screenVideo.videoWidth) {
    // Generate placeholder 1x1 base64 png if video stream is not active
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
  }
  const canvas = document.getElementById('screen-canvas') || document.createElement('canvas');
  canvas.width = screenVideo.videoWidth;
  canvas.height = screenVideo.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(screenVideo, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.85);
}

// Perform Screen Inspection with 6-step diagnosis
async function performScreenInspection(promptText = "What's wrong here?", appendUserMsg = true) {
  if (appendUserMsg) {
    appendMessage('user', promptText, 'vision');
  }
  setTyping(true);

  const frameBase64 = captureScreenFrame();

  try {
    const res = await fetch('/api/screen/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: frameBase64,
        prompt: promptText
      })
    });

    if (!res.ok) throw new Error(`Inspection failed (${res.status})`);
    const data = await res.json();
    appendMessage('assistant', data.diagnosis, 'debugging');

    if (isVoiceRecording && 'speechSynthesis' in window) {
      speakResponse(data.diagnosis);
    }
  } catch (err) {
    appendMessage('assistant', `⚠️ Screen Vision Notice: ${err.message}. Make sure backend is running.`, 'error');
  } finally {
    setTyping(false);
  }
}

// Setup New Modals: Study, Resources, Project
function setupNewModals() {
  // Study Dashboard Modal
  const studyDashboardBtn = document.getElementById('study-dashboard-btn');
  const studyModal = document.getElementById('study-modal');
  const closeStudyModalBtn = document.getElementById('close-study-modal-btn');

  if (studyDashboardBtn && studyModal) {
    studyDashboardBtn.addEventListener('click', async () => {
      studyModal.style.display = 'flex';
      await loadStudyDashboard();
    });
    if (closeStudyModalBtn) {
      closeStudyModalBtn.addEventListener('click', () => studyModal.style.display = 'none');
    }
  }

  // Resources Modal
  const resourcesModalBtn = document.getElementById('resources-modal-btn');
  const resourcesModal = document.getElementById('resources-modal');
  const closeResourcesModalBtn = document.getElementById('close-resources-modal-btn');
  const resourceSearchBtn = document.getElementById('resource-search-btn');
  const resourceSearchInput = document.getElementById('resource-search-input');

  if (resourcesModalBtn && resourcesModal) {
    resourcesModalBtn.addEventListener('click', async () => {
      resourcesModal.style.display = 'flex';
      await loadResources("Unreal Engine");
    });
    if (closeResourcesModalBtn) {
      closeResourcesModalBtn.addEventListener('click', () => resourcesModal.style.display = 'none');
    }
    if (resourceSearchBtn && resourceSearchInput) {
      resourceSearchBtn.addEventListener('click', () => loadResources(resourceSearchInput.value.trim()));
      resourceSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') loadResources(resourceSearchInput.value.trim());
      });
    }

    // Tier filter tabs
    document.querySelectorAll('.tier-tab-btn').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tier-tab-btn').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        filterVideoCards(tab.dataset.tier);
      });
    });
  }

  // Project Scanner Modal
  const projectScanBtn = document.getElementById('project-scan-btn');
  const projectModal = document.getElementById('project-modal');
  const closeProjectModalBtn = document.getElementById('close-project-modal-btn');
  const projectScanForm = document.getElementById('project-scan-form');

  if (projectScanBtn && projectModal) {
    projectScanBtn.addEventListener('click', () => {
      projectModal.style.display = 'flex';
    });
    if (closeProjectModalBtn) {
      closeProjectModalBtn.addEventListener('click', () => projectModal.style.display = 'none');
    }
    if (projectScanForm) {
      projectScanForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pPath = document.getElementById('input-project-path').value.trim();
        await scanProjectDirectory(pPath);
      });
    }
  }
}

// Load Study Dashboard
async function loadStudyDashboard() {
  try {
    const res = await fetch('/api/study/dashboard');
    if (!res.ok) return;
    const data = await res.json();

    const barsContainer = document.getElementById('skills-bars-container');
    barsContainer.innerHTML = `
      <div class="skill-bar-card">
        <div class="skill-bar-header"><span>Unreal Engine 5</span><span>${data.unreal_progress_pct}%</span></div>
        <div class="progress-track"><div class="progress-fill-glow" style="width: ${data.unreal_progress_pct}%;"></div></div>
      </div>
      <div class="skill-bar-card">
        <div class="skill-bar-header"><span>C++ Game Dev</span><span>${data.cpp_progress_pct}%</span></div>
        <div class="progress-track"><div class="progress-fill-glow" style="width: ${data.cpp_progress_pct}%;"></div></div>
      </div>
      <div class="skill-bar-card">
        <div class="skill-bar-header"><span>Blender 4.x Pipeline</span><span>${data.blender_progress_pct}%</span></div>
        <div class="progress-track"><div class="progress-fill-glow" style="width: ${data.blender_progress_pct}%;"></div></div>
      </div>
    `;

    const weakList = document.getElementById('weak-areas-list');
    weakList.innerHTML = data.weak_areas.map(w => `<span class="tag tag-warn"><i class="fa-solid fa-triangle-exclamation"></i> ${w}</span>`).join('');

    const completedList = document.getElementById('completed-topics-list');
    completedList.innerHTML = data.completed_topics.map(c => `<span class="tag tag-success"><i class="fa-solid fa-check"></i> ${c}</span>`).join('');
  } catch (err) {
    console.error('Failed to load study dashboard:', err);
  }
}

// Load Video Resources
let cachedVideoResources = null;
async function loadResources(topic = "") {
  const container = document.getElementById('video-cards-grid');
  container.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Finding curated learning resources...</div>';

  try {
    const res = await fetch('/api/resources/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic || "Niagara" })
    });
    if (!res.ok) throw new Error('Failed to fetch resources');
    const data = await res.json();
    cachedVideoResources = data.resources;
    renderVideoCards(cachedVideoResources, 'all');
  } catch (err) {
    container.innerHTML = `<p class="error-msg">⚠️ Error fetching video resources: ${err.message}</p>`;
  }
}

function renderVideoCards(resourcesByTier, tierFilter = 'all') {
  const container = document.getElementById('video-cards-grid');
  container.innerHTML = '';

  const tiers = tierFilter === 'all' ? ['Beginner', 'Intermediate', 'Advanced'] : [tierFilter];
  let totalCards = 0;

  tiers.forEach(tier => {
    const list = resourcesByTier[tier] || [];
    list.forEach(item => {
      totalCards++;
      const card = document.createElement('div');
      card.className = `video-card tier-${item.difficulty.toLowerCase()}`;
      card.innerHTML = `
        <div class="video-card-header">
          <span class="video-difficulty-badge ${item.difficulty.toLowerCase()}">${item.difficulty}</span>
          <span class="video-duration"><i class="fa-regular fa-clock"></i> ${item.duration || 'Video'}</span>
        </div>
        <h4 class="video-title">${item.title}</h4>
        <div class="video-creator"><i class="fa-solid fa-chalkboard-user"></i> ${item.creator}</div>
        <p class="video-why">${item.why_relevant}</p>
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary video-link-btn">
          <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Tutorial
        </a>
      `;
      container.appendChild(card);
    });
  });

  if (totalCards === 0) {
    container.innerHTML = '<p class="empty-notice">No videos found for this filter. Try searching for "Niagara", "Replication", or "Blender".</p>';
  }
}

function filterVideoCards(tier) {
  if (cachedVideoResources) {
    renderVideoCards(cachedVideoResources, tier);
  }
}

// Scan Project Directory
async function scanProjectDirectory(projectPath) {
  const resultsDiv = document.getElementById('project-scan-results');
  const metricsDiv = document.getElementById('scan-metrics');
  const classesList = document.getElementById('scanned-classes-list');

  resultsDiv.style.display = 'block';
  metricsDiv.innerHTML = '<div class="loading-spinner"><i class="fa-solid fa-circle-notch fa-spin"></i> Scanning project structure & C++ classes...</div>';
  classesList.innerHTML = '';

  try {
    const res = await fetch('/api/project/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_path: projectPath })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Scan failed');
    }

    const data = await res.json();
    const p = data.project;

    metricsDiv.innerHTML = `
      <div class="metric-box"><span class="metric-num">${p.project_name}</span><span class="metric-lbl">Project</span></div>
      <div class="metric-box"><span class="metric-num">${p.engine_version || 'UE 5.4'}</span><span class="metric-lbl">Engine</span></div>
      <div class="metric-box"><span class="metric-num">${p.classes.length}</span><span class="metric-lbl">C++ Classes</span></div>
      <div class="metric-box"><span class="metric-num">${p.total_files_indexed}</span><span class="metric-lbl">Source Files</span></div>
    `;

    if (p.classes.length > 0) {
      classesList.innerHTML = p.classes.map(c => `
        <div class="class-item">
          <span class="class-name"><i class="fa-solid fa-code"></i> ${c.name}</span>
          <span class="class-base">: public ${c.base_class || 'UObject'}</span>
          <span class="class-file">${c.file_path}</span>
        </div>
      `).join('');
    } else {
      classesList.innerHTML = '<p class="empty-notice">No C++ classes parsed yet in Source/ directory.</p>';
    }

    await fetchContext();
  } catch (err) {
    metricsDiv.innerHTML = `<div class="error-msg">⚠️ ${err.message}</div>`;
  }
}

