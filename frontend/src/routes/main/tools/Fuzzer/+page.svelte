<script>
    let fuzzerInput = [
      { id: "target_url", label: "Target URL", type: "text", value: "", example: "Example-> https://test.com/FUZZ", required: true },
      { id: "word_list", label: "Word List", type: "text", value: "", example: "Example->test", required: true },
      { id: "http_method", label: "HTTP Method", type: "select", options: ["GET", "POST", "PUT"], value: "GET", required: true }
    ];
    
    let fuzzerParam = {target_url: ""}
    
    let fuzzerResult = [];
    let acceptingParams = true;
    let fuzzing = false;
    let showResults = false;
    
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


    //WillUpdates the fuzzerParams object when input values change.
    //then send to the backend 
    function FuzzerParamUpdate(id, value) {
    if (id) {
        fuzzerParam[id] = value;
        console.log("Updated " + id + " to: " + fuzzerParam[id]);
    }
    }
    
    async function handleSubmit() {
      const response = await fetch('http://localhost:8000/fuzzer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fuzzerParam),
      });
      
      if (response.ok) {
        fuzzingResults();
        const data = await response.json();
        fuzzerResult = data.results || [];
        console.log("Fuzzer results her ->:", fuzzerResult);
      } else {
        console.error("--Error with fuzzer--:", response.statusText);
      }
    }
  </script>
  
  <div class="fuzzerConfigPage">
    <div>
      <h1>Fuzzer</h1>
      {#if acceptingParams}
        <div>
          <form on:submit={(e) => {e.preventDefault(); handleSubmit(); paramsToFuzz()}}>
            {#each fuzzerInput as param}
              <label>
                {param.label}:
                {#if param.type === 'select'}
                  <select bind:value={fuzzerParam[param.id]} on:change={(e) => FuzzerParamUpdate(param.id, e.target.value)}>
                    {#each param.options as option}
                      <option value={option}>{option}</option>
                    {/each}
                  </select>
                {:else}
                  <input 
                    type={param.type} 
                    bind:value={fuzzerParam[param.id]} 
                    placeholder={param.example} 
                    required={param.required}
                    on:input={(e) => FuzzerParamUpdate(param.id, e.target.value)}
                  />
                {/if}
              </label>
            {/each}
            <button type="submit">Start fuzzer operation</button>
          </form>
        </div>
      {/if}
      
      {#if fuzzing}
        <div>
          <h2>Fuzzing...</h2>
        </div>
      {/if}
      
      {#if showResults}
        <h2>Fuzzing Results</h2>
        <div>
          {#each fuzzerResult as result}
            <div class="row">
              {#each Object.entries(result) as [key, value]}
                <span>{value}</span>
              {/each}
            </div>
          {/each}
          <button on:click={(e) => { ParamResults()}}>Back to Param Setup</button>
        </div>
      {/if}
    </div>
  </div>
  
  <style>
    form {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 300px;
      margin: 50px auto;
      padding: 20px;
      border: 1px solid #ccc;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    label {
      width: 100%;
      display: flex;
      flex-direction: column;
      font-weight: bold;
    }
    
    select {
      padding: 8px;
      margin-top: 5px;
      border-radius: 4px;
      border: 1px solid #ddd;
    }
    
    .row {
      display: flex;
      flex-direction: row;
      margin: 10px;
      padding: 5px;
      border-bottom: 1px solid #ccc;
    }
    
    .row span {
      margin-right: 15px;
    }
  </style>