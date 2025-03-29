<script lang="ts">
    let fuzzerInput = [
      { id: "target_url", label: "Target URL", type: "text", value: "", example: "https://example.com/FUZZ", required: true },
      { id: "word_list", label: "Word List", type: "text", value: "", example: "admin,test,login", required: true },
      { id: "http_method", label: "HTTP Method", type: "select", options: ["GET", "POST", "PUT"], value: "GET", required: true },
      { id: "cookies", label: "Cookies", type: "text", value: "", example: "auth_token=abc123", required: false },
      { id: "hide_codes", label: "Hide Codes", type: "text", value: "", example: "403,404", required: false },
      { id: "show_only", label: "Show Only Codes", type: "text", value: "", example: "200", required: false },
      { id: "content_length", label: "Content Length Filter", type: "text", value: "", example: ">100,<500", required: false },
      { id: "extra_params", label: "Extra Parameters", type: "text", value: "", example: "token=abc", required: false }
    ];
    
    let stats = {
      running_time: 0,
      processed_requests: 0,
      filtered_requests: 0,
      requests_per_sec: 0
    };

    type FuzzResult = {
	    id: number;
      response: number;
      lines: number;
      words: number;
      chars: number;
      payload: string;
      length: number;
      error: boolean;
    };
  
    let fuzzerParams: Record<string, string> = {};
    let fuzzerResult: FuzzResult[] = [];
    let acceptingParams = true;
    let fuzzing = false;
    let showResults = false;
    let startTime = 0;
    let elapsedTime = "0s";
    let timerInterval = 0;
    let terminalVisible = false;
    let terminalLogs: string[] = [];
    let showTerminal = false;
    let eventSource: EventSource | null = null;


    //timer functions
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

  
    function FuzzerParamUpdate(id: string, value: string) {
      fuzzerParams[id] = value;
      console.log("Updated", id, "to:", fuzzerParams[id]);
    }
  
    function paramsToFuzz() {
      acceptingParams = false;
      fuzzing = true;
    }
  
    function fuzzingResults() {
      fuzzing = false;
      showResults = true;
    }
  
    function ParamResults() {
      showResults = false;
      acceptingParams = true;
    }

    //Buttons
    function pauseFuzzer() {
      console.log("Pause clicked");
      // Notes for later: Send pause request to backend or stop frontend updates
    }

    function stopFuzzer() {
      console.log("Stop clicked");
      // Notes for later: Abort request, reset state, etc.
      stopTimer();
      fuzzing = false;
      showResults = true; // or false if you want to hide results
    }

    function restartFuzzer() {
      console.log("Restart clicked");
      fuzzerResult = [];
      stats = {
        running_time: 0,
        processed_requests: 0,
        filtered_requests: 0,
        requests_per_sec: 0
      };
      handleSubmit(); // re-trigger fuzzing
    }

    //Terminal functions
    function toggleTerminal() {
      showTerminal = !showTerminal;
      console.log(showTerminal ? "Terminal opened" : "Terminal closed");
    }

    async function handleSubmit() {
      paramsToFuzz();
      acceptingParams = false;
      fuzzing = true;
      fuzzerResult = [];
      terminalLogs = [];
      startTimer();

      eventSource = new EventSource("http://localhost:8000/fuzzer/stream");

      eventSource.onmessage = (event) => {
        terminalLogs = [...terminalLogs, event.data];
        console.log("TERMINAL LINE:", event.data); // Debug
      };

      eventSource.onerror = () => {
        console.error("EventSource failed");
        eventSource?.close();
      };


      try {
        const response = await fetch("http://localhost:8000/fuzzer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(fuzzerParams),
        });
        
        //json conversion
        if (response.ok) {
          const fullJson = await response.json();
          fuzzerResult = fullJson["fuzzer results"];
          stats = fullJson["stats"]; 
          showResults = true;
        } else {
          console.error("Fuzzer failed to respond:", response.statusText);
        }
      } catch (err) {
        console.error("Fuzzer error:", err);
      }

      stopTimer();
      fuzzing = false;
    }
  </script>
  
  <!--fuzzer configuration config-->
  <section class="fuzzerConfigPage">
    <div>
      <h1>Fuzzer</h1>
      {#if acceptingParams}
        <form on:submit|preventDefault={() => { handleSubmit(); paramsToFuzz(); }}>
          {#each fuzzerInput as param}
            <label>
              {param.label}:
              {#if param.type === 'select'}
                <select bind:value={fuzzerParams[param.id]} on:change={(e) => FuzzerParamUpdate(param.id, (e.target as HTMLSelectElement).value)}>
                    {#if param.options}
                        {#each param.options as option}
                        <option value={option}>{option}</option>
                        {/each}
                    {/if}
                </select>
              {:else}
                <input
                  type={param.type}
                  bind:value={fuzzerParams[param.id]}
                  placeholder={param.example}
                  required={param.required}
                  on:input={(e) => FuzzerParamUpdate(param.id, (e.target as HTMLInputElement).value)}
                />
              {/if}
            </label>
          {/each}
          <button type="submit">Start Fuzzer</button>
        </form>
      {/if}
      
      <!-- Fuzzing page-->
      {#if fuzzing}
        <h2>Fuzzing in progress...</h2>
      {/if}
  
      {#if showResults}
        <h2>Fuzzing Results</h2>
        <div class="stats">
          <p><strong>Running Time:</strong> {stats.running_time} s</p>
          <p><strong>Processed Requests:</strong> {stats.processed_requests}</p>
          <p><strong>Filtered Requests:</strong> {stats.filtered_requests}</p>
          <p><strong>Requests/sec:</strong> {stats.requests_per_sec}</p>
        </div>
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
            {#each fuzzerResult as row (row.id)}
                {#if typeof row.id === 'number'}
                 <tr>
                  <td>{row.id}</td>
                  <td>{row.response}</td>
                  <td>{row.lines}</td>
                  <td>{row.words}</td>
                  <td>{row.chars}</td>
                  <td>{row.payload}</td>
                  <td>{row.length}</td>
                  <td>{row.error ? 'True' : 'False'}</td>
                </tr>
               {/if}
            {/each}
          </tbody>
        </table>
        <div class="fuzzer-controls">
          <button on:click={() => pauseFuzzer()}>Pause</button>
          <button on:click={() => stopFuzzer()}>Stop</button>
          <button on:click={() => restartFuzzer()}>Restart</button>
          <button on:click={() => toggleTerminal()} class="control-btn secondary-btn">Show Terminal</button>
        </div>
      {/if}
      
      <!--Toggle Terminal-->
      {#if showTerminal}
        <div class="terminal-overlay">
          <div class="terminal-header">
            <span>Fuzzer — 80×24</span>
            <button on:click={() => toggleTerminal()}>×</button>
          </div>
          <div class="terminal-body">
            {#each terminalLogs as line}
              <pre>{line}</pre>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </section>
  
  <style>
    form {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 1rem;
    }
  
    label {
      display: flex;
      flex-direction: column;
      font-weight: bold;
    }
  
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
    }
  
    th, td {
      border: 1px solid #ddd;
      padding: 8px;
    }
  
    th {
      background-color: #f4f4f4;
    }

    .fuzzer-controls {
      display: flex;
      gap: 1rem;
      margin-top: 1rem;
    }

    .fuzzer-controls button {
      padding: 0.6rem 1.5rem;
      background-color: #b8dbe4;
      border: none;
      border-radius: 5px;
      font-weight: bold;
      cursor: pointer;
      transition: background-color 0.2s;
    }

    .fuzzer-controls button:hover {
      background-color: #a4cbd6;
    }

    .terminal-overlay {
      position: fixed;
      top: 20%;
      left: 10%;
      width: 80%;
      height: 300px;
      background: black;
      color: lime;
      overflow-y: scroll;
      z-index: 999;
      border: 2px solid #444;
      border-radius: 6px;
      font-family: monospace;
    }

    .terminal-header {
      background: #222;
      color: white;
      padding: 8px;
      display: flex;
      justify-content: space-between;
      font-weight: bold;
    }

    .terminal-body {
      padding: 10px;
      white-space: pre-wrap;
      font-size: 14px;
    }
  </style>  