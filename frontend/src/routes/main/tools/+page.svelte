<h1> Tools </h1>

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
        <div class="row">
          <span> Crawler </span>
          <button on:click={gotoCrawler}>Select</button>
        </div>

        <div class="row">
          <span> Fuzzer </span>
          <button on:click={gotoFuzzer}>Select</button>
        </div>

        <div class="row">
          <span> Brute Forcer </span>
          <button on:click={gotoBruteForcer}>Select</button>
        </div>

        <div class="row">
          <span> AI Credential Generator </span>
          <button on:click={gotoAI}>Select</button>
        </div>
        
      </div>
    </nav>