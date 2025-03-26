<h1> This is the Tools screen </h1>

<script>

    function gotoCrawler() {
      window.location.href = "/main/tools/Crawler";
    }

    function gotoAI() {
      window.location.href = "/main/tools/AI";
    }
    
    </script>
    
    <nav>
      <button on:click={gotoCrawler}>Crawler</button>
      <br>
      <button on:click={gotoAI}>AI Credential Generator</button>
    
    </nav>