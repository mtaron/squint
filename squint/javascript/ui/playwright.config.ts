import { execFileSync } from 'node:child_process';
import { defineConfig } from '@playwright/test';

// The app needs the cluster's services, so tests run against the deployment Tilt keeps up to date
function gatewayOrigin() {
	const address = execFileSync(
		'kubectl',
		[
			'get',
			'gateway',
			'--namespace',
			'agentgateway-system',
			'agentgateway-proxy',
			'--output',
			'jsonpath={.status.addresses[0].value}'
		],
		{ encoding: 'utf8' }
	).trim();
	if (!address) throw new Error('The gateway has no address; run `task lb-dev-cluster`');
	return `https://${address}`;
}

export default defineConfig({
	testMatch: '**/*.e2e.{ts,js}',
	use: { baseURL: process.env.PLAYWRIGHT_BASE_URL ?? gatewayOrigin() }
});
