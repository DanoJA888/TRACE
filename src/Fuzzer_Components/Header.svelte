<script lang="ts">
	let currentStep = 1;
</script>

<header class="flex flex-col w-full bg-white border-b">
	<div class="max-w-6xl mx-auto w-full flex justify-between items-center p-4">
		<h1 class="text-2xl font-semibold text-slate-800">Parameter Fuzzing</h1>
		<div class="flex items-center gap-6 text-sm">
			<!-- Stepper -->
			{#each ['Configuration', 'Running', 'Results'] as step, i (i)}
				<div class="flex items-center gap-2">
					<div class={`w-3 h-3 rounded-full ${currentStep >= i + 1 ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
					<span class={`${currentStep === i + 1 ? 'text-blue-600 font-semibold' : 'text-gray-500'}`}>{step}</span>
				</div>
				{#if i < 2}
					<div class="w-6 h-px bg-gray-300"></div>
				{/if}
			{/each}
		</div>
	</div>
</header>