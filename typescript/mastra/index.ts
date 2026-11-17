/**
 * Order-status agent built with Mastra, served over HTTP.
 *
 * POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
 * Needs OPENAI_API_KEY. Run: npm install && npm start
 */

import { createServer } from 'node:http';

import { Agent } from '@mastra/core/agent';
import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

const getOrderStatus = createTool({
  id: 'getOrderStatus',
  description: 'Look up the shipping status of an order by its id.',
  inputSchema: z.object({ orderId: z.string().describe('The order id') }),
  outputSchema: z.object({ status: z.string() }),
  execute: ({ orderId }) => Promise.resolve({ status: `Order ${orderId}: shipped, arriving Friday.` }),
});

const agent = new Agent({
  id: 'order-agent',
  name: 'order-agent',
  instructions: 'You are a customer support agent. Use your tools to answer questions about orders.',
  model: `openai/${process.env['OPENAI_MODEL'] ?? 'gpt-4o-mini'}`,
  tools: { getOrderStatus },
});

const server = createServer(async (req, res) => {
  if (req.method !== 'POST' || req.url !== '/run') {
    res.writeHead(404).end();
    return;
  }
  try {
    let body = '';
    for await (const chunk of req) body += chunk;
    const { prompt } = JSON.parse(body) as { prompt: string };
    const result = await agent.generate(prompt);
    res.writeHead(200, { 'Content-Type': 'application/json' }).end(JSON.stringify({ answer: result.text }));
  } catch (err) {
    res.writeHead(500).end(String(err));
  }
});

const port = Number(process.env['PORT'] ?? 8000);
server.listen(port, () => console.log(`listening on :${port}`));
