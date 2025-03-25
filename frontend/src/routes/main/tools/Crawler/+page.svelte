<script>
  let crawlerInput = [
    { id: "url", label: "Target URL", type: "text", value: "", example: "Ex: https://example.com", required: true },
    { id: "depth", label: "Crawl Depth", type: "number", value: "", example: "Ex: 2", required: false },
    { id: "max_pages", label: "Max Pages", type: "number", value: "", example: "Ex: 15", required: false },
    { id: "user_agent", label: "User Agent", type: "text", value: "", example: "Ex: Mozilla/5.0", required: false },
    { id: "delay", label: "Request Delay", type: "number", value: "", example: "Ex: 5", required: false },
    { id: "proxy", label: "Proxy", type: "text", value: "", example: "Ex: 8080", required: false }
  ];

  let crawlerParams = {
    url : ""
  }

  let crawlResult = []

  let acceptingParams = true;
  let crawling = false;
  let displayingResults = false;

  function paramsToCrawling(){
    acceptingParams = false;
    crawling = true;
  }

  function crawlingToResults(){
    crawling = false;
    displayingResults = true;
  }

  function resultsToParams(){
    displayingResults = false;
    acceptingParams = true;
  }

  //instead of hard coded values in dict, dynamically add items to dictionary
  function dynamicCrawlerParamUpdate(id, value) {
    crawlerParams[id] = value;
    console.log(crawlerParams[id])
  }
  

  // This is for inputs to be sent to the backend for computation.
  async function handleSubmit() {
    const response = await fetch('http://localhost:8000/crawler', { //This is where the params are being sent
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(crawlerParams),
    });
    if (response.ok) {
      crawlingToResults()
      crawlResult = await response.json();
      console.log("Crawler results:", crawlResult);
    } else {
      console.error("Error starting crawler:", response.statusText);
    }
  }
</script>
  
  <div class="crawlerConfigPage">
    <div>
      <h1>Crawler</h1>
      {#if acceptingParams}
        <div>
          <form  onsubmit= "{(e) => {e.preventDefault(); handleSubmit(); paramsToCrawling()}}">
            {#each crawlerInput as param}
              <label>
                {param.label}:
                <input type={param.type} bind:value={crawlerParams[param.id]} placeholder={param.example} requirement={param.required} oninput={(e) => dynamicCrawlerParamUpdate(param.id, e.target.value)}/>
              </label>
            {/each}
            
            <button type="submit">Submit</button>
          </form>
        </div>
      {/if}
      
      {#if crawling}
        <div>
          <h2>Crawling...</h2>
        </div>
      {/if}


      {#if displayingResults}
      <h2>Crawl Results</h2>
      <div class="results-table">
        <table>
          <thead>
            <tr>
              <!-- Fixed header order -->
              <th>ID</th>
              <th>URL</th>
              <th>Title</th>
              <th>Word Count</th>
              <th>Character Count</th>
              <th>Links</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {#each crawlResult as crawledURL}
              <tr>
                <!-- Fixed row order to match the header -->
                <td>{crawledURL.id}</td>
                <td>{crawledURL.url}</td>
                <td>{crawledURL.title}</td>
                <td>{crawledURL.word_count}</td>
                <td>{crawledURL.char_count}</td>
                <td>{crawledURL.link_count}</td>
                <td>{crawledURL.error ? 'True' : 'False'}</td> <!-- Display error as True or False -->
              </tr>
            {/each}
          </tbody>
        </table>
        <button onclick={(e) => { resultsToParams()}}>Back to Param Setup</button>
      </div>
    {/if}
    </div>
  </div>
    

  <!-- just commenting this out incase i need to copy this over to the style sheet -->
  <!-- <style>
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

  </style> -->
  
  