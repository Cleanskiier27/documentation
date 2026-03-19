/**
 * AI Providers - Multi-provider abstraction layer for AI inference
 * Supports: OpenAI, Azure OpenAI, Anthropic Claude, Google Gemini, Custom endpoints
 * 
 * Usage:
 *   import { createProvider, getAvailableProviders, chat, embed, generateImage } from './aiProviders.js';
 *   const result = await chat('openai', [{ role: 'user', content: 'Hello!' }]);
 */

import crypto from 'crypto';

// Provider configurations from environment
const PROVIDER_CONFIGS = {
  openai: {
    name: 'OpenAI',
    apiKey: () => process.env.OPENAI_API_KEY,
    baseUrl: 'https://api.openai.com/v1',
    models: {
      chat: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
      embed: ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002'],
      image: ['dall-e-3', 'dall-e-2']
    },
    defaultModel: { chat: 'gpt-4o-mini', embed: 'text-embedding-3-small', image: 'dall-e-3' }
  },
  azure: {
    name: 'Azure OpenAI',
    apiKey: () => process.env.AZURE_OPENAI_KEY,
    endpoint: () => process.env.AZURE_OPENAI_ENDPOINT,
    deployment: () => process.env.AZURE_OPENAI_DEPLOYMENT || 'gpt-4o',
    apiVersion: '2024-02-15-preview',
    models: { chat: ['deployment'], embed: ['deployment'], image: [] }
  },
  anthropic: {
    name: 'Anthropic Claude',
    apiKey: () => process.env.ANTHROPIC_API_KEY,
    baseUrl: 'https://api.anthropic.com/v1',
    models: {
      chat: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229'],
      embed: [],
      image: []
    },
    defaultModel: { chat: 'claude-3-5-sonnet-20241022' }
  },
  gemini: {
    name: 'Google Gemini',
    apiKey: () => process.env.GOOGLE_GEMINI_KEY || process.env.GEMINI_API_KEY,
    baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
    models: {
      chat: ['gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash'],
      embed: ['text-embedding-004'],
      image: ['imagen-3.0-generate-001']
    },
    defaultModel: { chat: 'gemini-2.0-flash-exp', embed: 'text-embedding-004' }
  },
  custom: {
    name: 'Custom Endpoint',
    apiKey: () => process.env.CUSTOM_AI_KEY,
    baseUrl: () => process.env.CUSTOM_AI_ENDPOINT || 'http://localhost:11434/v1',
    models: { chat: ['*'], embed: ['*'], image: [] },
    defaultModel: { chat: 'llama2', embed: 'nomic-embed-text' }
  }
};

// Response cache
const responseCache = new Map();
const CACHE_TTL = parseInt(process.env.AI_CACHE_TTL_SECONDS || '300') * 1000;

function getCacheKey(provider, type, payload) {
  const hash = crypto.createHash('sha256')
    .update(JSON.stringify({ provider, type, payload }))
    .digest('hex');
  return hash.substring(0, 32);
}

function getCached(key) {
  const entry = responseCache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expiresAt) {
    responseCache.delete(key);
    return null;
  }
  return entry.data;
}

function setCache(key, data) {
  responseCache.set(key, { data, expiresAt: Date.now() + CACHE_TTL });
  // Cleanup old entries
  if (responseCache.size > 1000) {
    const now = Date.now();
    for (const [k, v] of responseCache) {
      if (now > v.expiresAt) responseCache.delete(k);
    }
  }
}

// Rate limiting
const rateLimits = new Map();
const RATE_LIMIT_PER_MINUTE = parseInt(process.env.AI_RATE_LIMIT_PER_MINUTE || '60');

function checkRateLimit(deviceId) {
  // UNLIMITED TOKENS MODE
  return { allowed: true, remaining: 999999, resetIn: 0 };
}

// Get available providers
export function getAvailableProviders() {
  const available = [];
  for (const [id, config] of Object.entries(PROVIDER_CONFIGS)) {
    const hasKey = typeof config.apiKey === 'function' ? !!config.apiKey() : !!config.apiKey;
    if (hasKey || id === 'custom') {
      available.push({
        id,
        name: config.name,
        capabilities: {
          chat: config.models.chat.length > 0,
          embed: config.models.embed.length > 0,
          image: config.models.image.length > 0
        },
        models: config.models
      });
    }
  }
  return available;
}

