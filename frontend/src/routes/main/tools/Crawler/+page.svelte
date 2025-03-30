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

  let crawlResult = []; // Updated dynamically during crawling

  let acceptingParams = true;
  let crawling = false;
  let displayingResults = false;

  let totalPages = 0;
  let crawledPages = 0;

  let startTime = null;
  let elapsedTime = "0s";
  let timerInterval;

  let processedRequests = 0;
  let filteredRequests = 0;
  let requestsPerSecond = 0;

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
    paramsToCrawling();
    startTimer(); // Start the timer
    crawledPages = 0; // Reset progress
    totalPages = crawlerParams.max_pages || 0; // Set total pages if max_pages is defined

    const response = await fetch('http://localhost:8000/crawler', { //This is where the params are being sent
      method: 'POST', 
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(crawlerParams),
    });

    if (response.ok) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const updates = chunk.split('\n').filter(Boolean).map(JSON.parse);
          crawlResult = [...crawlResult, ...updates];
          crawledPages += updates.length; // Update progress

          // Update real-time metrics
          processedRequests += updates.length;
          filteredRequests = crawlResult.filter((item) => !item.error).length;
          requestsPerSecond = (processedRequests / ((Date.now() - startTime) / 1000)).toFixed(2);
        }
      }

      crawlingToResults();
    } else {
      console.error("Error starting crawler:", response.statusText);
    }
    stopTimer(); // Stop the timer
  }
</script>
  
<div class="crawlerConfigPage">
  <div>
    <h1>Crawler</h1>
    {#if acceptingParams}
      <div>
        <form onsubmit="{(e) => {e.preventDefault(); handleSubmit(); paramsToCrawling()}}">
          {#each crawlerInput as param}
            <label>
              <span>{param.label}:</span>
              <input type={param.type} bind:value={crawlerParams[param.id]} placeholder={param.example} requirement={param.required} oninput={(e) => dynamicCrawlerParamUpdate(param.id, e.target.value)}/>
            </label>
          {/each}

          <button type="submit">Submit</button>
        </form>
      </div>
    {/if}
    
    {#if crawling}
      <div>
        <h2>Running...</h2>
        <div class="progress-bar">
          <div
            class="progress"
            style="width: {totalPages > 0 ? (crawledPages / totalPages) * 100 : 0}%"
          ></div>
        </div>
        <p>{crawledPages} / {totalPages || "∞"} pages crawled</p>
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
          {#if crawlResult.length === 0}
            <p>No data received yet. Please wait...</p>
          {/if}
          <table>
            <thead>
              <tr>
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
              {#each crawlResult as crawledURL, index (crawledURL.id)}  <!-- Ensure each item is uniquely identified -->
                <tr>
                  <td>{crawledURL.id}</td>
                  <td>{crawledURL.url}</td>
                  <td>{crawledURL.title}</td>
                  <td>{crawledURL.word_count}</td>
                  <td>{crawledURL.char_count}</td>
                  <td>{crawledURL.link_count}</td>
                  <td>{crawledURL.error ? 'True' : 'False'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}


    {#if displayingResults}
      <h2>Crawl Results</h2>
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
            {#each crawlResult as crawledURL, index (crawledURL.id)}  <!-- Ensure each item is uniquely identified -->
              <tr>
                <td>{crawledURL.id}</td>
                <td>{crawledURL.url}</td>
                <td>{crawledURL.title}</td>
                <td>{crawledURL.word_count}</td>
                <td>{crawledURL.char_count}</td>
                <td>{crawledURL.link_count}</td>
                <td>{crawledURL.error ? 'True' : 'False'}</td>
              </tr>
            {/each}
          </tbody>
        </table>
        <button onclick={(e) => { resultsToParams() }}>Back to Param Setup</button>
      </div>
    {/if}
  </div>
</div>

<!-- doing this here for now so i dont bloat the css adding space between the table and the return button-->
<style>
  .results-table {
    margin-top: 20px; /* Add space between the table and the button */
  }

  .results-table button {
    margin-top: 20px; /* Add space between the table and the button */
  }
</style>


<!-- <style>
  .progress-bar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
  }

  .progress {
    height: 20px;
    background-color: #76c7c0;
    transition: width 0.3s ease;
  }
</style> -->