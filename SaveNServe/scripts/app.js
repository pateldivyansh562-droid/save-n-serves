// app.js - Centralized Frontend Logic

// --- UTILS ---
function showToast(msg, isError=false) {
    let t = document.getElementById('toast');
    if(!t){
        t=document.createElement('div'); t.id='toast';
        document.body.appendChild(t);
        Object.assign(t.style, {position:'fixed',bottom:'20px',right:'20px',padding:'12px 20px',background:isError?'#d32f2f':'#0ea95d',color:'white',borderRadius:'8px',zIndex:9999,transition:'opacity 0.3s',opacity:0});
    }
    t.textContent=msg; t.style.background=isError?'#d32f2f':'#0ea95d'; t.style.opacity=1;
    setTimeout(()=>t.style.opacity=0,3000);
}

async function apiCall(url, method='GET', data=null) {
    try {
        const opts = { method, headers: {'Content-Type':'application/json'} };
        if(data) opts.body = JSON.stringify(data);
        const res = await fetch(url, opts);
        return await res.json();
    } catch(e) {
        console.error(e); return {success:false, message:"Connection error"};
    }
}

// --- AUTO-BIND FORMS ---
document.addEventListener('DOMContentLoaded', () => {
    // Login
    bindForm('loginForm', async (f) => {
        const res = await apiCall('/api/login', 'POST', {username: f.loginUser.value.trim(), password: f.loginPass.value.trim()});
        if(res.success) {
            localStorage.setItem('sns_user', JSON.stringify(res.user));
            window.location.href = 'dashboard.html';
        } else showToast(res.message, true);
    });

    // Signup
    bindForm('signupForm', async (f) => {
        const res = await apiCall('/api/signup', 'POST', {
            name: f.name.value, username: f.username.value, password: f.password.value, role: f.role.value
        });
        if(res.success) { showToast("Success! Please login."); setTimeout(()=>window.location.href='login.html',1500); }
        else showToast(res.message, true);
    });

    // Standard Donation & Request
    bindForm('donationForm', async (f) => handleSub('/api/donate', {donor:f.donor.value, qty:f.qty.value, location:f.location.value}, 'dashboard.html'));
    bindForm('requestForm', async (f) => handleSub('/api/request-food', {name:f.name.value, org:f.org.value, qty:f.qty.value, location:f.location.value}, 'dashboard.html'));
    
    // Other Forms
    bindForm('eventForm', async (f) => handleSub('/api/event', {org:f.organizer.value, contact:f.contact.value, qty:f.servings.value, loc:f.location.value}, 'index.html'));
    bindForm('feedForm', async (f) => handleSub('/api/animal', {src:f.source.value, qty:f.qty.value, loc:f.location.value}, 'index.html'));
    bindForm('contactForm', async (f) => handleSub('/api/feedback', {name:f.cname.value, email:f.cemail.value, msg:f.cmsg.value}));
    bindForm('contactForm2', async (f) => handleSub('/api/feedback', {name:f.name2.value, email:f.email2.value, msg:f.msg2.value}));
});

function bindForm(id, handler) {
    const f = document.getElementById(id);
    if(f) f.addEventListener('submit', (e) => { e.preventDefault(); handler(f); });
}

async function handleSub(url, data, redirect=null) {
    for(let k in data) if(!data[k] && k!=='org' && k!=='email') return showToast("Fill all fields", true);
    const res = await apiCall(url, 'POST', data);
    showToast(res.message, !res.success);
    if(res.success && redirect) setTimeout(()=>window.location.href=redirect, 1500);
}