// Check if provider is available
export function isProviderAvailable(providerId) {
  const config = PROVIDER_CONFIGS[providerId];
  if (!config) return false;
  if (providerId === 'custom') return true;
  const apiKey = typeof config.apiKey === 'function' ? config.apiKey() : config.apiKey;
  return !!apiKey;
}

// ============ OPENAI PROVIDER ============
async function openaiChat(messages, options = {}) {
  const config = PROVIDER_CONFIGS.openai;
  const apiKey = config.apiKey();
  if (!apiKey) throw new Error('OpenAI API key not configured');

  const model = options.model || config.defaultModel.chat;
  const response = await fetch(`${config.baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: options.maxTokens || 1000,
      temperature: options.temperature ?? 0.7,
      stream: options.stream || false,
      ...options.extra
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI error: ${response.status} - ${error}`);
  }

  if (options.stream) {
    return response.body; // Return the readable stream
  }

  const data = await response.json();
  return {
    provider: 'openai',
    model,
    content: data.choices?.[0]?.message?.content || '',
    usage: data.usage,
    raw: data
  };
}

async function openaiEmbed(text, options = {}) {
  const config = PROVIDER_CONFIGS.openai;
  const apiKey = config.apiKey();
  if (!apiKey) throw new Error('OpenAI API key not configured');

  const model = options.model || config.defaultModel.embed;
  const input = Array.isArray(text) ? text : [text];

  const response = await fetch(`${config.baseUrl}/embeddings`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({ model, input })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI embedding error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'openai',
    model,
    embeddings: data.data.map(d => d.embedding),
    usage: data.usage
  };
}

async function openaiImage(prompt, options = {}) {
  const config = PROVIDER_CONFIGS.openai;
  const apiKey = config.apiKey();
  if (!apiKey) throw new Error('OpenAI API key not configured');

  const model = options.model || config.defaultModel.image;
  const response = await fetch(`${config.baseUrl}/images/generations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    },
    body: JSON.stringify({
      model,
      prompt,
      n: options.n || 1,
      size: options.size || '1024x1024',
      quality: options.quality || 'standard',
      response_format: 'url'
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI image error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'openai',
    model,
    images: data.data.map(d => ({ url: d.url, revisedPrompt: d.revised_prompt }))
  };
}

// ============ AZURE OPENAI PROVIDER ============
async function azureChat(messages, options = {}) {
  const config = PROVIDER_CONFIGS.azure;
  const apiKey = config.apiKey();
  const endpoint = config.endpoint();
  const deployment = options.deployment || config.deployment();

  if (!apiKey || !endpoint) throw new Error('Azure OpenAI not configured');

  const url = `${endpoint}/openai/deployments/${deployment}/chat/completions?api-version=${config.apiVersion}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'api-key': apiKey
    },
    body: JSON.stringify({
      messages,
      max_tokens: options.maxTokens || 1000,
      temperature: options.temperature ?? 0.7
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Azure OpenAI error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'azure',
    model: deployment,
    content: data.choices?.[0]?.message?.content || '',
    usage: data.usage,
    raw: data
  };
}

async function azureEmbed(text, options = {}) {
  const config = PROVIDER_CONFIGS.azure;
  const apiKey = config.apiKey();
  const endpoint = config.endpoint();
  const deployment = options.deployment || process.env.AZURE_OPENAI_EMBED_DEPLOYMENT || 'text-embedding-ada-002';

  if (!apiKey || !endpoint) throw new Error('Azure OpenAI not configured');

  const input = Array.isArray(text) ? text : [text];
  const url = `${endpoint}/openai/deployments/${deployment}/embeddings?api-version=${config.apiVersion}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'api-key': apiKey
    },
    body: JSON.stringify({ input })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Azure embedding error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'azure',
    model: deployment,
    embeddings: data.data.map(d => d.embedding),
    usage: data.usage
  };
}

// ============ ANTHROPIC CLAUDE PROVIDER ============
async function anthropicChat(messages, options = {}) {
  const config = PROVIDER_CONFIGS.anthropic;
  const apiKey = config.apiKey();
  if (!apiKey) throw new Error('Anthropic API key not configured');

  const model = options.model || config.defaultModel.chat;

  // Convert OpenAI-style messages to Anthropic format
  const systemMessage = messages.find(m => m.role === 'system')?.content;
  const nonSystemMessages = messages.filter(m => m.role !== 'system').map(m => ({
    role: m.role === 'assistant' ? 'assistant' : 'user',
    content: m.content
  }));

  const response = await fetch(`${config.baseUrl}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model,
      max_tokens: options.maxTokens || 1000,
      system: systemMessage,
      messages: nonSystemMessages
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Anthropic error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'anthropic',
    model,
    content: data.content?.[0]?.text || '',
    usage: { input_tokens: data.usage?.input_tokens, output_tokens: data.usage?.output_tokens },
    raw: data
  };
}

