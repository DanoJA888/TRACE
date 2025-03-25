<h1> This is the Crawler screen </h1>

<script>
    let crawlerInput = [
      { id: "url", label: "Target URL", type: "text", value: "", example: "https://example.com", required: true },
      { id: "depth", label: "Crawl Depth", type: "number", value: "", example: "#", required: false },
      { id: "max_pages", label: "Max Pages", type: "number", value: "", example: "#", required: false },
      { id: "user_agent", label: "User Agent", type: "text", value: "", example: "Mozilla/5.0", required: false },
      { id: "delay", label: "Request Delay", type: "number", value: "", example: "#", required: false },
      { id: "proxy", label: "Proxy", type: "number", value: "", example: "#", required: false }
    ];

    let crawlerParams = {
      url : "",
      depth : 0,
      max_pages: 0,
      user_agent: "",
      delay : "",
      proxy: ""
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
       const result = await response.json();
       console.log("Crawler started:", result);
     } else {
       console.error("Error starting crawler:", response.statusText);
     }
   }



  </script>
  
  <div class="crawlerConfigPage">
    <div>
      <h1>Crawler</h1>
      <div>
        <form on:submit|preventDefault={handleSubmit}>
          {#each crawlerInput as param}
            <label>
              {param.label}:
              <input type={param.type} bind:value={crawlerParams[param.id]} placeholder={param.example} requirement={param.required ? "required" : ""} />
            </label>
          {/each}
          
          <button type="submit">Submit</button>
        </form>
      </div>
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
  
  </style>
  
  