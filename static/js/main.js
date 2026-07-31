function getCookie(name){
  let value = null;
  if (document.cookie && document.cookie !== ''){
    document.cookie.split(';').forEach(cookie=>{
      const c = cookie.trim();
      if (c.substring(0, name.length + 1) === (name + '=')){
        value = decodeURIComponent(c.substring(name.length + 1));
      }
    });
  }
  return value;
}
const csrftoken = getCookie('csrftoken');

document.addEventListener('DOMContentLoaded', function(){
  // Hamburger toggle
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');
  if (hamburger){
    hamburger.addEventListener('click', ()=> navLinks.classList.toggle('open'));
  }

  // Theme toggle — flips instantly on click (optimistic UI), then persists
  // to the session in the background. Works on every page, including
  // logged-out pages like Login/Register, since it never depends on auth.
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn){
    themeBtn.addEventListener('click', function(){
      const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      themeBtn.textContent = next === 'dark' ? '☀ Light' : '🌙 Dark';
      fetch('/toggle-theme/', {method:'POST', headers:{'X-CSRFToken':csrftoken}})
        .then(r=>r.json())
        .then(data=>{
          // Reconcile with the server's session value in case of any drift.
          document.documentElement.setAttribute('data-theme', data.theme);
          themeBtn.textContent = data.theme === 'dark' ? '☀ Light' : '🌙 Dark';
        })
        .catch(()=>{ /* optimistic UI already applied; nothing more to do */ });
    });
  }

  // Password show/hide toggles
  document.querySelectorAll('.toggle-pass').forEach(btn=>{
    btn.addEventListener('click', function(){
      const input = document.getElementById(btn.dataset.target);
      if (input.type === 'password'){
        input.type = 'text'; btn.textContent = 'HIDE';
      } else {
        input.type = 'password'; btn.textContent = 'SHOW';
      }
    });
  });

  // Solved / marked checkboxes (DSA / Aptitude / Technical / Interview)
  document.querySelectorAll('.checkbox-solved').forEach(cb=>{
    cb.addEventListener('change', function(){
      const url = cb.dataset.url;
      fetch(url, {method:'POST', headers:{'X-CSRFToken':csrftoken}})
        .then(r=>r.json())
        .then(data=>{
          const solved = data.solved !== undefined ? data.solved : data.marked;
          cb.checked = solved;
          const row = cb.closest('tr');
          if (row) row.style.opacity = solved ? '0.6' : '1';
        });
    });
  });

  // Calendar heatmap render
  const calEl = document.getElementById('calendar-heatmap');
  const calDataEl = document.getElementById('calendar-data');
  if (calEl && calDataEl){
    try {
      const data = JSON.parse(calDataEl.textContent);
      const totalEl = document.getElementById('calTotal');
      if (totalEl){
        const total = data.reduce((sum, d) => sum + d.count, 0);
        totalEl.textContent = total;
      }
      let weeks = [];
      let currentWeek = [];
      data.forEach((d, i)=>{
        currentWeek.push(d);
        if (currentWeek.length === 7 || i === data.length -1){
          weeks.push(currentWeek);
          currentWeek = [];
        }
      });
      weeks.forEach(week=>{
        const weekDiv = document.createElement('div');
        weekDiv.className = 'cal-week';
        week.forEach(day=>{
          const dayDiv = document.createElement('div');
          dayDiv.className = 'cal-day';
          let level = 0;
          if (day.count > 0) level = 1;
          if (day.count >= 3) level = 2;
          if (day.count >= 6) level = 3;
          if (day.count >= 10) level = 4;
          dayDiv.dataset.level = level;
          dayDiv.title = day.date + ': ' + day.count + ' activities';
          weekDiv.appendChild(dayDiv);
        });
        calEl.appendChild(weekDiv);
      });
    } catch (e) {
      console.error('Voyage Log calendar failed to render:', e);
    }
  }
});