// ============ GOOGLE GEMINI PROVIDER ============
async function geminiChat(messages, options = {}) {
  const config = PROVIDER_CONFIGS.gemini;
  const apiKey = config.apiKey();
  if (!apiKey) throw new Error('Google Gemini API key not configured');

  const model = options.model || config.defaultModel.chat;

  // Convert to Gemini format
  const contents = messages.filter(m => m.role !== 'system').map(m => ({
    role: m.role === 'assistant' ? 'model' : 'user',
    parts: [{ text: m.content }]
  }));

  const systemInstruction = messages.find(m => m.role === 'system')?.content;

  const url = `${config.baseUrl}/models/${model}:generateContent?key=${apiKey}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents,
      systemInstruction: systemInstruction ? { parts: [{ text: systemInstruction }] } : undefined,
      generationConfig: {
        maxOutputTokens: options.maxTokens || 1000,
        temperature: options.temperature ?? 0.7
      }
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Gemini error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'gemini',
    model,
    content: data.candidates?.[0]?.content?.parts?.[0]?.text || '',
    usage: data.usageMetadata,
    raw: data
  };
}

async function geminiEmbed(text, options = {}) {
  const config = PROVIDER_CONFIGS.gemini;
  const apiKey = config.apiKey();
  if (!apiKey) throw new Error('Google Gemini API key not configured');

  const model = options.model || config.defaultModel.embed;
  const input = Array.isArray(text) ? text : [text];

  const url = `${config.baseUrl}/models/${model}:batchEmbedContents?key=${apiKey}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      requests: input.map(t => ({
        model: `models/${model}`,
        content: { parts: [{ text: t }] }
      }))
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Gemini embedding error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'gemini',
    model,
    embeddings: data.embeddings.map(e => e.values)
  };
}

// ============ CUSTOM ENDPOINT PROVIDER ============
async function customChat(messages, options = {}) {
  const config = PROVIDER_CONFIGS.custom;
  const baseUrl = typeof config.baseUrl === 'function' ? config.baseUrl() : config.baseUrl;
  const apiKey = config.apiKey();

  const model = options.model || config.defaultModel.chat;
  const headers = { 'Content-Type': 'application/json' };
  if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model,
      messages,
      max_tokens: options.maxTokens || 1000,
      temperature: options.temperature ?? 0.7
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Custom endpoint error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'custom',
    model,
    content: data.choices?.[0]?.message?.content || data.message?.content || '',
    usage: data.usage,
    raw: data
  };
}

async function customEmbed(text, options = {}) {
  const config = PROVIDER_CONFIGS.custom;
  const baseUrl = typeof config.baseUrl === 'function' ? config.baseUrl() : config.baseUrl;
  const apiKey = config.apiKey();

  const model = options.model || config.defaultModel.embed;
  const input = Array.isArray(text) ? text : [text];
  const headers = { 'Content-Type': 'application/json' };
  if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;

  const response = await fetch(`${baseUrl}/embeddings`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ model, input })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Custom embedding error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return {
    provider: 'custom',
    model,
    embeddings: data.data?.map(d => d.embedding) || data.embeddings || []
  };
}

// ============ UNIFIED API ============
const PROVIDER_HANDLERS = {
  openai: { chat: openaiChat, embed: openaiEmbed, image: openaiImage },
  azure: { chat: azureChat, embed: azureEmbed, image: null },
  anthropic: { chat: anthropicChat, embed: null, image: null },
  gemini: { chat: geminiChat, embed: geminiEmbed, image: null },
  custom: { chat: customChat, embed: customEmbed, image: null }
};

