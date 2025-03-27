<script>
  
  let wordlistInput = { id: "wordlist", type: "file", accept: ".txt", label: "Word List", value: "", example: "Ex: wordlist.txt", required: true }

  let usernameInput = [
    { id: "userChar", type: "checkbox", label: "Characters", isChecked: true},
    { id: "userNum", type: "checkbox", label: "Numbers", isChecked: true},
    { id: "userSymb", type: "checkbox", label: "Symbols", isChecked: true}
  ];

  let passwordInput = [
    { id: "passChar", type: "checkbox", label: "Characters", isChecked: true},
    { id: "passNum", type: "checkbox", label: "Numbers", isChecked: true},
    { id: "passSymb", type: "checkbox", label: "Symbols", isChecked: true}
  ]

  let usernameLenInput = { id: "userLen", type: "number", label: "Length", value: "", example: "Ex: 12", required: true }
  let passwordLenInput = { id: "passLen", type: "number", label: "Length", value: "", example: "Ex: 12", required: true }

  let wordlist;

  let aiParams = {
    wordlist : ""
  }

  for(let i = 0; i < usernameInput.length;i++){
    aiParams[usernameInput[i].id] = usernameInput[i].value;
  }
  console.log("Populated aiParams with Username checkbox...");

  for(let i = 0; i < passwordInput.length;i++){
    aiParams[passwordInput[i].id] = passwordInput[i].value;
  }
  console.log("Populated aiParams with Password checkbox...");

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
    aiParams[id] = value;
    console.log(`Updated ${id}: ${value}`);
  }

  // Checks that the file is exclusively txt file and updates our file accordingly
  async function handleFile(event) {
    const selectedFile = event.target.files[0];

    if (selectedFile && selectedFile.type === "text/plain") {
      wordlist = selectedFile;

      // Update param after file validation
      dynamicAiParamUpdate(wordlistInput.id, selectedFile);
      console.log("Valid file selected:", wordlist.name);

    } else {
      alert("Please select a valid .txt file");
      event.target.value = ""; // Reset input
      wordlist = null;
    }
  }

  // This is for inputs to be sent to the backend for computation.
  async function handleSubmit() {
    console.log("Form Submitted");

    const formData = newFormData();

    if(wordlist) {
      formData.append("wordlist", wordlist);
    }

    formData.append("date", JSON.stringify(aiParams));

    try{
      const response = await fetch('http://localhost:8000/ai', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        console.log("Generating...")
      } else {
        console.error("Error starting generate:", response.statusText);
      }
    } catch (error) {
        console.error("Request failed:", error);
    }
  }
</script>
  
  <div class="aiConfigPage">
    <div>
      <h1>AI Generator</h1>
      {#if acceptingParams}
        <div>
            <form onsubmit= "{(e) => {e.preventDefault(); handleSubmit(); paramsToGenerate()}}">

                {wordlistInput.label}
                <input accept=wordlistInput.accept type={wordlistInput.type} placeholder={wordlistInput.example} requirement={wordlistInput.required} onchange={handleFile}/>

                <div class="input-container">
                  <div class="column">
                  <label>Username</label>
                  {#each usernameInput as param}
                      <label>
                          {param.label}:
                          <input type="checkbox" bind:checked={param.isChecked} onchange={(e) => dynamicAiParamUpdate(param.id, e.target.checked)} />
                      </label>
                  {/each}

                  <label>
                    {usernameLenInput.label}:
                    <input type={usernameLenInput.type} bind:value={usernameLenInput[usernameLenInput.id]} placeholder={usernameLenInput.example} requirement={usernameLenInput.required} oninput={(e) => dynamicAiParamUpdate(usernameLenInput.id, e.target.value)}/>
                  </label>

                  </div>

                  <div class="column">
                  <label>Password</label>
                  {#each passwordInput as param}
                      <label>
                          {param.label}:
                          <input type="checkbox" bind:checked={param.isChecked} onchange={(e) => dynamicAiParamUpdate(param.id, e.target.checked)} />
                      </label>
                  {/each}

                  <label>
                    {passwordLenInput.label}:
                    <input type={passwordLenInput.type} bind:value={passwordLenInput[passwordLenInput.id]} placeholder={passwordLenInput.example} requirement={passwordLenInput.required} oninput={(e) => dynamicAiParamUpdate(passwordLenInput.id, e.target.value)}/>
                  </label>

                  </div>
                </div>

            <button type="submit">Submit</button>
          </form>
        </div>
      {/if}

      {#if generating}
        <div>
          <h2>Generating Credentials...</h2>
        </div>
      {/if}

      {#if displayingResults}
        <h2>AI Credential Generator Results</h2>
        <div>
          <button onclick={(e) => { resultsToParams()}}>Back to Param Setup</button>
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
      width: 400px;
      margin: 50px auto;
      padding: 20px;
      border: 1px solid #ccc;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .input-container {
    display: flex;
    gap: 20px; /* Adjust spacing between columns */
    justify-content: space-between; /* Distributes columns evenly */
    }

    .column {
        display: flex;
        flex-direction: column;
        gap: 10px; /* Adjusts spacing between elements */
        width: 48%; /* Ensures equal width */
    }
  
    label {
      width: 100%;
      display: flex;
      flex-direction: column;
      font-weight: bold;
    }
    
    .input-label {
    display: flex;
    align-items: center;
    gap: 10px; /* Adjust spacing between label and input */
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