/**
 * Cloudflare Pages Function — Mews API proxy
 * Route: /mews/* → https://api.mews.com/*
 *
 * Vervangt de /mews/* route uit server.js.
 * Voegt de vereiste Origin/Referer headers toe die Mews verwacht.
 */
export async function onRequest(context) {
  const { request, params } = context;

  // Bouw de Mews URL op basis van het pad achter /mews/
  const path = params.path ? params.path.join('/') : '';
  const url = new URL(request.url);
  const mewsUrl = `https://api.mews.com/${path}${url.search}`;

  // Haal de request body op (voor POST/PUT)
  const body = request.method !== 'GET' && request.method !== 'HEAD'
    ? await request.arrayBuffer()
    : undefined;

  const mewsResponse = await fetch(mewsUrl, {
    method: request.method,
    headers: {
      'Content-Type': 'application/json',
      'Origin': 'https://apps.mews.com',
      'Referer': 'https://apps.mews.com/',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    },
    body,
  });

  const responseBody = await mewsResponse.arrayBuffer();

  return new Response(responseBody, {
    status: mewsResponse.status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
