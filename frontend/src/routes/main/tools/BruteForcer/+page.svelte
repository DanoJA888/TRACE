<script>
    import { preventDefault } from "svelte/legacy";
  
    let bruteForceInput = [
      { id: "target_url", label: "Target URL", type: "text", value: "", example: "Ex: https://example.com", required: true },
      { id: "wordlist", label: "Word List", type: "file", value: "", required: true },
      { id: "top_level_directory", label: "Top Level Directory", type: "text", value: "", example: "/", required: true },
      { id: "hide_status", label: "Hide Status Code", type: "text", value: "", example: "403", required: false },
      { id: "show_status", label: "Show Only Status Code", type: "text", value: "", example: "200", required: false },
      { id: "filter_by_content_length", label: "Filter by Content Length", type: "number", value: "", example: "100", required: false },
      { id: "additional_parameters", label: "Additional Parameter", type: "text", value: "", example: "param=value", required: false }
    ];

    let bruteForceParams = {
      target_url: "",
      wordlist: "",
      top_level_directory: "",
      hide_status: "",
      show_status: "",
      filter_by_content_length: "",
      additional_parameters: "",
      proxy: "",
      show_results: true
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
      const response = await fetch('http://localhost:8000/stop_bruteforcer', {
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
  
      if (!bruteForceParams.target_url) {
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
    async function handleSubmit(event) {
      const file = bruteForceParams["wordlist"];
      if (!file || !(file instanceof File)) {
        errorMessages.wordlist = "Please select a valid wordlist file.";
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      try {
        const uploadRes = await fetch("http://localhost:8000/upload-wordlist", {
          method: "POST",
          body: formData
        });

        const uploadData = await uploadRes.json();
        if (uploadData.path) {
          // Replace File object with just filename before sending to backend
          bruteForceParams.wordlist = uploadData.path.split("/").pop();
        } else {
          errorMessages.wordlist = "Wordlist upload failed.";
          return;
        }
      } catch (e) {
        errorMessages.wordlist = "Error uploading wordlist.";
        console.error("Upload failed:", e);
        return;
      }

      if (!validateParams()) {
        return; // Do not proceed if validation fails
      }

      paramsToBruteForcing();
      startTimer();
      completedRequests = 0;
      totalRequests = 0;

      activeController = new AbortController();

      const response = await fetch('http://localhost:8000/bruteforcer', {
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
              completedRequests += updates.length;

              processedRequests += updates.length;
              filteredRequests = bruteForceResult.filter((item) => !item.error).length;
              requestsPerSecond = (processedRequests / ((Date.now() - startTime) / 1000)).toFixed(2);
            }
          } catch (err) {
            if (err.name === 'AbortError') {
              done = true;
              console.log("real-time results stopped to end brute force");
            } else {
              console.error('Error: ', err);
            }
          }
        }
        bruteForcingToResults();
      } else {
        const errorDetails = {
          status: response.status,
          statusText: response.statusText,
          responseBody: await response.text(),
          payload: bruteForceParams
        };

        console.error("Error starting brute force:", response.statusText);
        bruteForceResult.push(errorDetails);
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
          <form onsubmit={preventDefault(handleSubmit)}>
            {#each bruteForceInput as param}
              <label>
                <span>{param.label}:</span>

                {#if param.type === "file"}
                  <input
                    type="file"
                    accept=".txt"
                    required={param.required}
                    onchange={(e) => bruteForceParams[param.id] = e.target.files[0]}
                  />
                {:else}
                  <input
                    type={param.type}
                    value={bruteForceParams[param.id]}
                    placeholder={param.example}
                    required={param.required}
                    oninput={(e) => bruteForceParams[param.id] = e.target.value}
                  />
                {/if}

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
          <h2>Running...</h2>
          <div class="progress-bar">
            <div
              class="progress"
              style="width: {(completedRequests / Math.max(bruteForceResult.length, 1)) * 100}%"
            ></div>
          </div>
          <p>{completedRequests} / {bruteForceResult.length || "?"} requests completed</p>

          <div class="metrics">
            <div class="metric-item"><strong>Running Time:</strong> <span>{elapsedTime}</span></div>
            <div class="metric-item"><strong>Processed Requests:</strong> <span>{processedRequests}</span></div>
            <div class="metric-item"><strong>Filtered Requests:</strong> <span>{filteredRequests}</span></div>
            <div class="metric-item"><strong>Requests/sec:</strong> <span>{requestsPerSecond}</span></div>
          </div>
        </div>
      {/if}

      {#if bruteForceResult.length > 0}
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
              </tr>
            </thead>
            <tbody>
              {#each bruteForceResult as result, index (result.id || index)}
                <tr>
                  <td>{index + 1}</td>
                  <td>{result.response}</td>
                  <td>{result.lines}</td>
                  <td>{result.words}</td>
                  <td>{result.chars}</td>
                  <td>{result.payload}</td>
                  <td>{parseFloat(result.length).toFixed(2)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else if bruteForcing}
        <p>Waiting for results...</p>
      {/if}
  
      {#if displayingResults}
      <div class="bruteforce-section">
        <h2> Brute Force Results</h2>
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
          <table>
            <thead>
              <tr>
                <th onclick={() => sortTable('id')}>
                  ID
                  {#if sortConfig.column === 'id'}
                    {sortConfig.direction === 'asc' ? '▲' : '▼'}
                  {/if}
                </th>
                <th onclick={() => sortTable('response')}>
                  Response
                  {#if sortConfig.column === 'response'}
                    {sortConfig.direction === 'asc' ? '▲' : '▼'}
                  {/if}
                </th>
                <th onclick={() => sortTable('lines')}>
                  Lines
                  {#if sortConfig.column === 'lines'}
                    {sortConfig.direction === 'asc' ? '▲' : '▼'}
                  {/if}
                </th>
                <th onclick={() => sortTable('words')}>
                  Word
                  {#if sortConfig.column === 'words'}
                    {sortConfig.direction === 'asc' ? '▲' : '▼'}
                  {/if}
                </th>
                <th onclick={() => sortTable('chars')}>
                  Chars
                  {#if sortConfig.column === 'chars'}
                    {sortConfig.direction === 'asc' ? '▲' : '▼'}
                  {/if}
                </th>
                <th>Payload</th>
                <th onclick={() => sortTable('length')}>
                  Length
                  {#if sortConfig.column === 'length'}
                    {sortConfig.direction === 'asc' ? '▲' : '▼'}
                  {/if}
                </th>
              </tr>
            </thead>
            <tbody>
              {#each bruteForceResult as result, index (result.url)}
              <tr>
                <td>{index + 1}</td>
                <td>{result.response}</td>
                <td>{result.lines}L</td>
                <td>{result.words}W</td>
                <td>{result.chars}</td>
                <td>{result.payload}</td>
                <td>{parseFloat(result.length).toFixed(2)}</td>
              </tr>
              {/each}
            </tbody>
          </table>
        </div>
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

  .bruteforce-section {
    background-color: #1f1f1f;
    padding: 1.5rem;
    border-radius: 1rem;
    margin-top: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }

  .error {
    color: red;
    font-size: 0.8rem;
  }
</style>