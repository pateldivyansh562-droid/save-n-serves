// app.js - SaveNServe logic (Backend-connected)

/* UI helpers */
function showToast(msg, time = 2500, isError = false) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.style.position = 'fixed';
    t.style.right = '20px';
    t.style.bottom = '20px';
    t.style.background = isError ? '#d9534f' : 'linear-gradient(90deg,#0ea95d,#d4af37)';
    t.style.color = 'white';
    t.style.padding = '10px 14px';
    t.style.borderRadius = '10px';
    t.style.zIndex = '1000';
    document.body.appendChild(t);
  }
  t.innerText = msg;
  t.style.display = 'block';
  t.style.background = isError ? '#d9534f' : 'linear-gradient(90deg,#0ea95d,#d4af37)';
  setTimeout(() => t.style.display = 'none', time);
}

/**
 * Helper function to send data to the backend.
 * @param {string} endpoint The API endpoint (e.g., '/api/donate')
 * @param {object} data The data object to send.
 * @returns {Promise<object>} The JSON response from the server.
 */
async function postData(endpoint, data) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      // Handle HTTP errors (like 409, 401)
      throw new Error(result.message || 'An error occurred.');
    }
    
    return result;
  } catch (error) {
    console.error(`Error posting to ${endpoint}:`, error);
    showToast(error.message, 3000, true);
    // Re-throw the error so form handlers can react
    throw error;
  }
}

/* render dashboard counters */
async function renderDashboard() {
  const mealsEl = document.getElementById('mealsSaved');
  const donationsEl = document.getElementById('donationsCount');
  const requestsEl = document.getElementById('requestsCount');
  const eventsEl = document.getElementById('eventsCount');

  // Only run if we are on a page with these elements
  if (!mealsEl) return;

  try {
    const response = await fetch('/api/dashboard-stats');
    if (!response.ok) throw new Error('Could not fetch stats');
    
    const stats = await response.json();
    
    if (mealsEl) mealsEl.innerText = stats.mealsSaved || 0;
    if (donationsEl) donationsEl.innerText = stats.donationsCount || 0;
    if (requestsEl) requestsEl.innerText = stats.requestsCount || 0;
    if (eventsEl) eventsEl.innerText = stats.eventsCount || 0;

  } catch (error) {
    console.error("Error fetching dashboard stats:", error);
    // Show 0s as a fallback
    if (mealsEl) mealsEl.innerText = 0;
    if (donationsEl) donationsEl.innerText = 0;
    if (requestsEl) requestsEl.innerText = 0;
    if (eventsEl) eventsEl.innerText = 0;
  }
}

/* bind forms */
function bindForms() {
  // --- Donation Form (donate.html) ---
  const donateForm = document.getElementById('donationForm');
  if (donateForm) {
    donateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        donor: donateForm.donor.value || "Anonymous",
        qty: parseInt(donateForm.qty.value || 0),
        location: donateForm.location.value || "Campus",
      };
      try {
        const result = await postData('/api/donate', data);
        donateForm.reset();
        showToast(result.message);
        renderDashboard(); // Update dashboard stats
      } catch (error) {
        // Error toast is already shown by postData
      }
    });
  }

  // --- Event Donation Form (event_donate.html) ---
  const eventForm = document.getElementById('eventForm');
  if (eventForm) {
    eventForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        organizer: eventForm.organizer.value,
        contact: eventForm.contact.value,
        servings: parseInt(eventForm.servings.value || 0),
        location: eventForm.location.value,
      };
      if (!data.organizer || !data.contact || !data.location || data.servings <= 0) {
        return showToast("Please fill all fields.", 2000, true);
      }
      try {
        const result = await postData('/api/event-donate', data);
        eventForm.reset();
        showToast(result.message);
        renderDashboard(); // Update dashboard stats
      } catch (error) {}
    });
  }

  // --- Request Form (request.html) ---
  const requestForm = document.getElementById('requestForm');
  if (requestForm) {
    requestForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        name: requestForm.name.value,
        org: requestForm.org.value,
        qty: parseInt(requestForm.qty.value || 0),
        location: requestForm.location.value,
      };
       if (!data.name || !data.location || data.qty <= 0) {
        return showToast("Please fill name, quantity, and location.", 2000, true);
      }
      try {
        const result = await postData('/api/request-food', data);
        requestForm.reset();
        showToast(result.message);
        renderDashboard(); // Update dashboard stats
      } catch (error) {}
    });
  }

  // --- Feed Animals Form (feed_animals.html) ---
  const feedForm = document.getElementById('feedForm');
  if (feedForm) {
    feedForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        source: feedForm.source.value,
        qty: feedForm.qty.value,
        location: feedForm.location.value,
      };
      if (!data.source || !data.qty || !data.location) {
        return showToast("Please fill all fields.", 2000, true);
      }
      try {
        const result = await postData('/api/feed-animals', data);
        feedForm.reset();
        showToast(result.message);
      } catch (error) {}
    });
  }

  // --- Signup Form (signup.html) ---
  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        name: signupForm.name.value,
        username: signupForm.username.value,
        password: signupForm.password.value,
        role: signupForm.role.value,
      };
      if (!data.name || !data.username || !data.password) {
         return showToast("Please fill all fields.", 2000, true);
      }
      try {
        const result = await postData('/api/signup', data);
        signupForm.reset();
        showToast(result.message);
        // Redirect to login page on success
        window.location.href = 'login.html';
      } catch (error) {
         // Error toast is shown by postData, e.g., "Username already exists."
      }
    });
  }
  
  // Note: loginForm, contactForm, and contactForm2 are handled
  // by inline scripts in their respective HTML files.
}

/* map init - uses Google Maps JS API if loaded; falls back to static */
function initMap(elementId = 'map') {
  const el = document.getElementById(elementId);
  if (!el) return;
  
  // If Google Maps API available
  if (window.google && google.maps) {
    const map = new google.maps.Map(el, { center: { lat: 28.7041, lng: 77.1025 }, zoom: 12 });
    
    // In a real app, you would fetch marker data from your backend
    const sample = [
      { name: 'HelpingHands NGO', lat: 28.71, lng: 77.11 },
      { name: 'Hope Kitchen', lat: 28.7, lng: 77.09 },
      { name: 'Animal Shelter A', lat: 28.695, lng: 77.12 },
    ];
    
    sample.forEach(s => {
      const m = new google.maps.Marker({ position: { lat: s.lat, lng: s.lng }, map, title: s.name });
      const inf = new google.maps.InfoWindow({ content: `<strong>${s.name}</strong><br/>Demo marker` });
      m.addListener('click', () => inf.open(map, m));
    });
  } else {
    // fallback static message
    el.innerHTML = '<div style="display:grid;place-items:center;height:100%;color:#666">Map not available — set your Google Maps API key in scripts/config.js</div>';
  }
}

/* theme toggle */
function initTheme() {
  const saved = localStorage.getItem('sns_theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved === 'dark' ? 'dark' : 'light');
  const btn = document.getElementById('themeBtn');
  if (btn) btn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('sns_theme', next);
  });
}

/* init */
document.addEventListener('DOMContentLoaded', () => {
  // We no longer need initStorage()
  initTheme();
  bindForms();
  renderDashboard();
  
  // init map if present
  // Delay slightly to ensure config.js can load
  setTimeout(() => initMap('map'), 500);
});