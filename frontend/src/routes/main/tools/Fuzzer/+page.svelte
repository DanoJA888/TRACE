<script>
  let wordlistInput = { id: "word_list", type: "file", accept: ".json, .txt", label: "Word List", value: "", example: "Ex: wordlist.txt", required: true };

  let fuzzerInput = [
    { id: "target_url", label: "Target URL", type: "text", value: "", example: "Ex: https://userinput.com/path?param=value  ->", required: true },
    { id: "http_method", label: "HTTP Method", type: "select", options: ["GET", "POST", "PUT"], value: "GET", required: true },
    { id: "cookies", label: "Cookies", type: "text", value: "", example: "name=value; name2=value2", required: false },
    { id: "hide_status", label: "Hide Status Code", type: "text", value: "", example: "404,500", required: false },
    { id: "show_status", label: "Show Status Code", type: "text", value: "", example: "200,301,302", required: false },
    { id: "filter_by_content_length", label: "Filter by Content Length", type: "text", value: "", example: "1234", required: false },
    { id: "proxy", label: "Proxy", type: "text", value: "", example: "http://proxy:port ->", required: false },
    { id: "additional_parameters", label: "Additional Parameters", type: "text", value: "", example: "param1=value1&param2=value2", required: false }
  ];

  let fuzzerParams = {
    target_url: "",
    word_list: "",
    show_results: true  // Initialize show_results option
  };

  let results = [];
  let acceptingParams = true;
  let isRunning = false;
  let displayingResults = false;
  let showResultsButton = false; // New state variable
  let selectedFileName = "No file selected"; // Track selected file name
  let fileUploaded = false; // Track if file was successfully uploaded

  // Track progress
  let progress = 0;
  let processedRequests = 0;
  let filteredRequests = 0;
  let requestsPerSecond = 0;
  let startTime = null;
  let elapsedTime = "0s";
  let timerInterval;
  let showTerminal = false;
  let terminalOutput = [];

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
    terminalOutput = [];
  }

  function dynamicFuzzerParamUpdate(id, value) {
    fuzzerParams[id] = value;
    console.log(`Updated ${id} to ${value}`);
  }

  function toggleTerminal() {
    showTerminal = !showTerminal;
  }

  // Function to handle file upload for wordlist
  async function handleFile(event) {
    console.log("File Submitted");
    
    // Get the selected file
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
    
    const formData = new FormData();// Create FormData to send the file
    formData.append('file', file);
    
    try {
      // Send the file to the server
      const response = await fetch('http://localhost:8000/upload-wordlist', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }
      
      const result = await response.json();
      console.log("File uploaded successfully:", result);
      
      // Update the fuzzerParams with the file path
      fuzzerParams.word_list = result.path;
      fileUploaded = true;
      
      // Update the UI to show successful upload
      const statusElement = document.querySelector('#file-status');
      if (statusElement) {
        statusElement.textContent = `File uploaded: ${file.name}`;
        statusElement.className = 'selected-file success';
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      fileUploaded = false;
      
      // Update the UI to show error
      const statusElement = document.querySelector('#file-status');
      if (statusElement) {
        statusElement.textContent = `Error uploading the file: ${error.message}`;
        statusElement.className = 'selected-file error';
      }
    }
  }

  function exportResults() {  // Export the results to file
    const dataStr = JSON.stringify(results, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    const exportFileDefaultName = 'fuzz_results.json';

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  }

  // inputs to be sent to the backend for computation
  async function handleSubmit() {
    // Validate form before proceeding
    if (!fuzzerParams.target_url) {
      alert('Target URL is required');
      return;
    }
    
    if (!fileUploaded && !fuzzerParams.word_list) {
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
    terminalOutput = [];

    try {
      const response = await fetch('http://localhost:8000/fuzzer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fuzzerParams),
      });

      if (!response.ok) {
        throw new Error(`Fuzzing request failed: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          showResultsButton = true; // Set the button to visible when done
          stopTimer();
          break;
        }

        // Process the chunked response data here 
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const update = JSON.parse(line);

            // Update progress and stats
            if (update.progress) {
              progress = update.progress * 100;
            }

            processedRequests = update.processed_requests || processedRequests;
            filteredRequests = update.filtered_requests || filteredRequests;
            requestsPerSecond = update.requests_per_second || requestsPerSecond;

            if (update.payload) {
              // Add to terminal output
              terminalOutput = [...terminalOutput,
                `Request ${update.id}: ${update.payload} -> ${update.response}`];

              // Add result to table
              results = [...results, update];
            }
          } catch (error) {
            console.error('Error parsing update:', error);
          }
        }
      }
    } catch (error) {
      console.error('Error during fuzzing:', error);
      // Add to terminal output for visibility
      terminalOutput = [...terminalOutput, `ERROR: ${error.message}`];
      showResultsButton = true; // Show button even on error
      stopTimer();
    }
  }

  function pauseFuzz() {
    //will need some work here server?
    console.log('Pause requested');
  }

  function stopFuzz() {
    showResultsButton = true; // Show button when stopped
    stopTimer();
  }

  function restartFuzz() {
    results = [];
    terminalOutput = [];
    handleSubmit();
  }

  function goBack() {
    window.location.href = "/main/tools";
  }
</script>

<div class="fuzzerConfigPage">
  <div>
    <h1>Parameter Fuzzing</h1>
    <button on:click={goBack} class="back-button">Back to Tools</button>

    {#if acceptingParams}
      <div>
        <form on:submit="{(e) => {e.preventDefault(); handleSubmit()}}">
          <div class="file-input-container">
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

          {#each fuzzerInput as param}
            {#if param.type === "select"}
              <div class="input-container">
                <label for={param.id}>{param.label}:</label>
                <select
                  id={param.id}
                  bind:value={fuzzerParams[param.id]}
                  required={param.required}
                  on:change={(e) => dynamicFuzzerParamUpdate(param.id, e.target.value)}
                >
                  {#each param.options as option}
                    <option value={option}>{option}</option>
                  {/each}
                </select>
              </div>
            {:else}
              <div class="input-container">
                <label for={param.id}>{param.label}:</label>
                <input
                  id={param.id}
                  type={param.type}
                  bind:value={fuzzerParams[param.id]}
                  placeholder={param.example}
                  required={param.required}
                  on:input={(e) => dynamicFuzzerParamUpdate(param.id, e.target.value)}
                />
              </div>
            {/if}
          {/each}

          <button type="submit" class="submit-button">Start Fuzzing</button>
        </form>
      </div>
    {/if}

    {#if isRunning}
      <div>
        <h2>Running...</h2>
        <div class="progress-bar">
          <div
            class="progress"
            style="width: {progress}%"
          ></div>
        </div>
        <p>{progress.toFixed(0)}% Complete</p>
        <div class="metrics-container">
          <div class="metric">
            <span class="metric-label">Running Time</span>
            <span class="metric-value">{elapsedTime}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Processed Requests</span>
            <span class="metric-value">{processedRequests}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Filtered Requests</span>
            <span class="metric-value">{filteredRequests}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Requests/sec</span>
            <span class="metric-value">{requestsPerSecond}</span>
          </div>
        </div>

        {#if showTerminal}
          <div class="terminal">
            <div class="terminal-header">
              <span>Terminal Output</span>
              <button class="close-terminal" on:click={toggleTerminal}>×</button>
            </div>
            <div class="terminal-content">
              {#each terminalOutput as line}
                <div class="terminal-line">{line}</div>
              {/each}
            </div>
          </div>
        {/if}

        {#if fuzzerParams.show_results}
          <div class="results-table">
            {#if results.length === 0}
              <p>No data has been received. Please wait...</p>
            {/if}
            {#if results.length > 0}
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Response</th>
                    <th>Lines</th>
                    <th>Words</th>
                    <th>Chars</th>
                    <th>Payload</th>
                    <th>Length</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {#each results as result (result.id)}
                    <tr>
                      <td>{result.id}</td>
                      <td class={result.response >= 400 ? 'error' : (result.response >= 300 ? 'warning' : 'success')}>
                        {result.response}
                      </td>
                      <td>{result.lines}</td>
                      <td>{result.words}</td>
                      <td>{result.chars}</td>
                      <td>{result.payload}</td>
                      <td>{result.length}</td>
                      <td>{result.error ? 'Yes' : 'No'}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            {/if}
          </div>
        {:else}
          <div class="results-placeholder">
            <p>Results will be displayed when the scan completes</p>
          </div>
        {/if}

        <div class="action-buttons">
          <button class="pause-button" on:click={pauseFuzz}>Pause</button>
          <button class="restart-button" on:click={restartFuzz}>Restart</button>
          <button class="stop-button" on:click={stopFuzz}>Stop</button>
          <button class="terminal-button" on:click={toggleTerminal}>
            {showTerminal ? 'Close Terminal' : 'Show Terminal'}
          </button>
          <button class="export-button" on:click={exportResults}>Export</button>
          {#if showResultsButton}
            <button on:click={runningToResults} class="go-to-results-button">Go to Fuzzing Results</button>
          {/if}
        </div>
      </div>
    {/if}

    {#if displayingResults}
      <h2>Fuzzing Results</h2>
      <div class="results-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Response</th>
              <th>Lines</th>
              <th>Words</th>
              <th>Chars</th>
              <th>Payload</th>
              <th>Length</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {#each results as result (result.id)}
              <tr>
                <td>{result.id}</td>
                <td class={result.response >= 400 ? 'error' : (result.response >= 300 ? 'warning' : 'success')}>
                  {result.response}
                </td>
                <td>{result.lines}</td>
                <td>{result.words}</td>
                <td>{result.chars}</td>
                <td>{result.payload}</td>
                <td>{result.length}</td>
                <td>{result.error ? 'Yes' : 'No'}</td>
              </tr>
            {/each}
          </tbody>
        </table>
        <div class="action-buttons">
          <button on:click={resultsToParams} class="back-button">Back to Param Setup</button>
          <button class="export-button" on:click={exportResults}>Export Results</button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .fuzzerConfigPage {
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
  }

  .back-button {
    margin-bottom: 20px;
    padding: 8px 15px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    color: #333; /* Changed font color */
  }

  form {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
    width: 400px;
    margin: 50px auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .input-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .file-input-container {
    display: flex;
    flex-direction: column;
    gap: 5px;
    margin-bottom: 10px;
  }

  label {
    font-weight: bold;
  }

  .selected-file {
    font-size: 0.9em;
    margin-top: 5px;
  }

  .success {
    color: #4CAF50;
  }

  .error {
    color: #F44336;
  }

  .warning {
    color: #FF9800;
  }

  /* Styles for checkbox group */
  .checkbox-group label {
    flex-direction: row;
    align-items: center;
    gap: 10px;
  }

  .checkbox-group input[type="checkbox"] {
    width: auto;
    margin: 0;
  }

  .help-text {
    font-size: 0.8em;
    color: #666;
    margin-top: 5px;
  }

  .results-placeholder {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 4px;
    text-align: center;
    margin: 20px 0;
    border: 1px dashed #ccc;
  }

  input, textarea, select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  textarea {
    height: 100px;
    resize: vertical;
  }

  .submit-button {
    background-color: #76c7c0;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 15px;
    align-self: center;
  }

  .progress-bar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
  }

  .progress {
    height: 20px;
    background-color: #5bbfb2;
    transition: width 0.3s ease;
  }

  .metrics-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
  }

  .metric {
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #ddd;
  }

  .metric-label {
    display: block;
    font-weight: bold;
    margin-bottom: 5px;
    color: #666;
  }

  .metric-value {
    font-size: 1.2em;
    color: #333;
  }

  .terminal {
    background-color: #1E1E1E;
    color: #FFFFFF;
    border-radius: 5px;
    margin: 20px 0;
    max-height: 300px;
    overflow-y: auto;
  }

  .terminal-header {
    background-color: #333;
    padding: 8px 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
  }

  .close-terminal {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
  }

  .terminal-content {
    padding: 10px;
  }

  .terminal-line {
    font-family: monospace;
    margin-bottom: 3px;
    word-break: break-all;
  }

  .results-table {
    margin: 20px 0;
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f2f2f2;
    position: sticky;
    top: 0;
  }

  .action-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 20px 0;
  }

  .action-buttons button {
    padding: 8px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .pause-button {
    background-color: #5bbfb2;
    color: white;
  }

  .restart-button {
    background-color: #5bbfb2;
    color: white;
  }

  .stop-button {
    background-color: #5bbfb2;
    color: white;
  }

  .terminal-button {
    background-color: #5bbfb2;
    color: white;
  }

  .export-button {
    background-color: #4CAF50;
    color: white;
  }

  .go-to-results-button {
    background-color: #5bbfb2;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 10px;
  }
</style>