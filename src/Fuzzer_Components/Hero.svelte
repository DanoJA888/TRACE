<script lang="ts"></script>

<section class="max-w-4xl mx-auto mt-12 p-4 space-y-6">

	<div>
		<label for="targetUrl" class="block font-semibold mb-1 ">Target URL *</label>
		<input id="targetUrl" class="w-full border px-4 py-2 rounded" placeholder="https://juice-shop.herokuapp.com" />
	</div>

	<div>
		<label for="wordlist" class="block font-semibold mb-1">Word List *</label>
		<input id="wordlist" class="w-full border px-4 py-2 rounded mb-2" placeholder="/path/to/wordlist.txt" />
		<button class="px-4 py-2 bg-teal-400 text-white rounded shadow hover:bg-teal-500">📤 Upload Wordlist</button>
	</div>

	<div>
		<label class="block font-semibold mb-1 ">HTTP Method</label>
		<div class="flex gap-4">
			<label><input type="radio" name="method" value="GET" checked /> GET</label>
			<label><input type="radio" name="method" value="PUT" /> PUT</label>
			<label><input type="radio" name="method" value="POST" /> POST</label>
		</div>
	</div>

	<div>
		<label for="cookies" class="block font-semibold mb-1">Cookies (if applicable)</label>
		<input id="cookies" class="w-full border px-4 py-2 rounded" placeholder="NULL" />
	</div>

	<div>
		<label for="hideCodes" class="block font-semibold mb-1">Hide Status Code</label>
		<input id="hideCodes" class="w-full border px-4 py-2 rounded" placeholder="403, etc." />
	</div>

	<div>
		<label for="showOnly" class="block font-semibold mb-1">Show Only Status Code</label>
		<input id="showOnly" class="w-full border px-4 py-2 rounded" placeholder="200, 500, etc." />
	</div>

	<div>
		<label for="contentLength" class="block font-semibold mb-1">Filter by Content Length</label>
		<input id="contentLength" class="w-full border px-4 py-2 rounded" placeholder=">100, <500" />
	</div>

	<div>
		<label for="extraParams" class="block font-semibold mb-1">Additional Parameters (if applicable)</label>
		<input id="extraParams" class="w-full border px-4 py-2 rounded" placeholder="NULL" />
	</div>

	<div class="pt-4">
		<button class="px-6 py-3 bg-teal-500 text-white rounded hover:bg-teal-600">Start</button>
	</div>
</section>