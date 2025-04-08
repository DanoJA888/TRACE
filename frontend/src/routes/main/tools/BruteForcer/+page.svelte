<script>
    import { preventDefault } from "svelte/legacy";
  
    let bruteForceInput = [
      { id: "url", label: "Target URL", type: "text", value: "", example: "Ex: https://example.com", required: true },
      { id: "wordlist", label: "Word List", type: "file", value: "", required: true },
      { id: "top_level_directory", label: "Top Level Directory", type: "text", value: "", example: "/dir/", required: true },
      { id: "hide_status_code", label: "Hide Status Code", type: "text", value: "", example: "404,500", required: false },
      { id: "show_status_code", label: "Show Only Status Code", type: "text", value: "", example: "200,301", required: false },
      { id: "filter_by_content_length", label: "Filter by Content Length", type: "number", value: "", example: "1000", required: false },
      { id: "additional_param", label: "Additional Parameter", type: "text", value: "", example: "Ex: some_param=value", required: false }
    ];
  
    let bruteForceParams = {
      url: "",
      wordlist: "",
      top_level_directory: "",
      hide_status_code: "",
      show_status_code: "",
      filter_by_content_length: "",
      additional_param: ""
    };
  
    let bruteForceResult = []; // Updated dynamically during brute forcing
  
    let acceptingParams = true;
    let bruteForcing = false;
    let displayingResults = false;
  
    let totalRequests = 0;
    let completedRequests = 0;
  
    let startTime = null;
    let elapsedTime = "0s";
    let timerInterval;
  
    let processedRequests = 0;
    let filteredRequests = 0;
    let requestsPerSecond = 0;
    let activeController = null;
  
    let errorMessages = {
      url: "",
      wordlist: "",
      top_level_directory: "",
      hide_status_code: "",
      show_status_code: "",
      filter_by_content_length: "",
      additional_param: "",
    };
  
    let sortConfig = {
      column: "",
      direction: 'asc'
    };
  
    // Start timer function
    function startTimer() {
      startTime = Date.now();
      timerInterval = setInterval(() => {
        const seconds = Math.floor((Date.now() - startTime) / 1000);
        elapsedTime = `${seconds}s`;
      }, 1000);
    }
  
    function stopTimer() {
      clearInterval(timerInterval);
      elapsedTime = "0s";
    }
  
    function paramsToBruteForcing() {
      acceptingParams = false;
      bruteForcing = true;
    }
  
    function bruteForcingToResults() {
      bruteForcing = false;
      displayingResults = true;
    }
  
    function resultsToParams() {
      displayingResults = false;
      acceptingParams = true;
      bruteForceResult = [];
    }
  
    // Dynamically update brute force parameters
    function dynamicBruteForceParamUpdate(id, value) {
      bruteForceParams[id] = value;
    }
  
    async function stopBruteForce() {
      if (activeController) {
        activeController.abort();
      }
      const response = await fetch('http://localhost:8000/stop_bruteforce', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (response.ok) {
        console.log("Stopped successfully");
      } else {
        console.error("Error stopping brute force:", response.statusText);
      }
    }
  
    // Validate input parameters before starting brute force
    function validateParams() {
      let isValid = true;
  
      // Reset error messages
      Object.keys(errorMessages).forEach(key => {
        errorMessages[key] = "";
      });
  
      if (!bruteForceParams.url) {
        errorMessages.url = "URL is required!";
        isValid = false;
      }
  
      if (!bruteForceParams.wordlist) {
        errorMessages.wordlist = "Word list is required!";
        isValid = false;
      }
  
      if (!bruteForceParams.top_level_directory) {
        errorMessages.top_level_directory = "Top Level Directory is required!";
        isValid = false;
      }
  
      return isValid;
    }
  
    // This is for inputs to be sent to the backend for brute forcing.
    async function handleSubmit() {
      // Validate the input before proceeding
      if (!validateParams()) {
        return; // Do not proceed if validation fails
      }
  
      paramsToBruteForcing();
      startTimer();
      completedRequests = 0;
      totalRequests = 0;  // Reset for brute force requests
  
      activeController = new AbortController();
  
      const response = await fetch('http://localhost:8000/bruteforce', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bruteForceParams),
        signal: activeController.signal
      });
  
      if (response.ok) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
  
        while (!done) {
          try {
            if (activeController.signal.aborted) {
              break;
            }
            const { value, done: readerDone } = await reader.read();
            done = readerDone;
            if (value) {
              const chunk = decoder.decode(value, { stream: true });
              const updates = chunk.split('\n').filter(Boolean).map(JSON.parse);
              bruteForceResult = [...bruteForceResult, ...updates];
              completedRequests += updates.length; // Update progress
  
              processedRequests += updates.length;
              filteredRequests = bruteForceResult.filter((item) => !item.error).length;
              requestsPerSecond = (processedRequests / ((Date.now() - startTime) / 1000)).toFixed(2);
            }
          } catch (err) {
            if (err.name === 'AbortError') {
              done = true;
              console.log("real-time results stopped to end brute force");
            }
            else {
              console.error('Error: ', err);
            }
          }
        }
  
        bruteForcingToResults();
      } else {
        console.error("Error starting brute force:", response.statusText);
      }
      stopTimer();
    }
  
    // Sorting function
    function sortTable(column) {
      const { direction } = sortConfig;
  
      // Toggle sorting direction
      sortConfig.direction = direction === 'asc' ? 'desc' : 'asc';
      sortConfig.column = column;
  
      console.log(`Sorting by column: ${column}, direction: ${sortConfig.direction}`);
  
      bruteForceResult = [...bruteForceResult].sort((a, b) => {
          const aValue = a[column];
          const bValue = b[column];
  
          // Ensure we are working with numbers where appropriate
          const aValueParsed = typeof aValue === 'number' ? aValue : parseFloat(aValue);
          const bValueParsed = typeof bValue === 'number' ? bValue : parseFloat(bValue);
  
          console.log(`Comparing ${a[column]} with ${b[column]}`);
  
          if (aValueParsed < bValueParsed) {
              return sortConfig.direction === 'asc' ? -1 : 1;
          } else if (aValueParsed > bValueParsed) {
              return sortConfig.direction === 'asc' ? 1 : -1;
          }
          return 0;
      });
      console.log("Sorted Result: ", bruteForceResult);
  }
  </script>
  
  <div class="bruteForceConfigPage">
    <div>
      <h1>Brute Force</h1>
  
      {#if acceptingParams}
      <div>
        <form onsubmit="{(e) => {e.preventDefault(); handleSubmit()}}">
          {#each bruteForceInput as param}
          <label>
            <span>{param.label}:</span>
            <input
              type={param.type}
              bind:value={bruteForceParams[param.id]}
              placeholder={param.example}
              required={param.required}
              oninput={(e) => dynamicBruteForceParamUpdate(param.id, e.target.value)}
            />
            {#if errorMessages[param.id]}
            <p class="error">{errorMessages[param.id]}</p>
            {/if}
          </label>
          {/each}
  
          <button type="submit">Submit</button>
        </form>
      </div>
      {/if}
  
      {#if bruteForcing}
      <div class="bruteForce-section">
        <div>
          <h2>Running...</h2>
          <div class="progress-bar">
            <div
              class="progress"
              style="width: {totalRequests > 0 ? (completedRequests / totalRequests) * 100 : 0}%"
            ></div>
          </div>
          <p>{completedRequests} / {totalRequests || "∞"} requests completed</p>
          <div class="metrics">
            <div class="metric-item">
              <strong>Running Time:</strong>
              <span>{elapsedTime}</span>
            </div>
            <div class="metric-item">
              <strong>Processed Requests:</strong>
              <span>{processedRequests}</span>
            </div>
            <div class="metric-item">
              <strong>Filtered Requests:</strong>
              <span>{filteredRequests}</span>
            </div>
            <div class="metric-item">
              <strong>Requests/sec:</strong>
              <span>{requestsPerSecond}</span>
            </div>
          </div>
          <div class="results-table">
            {#if bruteForceResult.length > 0}
            <table>
              <thead>
                <tr>
                  <th>
                    <button type="button" onclick={() => sortTable("url")}>URL</button>
                  </th>
                  <th>
                    <button type="button" onclick={() => sortTable("status_code")}>Status Code</button>
                  </th>
                  <th>
                    <button type="button" onclick={() => sortTable("content_length")}>Content Length</button>
                  </th>
                </tr>
              </thead>
              <tbody>
                {#each bruteForceResult as result (result.url)}
                <tr>
                  <td>{result.url}</td>
                  <td>{result.status_code}</td>
                  <td>{result.content_length}</td>
                </tr>
                {/each}
              </tbody>
            </table>
            {/if}
          </div>
        </div>
      </div>
      {/if}
  
      {#if displayingResults}
      <div>
        <h2>Results</h2>
        <button onclick={resultsToParams}>Go Back to Parameters</button>
      </div>
      {/if}
    </div>
  </div>


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

  .error {
    color: red;
    font-size: 0.8rem;
  }
</style>