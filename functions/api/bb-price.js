/**
 * Cloudflare Pages Function — Logies & Ontbijt laagste prijs
 * GET /api/bb-price → { price: 89.5 } of { error: "..." }
 *
 * Leest de Mews sessie uit KV, haalt 30-nachten availability op
 * voor de Comfort kamer, en stuurt de laagste p.p.-prijs terug (afgerond op €0,50).
 */

const CORS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};

const CONFIG_ID     = '6dc9094c-76e3-4fd8-83a7-af1d00ffc556';
const HOTEL_ID      = '65a522c9-4828-413d-9ad8-af1d00ffb83f';
const COMFORT_ID    = '98900f3b-e5e2-49c9-9776-af1d00ffc315';
const CACHE_SECONDS = 3600; // prijs 1 uur cachen in CF edge cache

function toYMD(d) {
  return d.toISOString().slice(0, 10);
}

function ceilHalf(price) {
  return Math.ceil(price * 2) / 2;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: CORS });
}

export async function onRequestGet(context) {
  const { env, request } = context;
  const kv = env.ASTERIA_KV;

  if (!kv) return json({ error: 'KV not configured' }, 500);

  const session = await kv.get('mews_session');
  const client  = await kv.get('mews_client') || 'Mews Distributor 5656.0.0';

  if (!session) return json({ error: 'no session' });

  const now      = new Date();
  const checkin  = new Date(now); checkin.setDate(now.getDate() + 1);
  const checkout = new Date(now); checkout.setDate(now.getDate() + 31);

  let data;
  try {
    const res = await fetch('https://api.mews.com/api/distributor/v1/hotels/getAvailability', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin':  'https://apps.mews.com',
        'Referer': 'https://apps.mews.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      },
      body: JSON.stringify({
        Client:          client,
        SessionId:       session,
        ConfigurationId: CONFIG_ID,
        HotelId:         HOTEL_ID,
        StartUtc:        toYMD(checkin)  + 'T12:00:00Z',
        EndUtc:          toYMD(checkout) + 'T12:00:00Z',
        CategoryIds:     [COMFORT_ID],
      }),
    });
    data = await res.json();
  } catch (e) {
    return json({ error: 'mews fetch failed' });
  }

  const avails  = data.RoomCategoryAvailabilities || [];
  const comfort = avails.find(a => a.RoomCategoryId === COMFORT_ID);
  if (!comfort) return json({ error: 'no data', detail: data.Message });

  const occList = comfort.RoomOccupancyAvailabilities || [];
  // Index 1 = 2-persoons, index 0 = 1-persoons fallback
  const occ     = occList.length > 1 ? occList[1] : occList[0];
  if (!occ || !occ.Pricing || !occ.Pricing.length) return json({ error: 'no pricing' });

  // Zoek laagste GrossValue over alle nachten in de periode
  let lowestRoom = null;
  for (const p of occ.Pricing) {
    const v = p.Price && p.Price.GrossValue;
    if (v != null && (lowestRoom === null || v < lowestRoom)) lowestRoom = v;
  }
  if (lowestRoom === null) return json({ error: 'no gross value' });

  // Kamerprijs → p.p. prijs (deel door 2 bij 2-persoons occ), afgerond op €0,50
  const ppPrice = ceilHalf(occList.length > 1 ? lowestRoom / 2 : lowestRoom);

  return new Response(JSON.stringify({ price: ppPrice }), {
    status: 200,
    headers: {
      ...CORS,
      'Cache-Control': `public, max-age=${CACHE_SECONDS}`,
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
