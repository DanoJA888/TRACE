<script>
  let crawlerParams = [
    { id: "target-url", label: "Target URL", type: "text", value: "" },
    { id: "depth", label: "Crawl Depth", type: "number", value: "" },
    { id: "max-pages", label: "Max Pages", type: "number", value: "" },
    { id: "user-agent", label: "User Agent", type: "text", value: "" },
    { id: "delay", label: "Request Delay", type: "number", value: "" },
    { id: "proxy", label: "Proxy", type: "number", value: "" }
  ];

  function handleSubmit() {
    console.log("Form submitted:", crawlerParams);
  }
</script>

<div class="crawlerConfigPage">
  <div>
    <h1>Crawler</h1>
    <div>
      <form on:submit|preventDefault={handleSubmit}>
        {#each crawlerParams as param}
          <label>
            {param.label}:
            <input type={param.type} bind:value={param.value} required />
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

