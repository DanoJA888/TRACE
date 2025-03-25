<h1> This is the Tools screen </h1>

<script>

    function gotoCrawler() {
      window.location.href = "/main/tools/Crawler";
    }
    function gotoFuzzer() {
      window.location.href = "/main/tools/Fuzzer";
    }
    
    </script>
    
    <nav>
      <button on:click={gotoCrawler}>Crawler</button>
      <button on:click={gotoFuzzer}>Fuzzer</button>
    </nav>