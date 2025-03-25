<script>
  
  let wordlistInput = { id: "wordlist", accept: ".json, .txt", label: "Word List", type: "file", value: "", example: "Ex: wordlist.txt", required: true }
  let userPassInput = [
    { id: "userChar", type: "checkbox", label: "Characters", isChecked: true},
    { id: "userNum", type: "checkbox", label: "Numbers", isChecked: true},
    { id: "userSymb", type: "checkbox", label: "Symbols", isChecked: true},
    { id: "passChar", type: "checkbox", label: "Characters", isChecked: true},
    { id: "passChar", type: "checkbox", label: "Numbers", isChecked: true},
    { id: "passSymb", type: "checkbox", label: "Symbols", isChecked: true}
  ];
  let lengthInput = [
    { id: "userLen", label: "Length", type: "number", value: "", example: "Ex: 12", required: true },
    { id: "passLen", label: "Length", type: "number", value: "", example: "Ex: 12", required: true }
  ]

  let aiParams = {
    wordlist : ""
  }

  let aiResult = []

  let acceptingParams = true;
  let generating = false;
  let displayingResults = false;

  function paramsToGenerate(){
    acceptingParams = false;
    generating = true;
  }

  function generatingToResults(){
    generating = false;
    displayingResults = true;
  }

  function resultsToParams(){
    displayingResults = false;
    acceptingParams = true;
  }

  function dynamicAiParamUpdate(id, value) {
  }

  // This is for inputs to be sent to the backend for computation.
  async function handleSubmit() {
  }

  async function handleFile() {
  }
</script>
  
  <div class="aiConfigPage">
    <div>
      <h1>AI Generator</h1>
      {#if acceptingParams}
        <div>
            <form  onsubmit= "{(e) => {e.preventDefault(); handleSubmit(); paramsToGenerate()}}">

                {wordlistInput.label}
                <input accept=wordlistInput.accept type={wordlistInput.type} bind:value={wordlistInput.id} placeholder={wordlistInput.example} requirement={wordlistInput.required} oninput={(e) => dynamicAiParamUpdate(wordlistInput.id, e.target.value)}/>

                {#each userPassInput as param}
                    <label>
                        {param.label}:
                        <input type="checkbox" bind:checked={param.isChecked} oninput={(e) => dynamicAiParamUpdate(param.id, e.target.value)} />
                    </label>
                {/each}

                {#each lengthInput as param}
                    <label>
                        {param.label}:
                        <input type={param.type} bind:value={lengthInput[param.id]} placeholder={param.example} requirement={param.required} oninput={(e) => dynamicAiParamUpdate(param.id, e.target.value)}/>
                    </label>
                {/each}

            <button type="submit">Submit</button>
          </form>
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