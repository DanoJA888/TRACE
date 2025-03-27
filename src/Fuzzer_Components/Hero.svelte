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

    type FuzzResult = {
	    id: string | number;
	    response: string | number;
	    payload: string;
	    length: number;
    };
  
    let fuzzerParams: Record<string, string> = {};
    let fuzzerResult: FuzzResult[] = [];
    let acceptingParams = true;
    let fuzzing = false;
    let showResults = false;

    let startTime = 0;
    let elapsedTime = "0s";
    let timerInterval = 0;

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
  
    async function handleSubmit() {
        paramsToFuzz();
        acceptingParams = false;
        fuzzing = true;
        fuzzerResult = [];
        startTimer();

        try {
            const response = await fetch('http://localhost:8000/fuzzer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fuzzerParams)
            });

            if (response.ok && response.body) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let done = false;

            while (!done) {
                const { value, done: readerDone } = await reader.read();
                done = readerDone;
                if (value) {
                const chunk = decoder.decode(value, { stream: true });
                const updates = chunk.split('\n').filter(Boolean).map((line) => JSON.parse(line)["fuzzer results"]).flat();
                fuzzerResult = [...fuzzerResult, ...updates];
                }
            }

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
  
      {#if fuzzing}
        <h2>Fuzzing in progress...</h2>
      {/if}
  
      {#if showResults}
        <h2>Fuzzing Results</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Response</th>
              <th>Payload</th>
              <th>Length</th>
            </tr>
          </thead>
          <tbody>
            {#each fuzzerResult as row (row.id)}
                {#if typeof row.id === 'number'}
                 <tr>
                    <td>{row.id}</td>
                    <td>{row.response}</td>
                    <td>{row.payload}</td>
                    <td>{row.length}</td>
                </tr>
               {/if}
            {/each}
          </tbody>
        </table>
        <button on:click={() => ParamResults()}>Back</button>
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
  </style>  