/**
 * Send a chat completion request
 * @param {string} provider - Provider ID (openai, azure, anthropic, gemini, custom)
 * @param {Array} messages - Array of {role, content} messages
 * @param {Object} options - {model, maxTokens, temperature, deviceId, useCache}
 */
export async function chat(provider, messages, options = {}) {
  const handler = PROVIDER_HANDLERS[provider]?.chat;
  if (!handler) throw new Error(`Provider '${provider}' does not support chat`);

  // Rate limiting
  if (options.deviceId) {
    const rateCheck = checkRateLimit(options.deviceId);
    if (!rateCheck.allowed) {
      throw new Error(`Rate limit exceeded. Try again in ${rateCheck.resetIn} seconds.`);
    }
  }

  // Check cache (skip for streaming)
  if (options.useCache !== false && !options.stream) {
    const cacheKey = getCacheKey(provider, 'chat', { messages, model: options.model });
    const cached = getCached(cacheKey);
    if (cached) return { ...cached, cached: true };
  }

  const result = await handler(messages, options);

  // Store in cache (skip for streaming)
  if (options.useCache !== false && !options.stream && result && !result.then) {
    const cacheKey = getCacheKey(provider, 'chat', { messages, model: options.model });
    setCache(cacheKey, result);
  }

  if (options.deviceId && !options.stream) {
    trackUsage(options.deviceId, provider, 'chat', result.usage?.total_tokens || 0);
  }

  return result;
}

/**
 * Generate embeddings
 * @param {string} provider - Provider ID
 * @param {string|Array} text - Text(s) to embed
 * @param {Object} options - {model, deviceId}
 */
export async function embed(provider, text, options = {}) {
  const handler = PROVIDER_HANDLERS[provider]?.embed;
  if (!handler) throw new Error(`Provider '${provider}' does not support embeddings`);

  if (options.deviceId) {
    const rateCheck = checkRateLimit(options.deviceId);
    if (!rateCheck.allowed) {
      throw new Error(`Rate limit exceeded. Try again in ${rateCheck.resetIn} seconds.`);
    }
  }

  return handler(text, options);
}

/**
 * Generate images
 * @param {string} provider - Provider ID
 * @param {string} prompt - Image prompt
 * @param {Object} options - {model, size, quality, n, deviceId}
 */
export async function generateImage(provider, prompt, options = {}) {
  const handler = PROVIDER_HANDLERS[provider]?.image;
  if (!handler) throw new Error(`Provider '${provider}' does not support image generation`);

  if (options.deviceId) {
    const rateCheck = checkRateLimit(options.deviceId);
    if (!rateCheck.allowed) {
      throw new Error(`Rate limit exceeded. Try again in ${rateCheck.resetIn} seconds.`);
    }
  }

  return handler(prompt, options);
}

// Get default provider
export function getDefaultProvider() {
  const preferred = process.env.AI_DEFAULT_PROVIDER || 'openai';
  if (isProviderAvailable(preferred)) return preferred;

  // Fallback order
  const fallbackOrder = ['openai', 'azure', 'anthropic', 'gemini', 'custom'];
  for (const p of fallbackOrder) {
    if (isProviderAvailable(p)) return p;
  }
  return null;
}

// Usage tracking per device
const deviceUsage = new Map();

export function trackUsage(deviceId, provider, type, tokens = 0) {
  if (!deviceUsage.has(deviceId)) {
    deviceUsage.set(deviceId, { requests: 0, tokens: 0, byProvider: {}, byType: {} });
  }
  const usage = deviceUsage.get(deviceId);
  usage.requests++;
  usage.tokens += tokens;
  usage.byProvider[provider] = (usage.byProvider[provider] || 0) + 1;
  usage.byType[type] = (usage.byType[type] || 0) + 1;
  usage.lastRequest = new Date().toISOString();
}

export function getDeviceUsage(deviceId) {
  return deviceUsage.get(deviceId) || { requests: 0, tokens: 0, byProvider: {}, byType: {} };
}

export function getAllUsage() {
  const result = {};
  for (const [id, usage] of deviceUsage) {
    result[id] = usage;
  }
  return result;
}

export default {
  chat,
  embed,
  generateImage,
  getAvailableProviders,
  isProviderAvailable,
  getDefaultProvider,
  trackUsage,
  getDeviceUsage,
  getAllUsage,
  checkRateLimit
};
