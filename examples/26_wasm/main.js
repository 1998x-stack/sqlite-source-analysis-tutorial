const button = document.querySelector('#run');
const status = document.querySelector('#status');
const output = document.querySelector('#output');
const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });

worker.addEventListener('message', (event) => {
  const message = event.data;
  if (message.type === 'success') {
    status.textContent = `完成：${message.mode} · SQLite ${message.version}`;
    output.textContent = JSON.stringify(message.rows, null, 2);
    button.disabled = false;
  } else {
    status.textContent = '执行失败';
    output.textContent = message.error;
    button.disabled = false;
  }
});

button.addEventListener('click', () => {
  button.disabled = true;
  status.textContent = 'Worker 正在初始化 SQLite…';
  worker.postMessage({ type: 'run' });
});

window.addEventListener('pagehide', () => worker.terminate(), { once: true });
