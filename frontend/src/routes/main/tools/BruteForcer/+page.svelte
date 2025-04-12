<script>
  import { preventDefault } from "svelte/legacy";
  let wordlistInput = { id: "word_list", type: "file", accept: ".json, .txt", label: "Word List", value: "", example: "Ex: wordlist.txt", required: true };

  let bruteForceInput = [
    { id: "target_url", label: "Target URL", type: "text", value: "", example: "Ex: https://example.com/path", required: true },
    { id: "top_level_directory", label: "Top Level Directory", type: "text", value: "", example: "/", required: true },
    { id: "hide_status_code", label: "Hide Status Code", type: "text", value: "", example: "403, 500", required: false },
    { id: "show_status_code", label: "Show Only Status Code", type: "text", value: "", example: "200, 500", required: false },
    { id: "filter_by_content_length", label: "Filter by Content Length", type: "number", value: "", example: ">100, <500", required: false },
    { id: "additional_param", label: "Additional Parameter", type: "text", value: "", example: "Ex: some_param=value", required: false }
  ];

  let bruteForceParams = {
    target_url: "",
    word_list: "",
    show_results: true  // Initialize show_results option
  };

  let results = [];
  let acceptingParams = true;
  let isRunning = false;
  let displayingResults = false;
  let showResultsButton = false;
  let selectedFileName = "No file selected"; // Track selected file name
  let fileUploaded = false; // Track if file was successfully uploaded
  let showTerminal = false;
  let logOutput = '';
  let visibleResults=[];

  // Track progress
  let progress = 0;
  let processedRequests = 0;
  let filteredRequests = 0;
  let requestsPerSecond = 0;
  let startTime = null;
  let elapsedTime = "0s";
  let timerInterval;

  function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(() => {
      const seconds = Math.floor((Date.now() - startTime) / 1000);
      elapsedTime = `${seconds}s`;
    }, 1000);
  }

  function stopTimer() {
    clearInterval(timerInterval);
  }

  function paramsToRunning() {
    acceptingParams = false;
    isRunning = true;
    showResultsButton = false; // Reset button 
  }

  function runningToResults() {
    isRunning = false;
    displayingResults = true;
    showResultsButton = false; // Hide button after navigating
  }

  function resultsToParams() {
    displayingResults = false;
    acceptingParams = true;
    results = [];
  }

  function dynamicBruteForceParamUpdate(id, value) {
    bruteForceParams[id] = value;
    console.log(`Updated ${id} to ${value}`);
  }

  function pauseBruteForce() {
    console.log("Paused (backend control not implemented yet)");
  }

  function stopBruteForce() {
    if (activeController) activeController.abort();
    stopTimer();
    isRunning = false;
    showResultsButton = true;
  }

  function restartBruteForce() {
    results = [];
    stopTimer();
    handleSubmit();
  }

  // Function to handle file upload for wordlist
  async function handleFile(event) {
    console.log("File Submitted");
    
    const fileInput = event.target;
    if (!fileInput.files || fileInput.files.length === 0) {
      console.log("No file selected");
      selectedFileName = "No file selected";
      fileUploaded = false;
      return;
    }
    
    const file = fileInput.files[0];
    selectedFileName = file.name;
    console.log("Selected file:", file.name);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch('http://localhost:8000/upload-wordlist', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }
      
      const result = await response.json();
      console.log("File uploaded successfully:", result);
      
      bruteForceParams.word_list = result.path;
      fileUploaded = true;
      
      const statusElement = document.querySelector('#file-status');
      if (statusElement) {
        statusElement.textContent = `File uploaded: ${file.name}`;
        statusElement.className = 'selected-file success';
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      fileUploaded = false;
      
      const statusElement = document.querySelector('#file-status');
      if (statusElement) {
        statusElement.textContent = `Error uploading the file: ${error.message}`;
        statusElement.className = 'selected-file error';
      }
    }
  }

  // inputs to be sent to the backend for brute-forcing
  async function handleSubmit() {
    if (!bruteForceParams.target_url) {
      alert('Target URL is required');
      return;
    }
    
    if (!fileUploaded && !bruteForceParams.word_list) {
      alert('Please upload a wordlist file first');
      return;
    }
    
    paramsToRunning();
    startTimer();
    progress = 0;
    processedRequests = 0;
    filteredRequests = 0;
    requestsPerSecond = 0;
    results = [];

    try {
      const response = await fetch('http://localhost:8000/bruteforcer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bruteForceParams),
      });

      if (!response.ok) {
        throw new Error(`Brute force request failed: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
        showResultsButton = true;
        stopTimer();
        runningToResults(); // << This line was missing
        break;
        }

        const chunk = decoder.decode(value);
        logOutput += chunk + '\n';
        const lines = chunk.split('\n').filter(line => line.trim());
        
        
        for (const line of lines) {
          try {
            const update = JSON.parse(line);
            console.log('Received update:', update); //debugging missing table entries
            if (update.progress) {
              progress = update.progress * 100;
            }
            processedRequests = update.processed_requests || processedRequests;
            filteredRequests = update.filtered_requests || filteredRequests;
            requestsPerSecond = update.requests_per_second || requestsPerSecond;

            if (update.payload) {
              results = [...results, update];
              const statusCode = update.response;
              const hideList = bruteForceParams.hide_status_code?.split(',').map(code => code.trim());
              const showList = bruteForceParams.show_status_code?.split(',').map(code => code.trim());

              let shouldShow = true;

              if (showList?.length && showList[0] !== '') {
                shouldShow = showList.includes(statusCode.toString());
              } else if (hideList?.length && hideList[0] !== '') {
                shouldShow = !hideList.includes(statusCode.toString());
              }

              if (shouldShow) {
                visibleResults = [...visibleResults, update];
              }
            }
          } catch (error) {
            console.error('Error parsing update:', error);
          }
        }
      }
    } catch (error) {
      console.error('Error during brute force:', error);
      showResultsButton = true;
      stopTimer();
    }
  }

  function exportResults() { 
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = 'bruteforce_results.json';

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }
</script>

<div class="bruteForceConfigPage">
  <div>
    <h1>Brute Force Configuration</h1>

    {#if acceptingParams}
      <div>
        <form on:submit="{(e) => {e.preventDefault(); handleSubmit()}}">
          {#each bruteForceInput as param}
            {#if param.type === 'file'}
              <div>
                <label for={param.id}><span>{param.label}</span></label>
                <input
                  id={param.id}
                  accept={param.accept}
                  type={param.type}
                  required={param.required}
                  on:change={handleFile}
                />
                <div id="file-status" class="selected-file">{selectedFileName}</div>
              </div>
            {:else}
              <div>
                <label for={param.id}>{param.label}:</label>
                <input
                  id={param.id}
                  type={param.type}
                  bind:value={bruteForceParams[param.id]}
                  placeholder={param.example}
                  required={param.required}
                  on:input={(e) => dynamicBruteForceParamUpdate(param.id, e.target.value)}
                />
              </div>
            {/if}
          {/each}

          <div>
            <label for="word_list">{wordlistInput.label}</label>
            <input
              id="word_list"
              accept={wordlistInput.accept}
              type="file"
              placeholder="No file selected."
              required={wordlistInput.required}
              on:change={handleFile}
            />
            <div id="file-status" class="selected-file">{selectedFileName}</div>
          </div>

          <button type="submit" class="submit-button">Start Brute Force</button>
        </form>
      </div>
    {/if}

    {#if isRunning}
      <div class="brute-section">
        <h2>Running...</h2>
        <div class="progress-bar">
          <div class="progress" style="width: {progress}%"></div>
        </div>
        <div class="metrics">
          <div class="metric-item"><strong>Processed</strong><span>{processedRequests}</span></div>
          <div class="metric-item"><strong>Filtered</strong><span>{filteredRequests}</span></div>
          <div class="metric-item"><strong>Requests/sec</strong><span>{requestsPerSecond}</span></div>
          <div class="metric-item"><strong>Elapsed Time</strong><span>{elapsedTime}</span></div>
        </div>
        <div class="results-table-scrollable">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Status</th><th>Lines</th><th>Words</th><th>Chars</th><th>Payload</th><th>Length</th>
              </tr>
            </thead>
            <tbody>
              {#each visibleResults as result, index}
                <tr>
                  <td>{index + 1}</td>
                  <td>{result.response}</td>
                  <td>{result.lines}</td>
                  <td>{result.words}</td>
                  <td>{result.chars}</td>
                  <td>{result.payload}</td>
                  <td>{result.length}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}

    {#if displayingResults}
      <div class="brute-section">
        <h2>Brute Force Results</h2>
        <div class="metrics">
          <div class="metric-item"><strong>Running Time:</strong><span>{elapsedTime}</span></div>
          <div class="metric-item"><strong>Processed Requests:</strong><span>{processedRequests}</span></div>
          <div class="metric-item"><strong>Filtered Requests:</strong><span>{filteredRequests}</span></div>
          <div class="metric-item"><strong>Requests/sec:</strong><span>{requestsPerSecond}</span></div>
        </div>
        <div class="results-table-scrollable">
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Status</th><th>Lines</th><th>Words</th><th>Chars</th><th>Payload</th><th>Length</th>
              </tr>
            </thead>
            <tbody>
              {#each results as result, index}
                <tr>
                  <td>{index + 1}</td>
                  <td>{result.response}</td>
                  <td>{result.lines}</td>
                  <td>{result.words}</td>
                  <td>{result.chars}</td>
                  <td>{result.payload}</td>
                  <td>{result.length}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}

    <!-- ✅ These are always visible when done -->
    {#if isRunning || displayingResults}
      <div class="action-buttons-bottom">
        <button on:click={pauseBruteForce}>Pause</button>
        <button on:click={stopBruteForce}>Stop</button>
        <button on:click={restartBruteForce}>Restart</button>
        <button on:click={() => showTerminal = true}>View Terminal</button>
        <button on:click={() => resultsToParams()}>Back to Param Setup</button>
        {#if showResultsButton}
          <button on:click={exportResults}>Export Results</button>
        {/if}
      </div>
    {/if}

    <!-- Optional fallback -->
    {#if !acceptingParams && !isRunning && !displayingResults}
      <p style="color: red; text-align: center; margin-top: 2rem;">⚠️ Nothing is being displayed. Check state logic.</p>
    {/if}
  </div>
</div>

{#if showTerminal}
  <div class="terminal-overlay">
    <div class="terminal-window">
      <div class="terminal-header">
        <span>Terminal Output</span>
        <button on:click={() => showTerminal = false}>✖</button>
      </div>
      <div class="terminal-content">
        <!-- Hook up streamed logs here -->
        <pre>{logOutput}</pre>
      </div>
    </div>
  </div>
{/if}

<style>
  .progress-bar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
  }

  .progress {
    height: 20px;
    background-color: #646cff;
    transition: width 0.3s ease;
  }

  .results-table {
    margin-top: 20px; 
  }

  .results-table button {
    margin-top: 20px; 
  }

  .brute-section {
    background-color: #1f1f1f;
    padding: 1.5rem;
    border-radius: 1rem;
    margin-top: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }

  .bruteForceConfigPage {
  width: 80%;  /* Adjusted width to give more space */
  margin: 10vh auto; /* Centered with some spacing from the top */
  padding: 20px;
  background: transparent;
  border-radius: 8px;
  /* box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); */
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #f5f5f5; /* Set text color to dark gray for better contrast */
}

.results-table-scrollable {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 10px;
  margin-top: 1rem;
}

.action-buttons-bottom {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}

.action-buttons-bottom button {
  background-color: #646cff;
  color: white;
  padding: 0.75rem 1.5rem;
  font-weight: bold;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.action-buttons-bottom button:hover {
  background-color: #4e56d3;
}

.terminal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.terminal-window {
  background: #111;
  color: #0f0;
  width: 80%;
  max-height: 70vh;
  border-radius: 8px;
  overflow-y: auto;
  padding: 1rem;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.terminal-content {
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-word;
}
  
</style>
