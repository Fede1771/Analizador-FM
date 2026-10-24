export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

export async function api(path, {method = 'GET', body, signal, timeout = 120000} = {}) {
  const controller = new AbortController();
  const cancel = () => controller.abort(signal?.reason);
  if (signal?.aborted) cancel();
  else signal?.addEventListener('abort', cancel, {once: true});
  const timer = setTimeout(() => controller.abort(new Error('La operación tardó demasiado. Reintentá.')), timeout);
  try {
    const response = await fetch(path, {method, signal: controller.signal,
      headers: body === undefined ? {} : {'Content-Type': 'application/json', 'X-FM-App': '1'},
      body: body === undefined ? undefined : JSON.stringify(body)});
    const data = await response.json();
    if (!response.ok) throw new ApiError(data.error || 'No se pudo completar la operación.', response.status);
    return data;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancel);
  }
}

export function upload(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('PUT', '/api/import');
    xhr.timeout = 120000;
    xhr.setRequestHeader('X-FM-App', '1');
    xhr.setRequestHeader('X-FM-Filename', encodeURIComponent(file.name));
    xhr.upload.onprogress = event => { if (event.lengthComputable) onProgress(Math.round(event.loaded/event.total*15)); };
    xhr.onload = () => {
      try { const value = JSON.parse(xhr.responseText); xhr.status === 202 ? resolve(value) : reject(new ApiError(value.error, xhr.status)); }
      catch (error) { reject(error); }
    };
    xhr.onerror = () => reject(new Error('Se perdió la conexión con Touchline.'));
    xhr.ontimeout = () => reject(new Error('La carga tardó demasiado. Reintentá.'));
    xhr.send(file);
  });
}

// A shared gate prevents both out-of-order results and responses from an old dataset.
export class RequestGate {
  version = 0;
  controller = null;
  begin(datasetId) {
    this.controller?.abort();
    this.controller = new AbortController();
    const version = ++this.version;
    return {signal: this.controller.signal, current: id => version === this.version && id === datasetId};
  }
  invalidate() { ++this.version; this.controller?.abort(); }
}
