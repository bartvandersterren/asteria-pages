// functions/api/google-reviews.js
// Proxy voor Google Places API — houdt de API key uit de frontend.
//
// Vereiste env var (Cloudflare Pages → Settings → Environment variables):
//   GOOGLE_PLACES_API_KEY  — Places API key (beperkt tot je domein)
//
// Place ID opzoeken (vervang YOUR_KEY):
//   curl "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Hotel+Asteria+Venray&inputtype=textquery&fields=place_id&key=YOUR_KEY"

const PLACE_ID = 'ChIJke8H2r9rcEcR0dE0LPPV'; // TODO: vervang met echt place_id van Hotel Asteria Venray

export async function onRequest(context) {
  const API_KEY = context.env.GOOGLE_PLACES_API_KEY;

  if (!API_KEY) {
    return new Response(JSON.stringify({ error: 'API key niet geconfigureerd' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const url = 'https://maps.googleapis.com/maps/api/place/details/json'
    + '?place_id=' + PLACE_ID
    + '&fields=rating,user_ratings_total,reviews'
    + '&reviews_sort=most_relevant'
    + '&language=nl'
    + '&key=' + API_KEY;

  let resp, data;
  try {
    resp = await fetch(url);
    data = await resp.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: 'upstream fetch mislukt' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  if (data.status !== 'OK') {
    return new Response(JSON.stringify({ error: data.status }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const result = data.result;
  const payload = {
    rating: result.rating,
    total:  result.user_ratings_total,
    reviews: (result.reviews || []).map(function (r) {
      return {
        author: r.author_name,
        avatar: r.profile_photo_url,
        rating: r.rating,
        text:   r.text,
        time:   r.relative_time_description,
        url:    r.author_url
      };
    })
  };

  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600'
    }
  });
}
