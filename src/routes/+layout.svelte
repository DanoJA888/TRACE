<script lang="ts">
	import '../app.css';
	import Header from '../Fuzzer_Components/Header.svelte';
	import Side from '../Fuzzer_Components/Side.svelte';
	import Footer from '../Fuzzer_Components/Footer.svelte';
</script>

<Header />
<Side />

<main>
	<slot />
</main>

<Footer />
