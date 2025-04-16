<script>

    function gotoCrawler() {
      window.location.href = "/main/tools/Crawler";
    }

    function gotoFuzzer() {
      window.location.href = "/main/tools/Fuzzer";
    }

    function gotoBruteForcer() {
      window.location.href = "/main/tools/BruteForcer";
    }

    function gotoAI() {
      window.location.href = "/main/tools/AI";
    }
    
    </script>
    
    <nav>
      <div class="toolsConfigPage">
        <h1>Tools</h1>
        <h3>[Project Name]</h3>
        <div class="row">
          <h3 style="padding-left: 15px;"> Crawler </h3>
          <button on:click={gotoCrawler} title="Navigates to the Crawler page">Select</button>
        </div>

        <div class="row">
          <h3 style="padding-left: 15px;"> Fuzzer </h3>
          <button on:click={gotoFuzzer} title="Navigates to the Fuzzer page">Select</button>
        </div>

        <div class="row">
          <h3 style="padding-left: 15px;"> Brute Forcer </h3>
          <button on:click={gotoBruteForcer} title="Navigates to the Brute Forcer page">Select</button>
        </div>

        <div class="row">
          <h3 style="padding-left: 15px;"> AI Credential Generator </h3>
          <button on:click={gotoAI} title="Navigates to the AI Credential Generastor page">Select</button>
        </div>
        
      </div>
    </nav>