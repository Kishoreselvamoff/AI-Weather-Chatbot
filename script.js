// script.js
const goBtn = document.getElementById('goBtn');
const cityInput = document.getElementById('cityInput');
const result = document.getElementById('result');
const status = document.getElementById('status');
const cityName = document.getElementById('cityName');
const desc = document.getElementById('desc');
const temp = document.getElementById('temp');
const icon = document.getElementById('weatherIcon');
const forecastEl = document.getElementById('forecast');
const micBtn = document.getElementById('micBtn');
const locBtn = document.getElementById('locBtn');

async function fetchWeather(city){
  status.textContent = 'Loading...';
  try{
    const res = await fetch('/api/weather', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({city})
    });
    if(!res.ok){
      const err = await res.json();
      status.textContent = 'Error: ' + (err.error || 'City not found');
      return;
    }
    const data = await res.json();
    status.textContent = 'Done';
    showResult(data);
  }catch(e){
    status.textContent = 'Network error';
  }
}

function showResult(data){
  const cur = data.current;
  result.classList.remove('hidden');
  cityName.textContent = cur.name;
  desc.textContent = cur.desc;
  temp.textContent = Math.round(cur.temp) + '°C';
  icon.src = `https://openweathermap.org/img/wn/${cur.icon}@2x.png`;
  // forecast
  forecastEl.innerHTML = '';
  (data.forecast||[]).forEach(d=>{
    const day = document.createElement('div');
    day.className = 'day';
    const date = new Date(d.date).toLocaleDateString();
    day.innerHTML = `<div style="font-weight:600">${date}</div>
                     <img src="https://openweathermap.org/img/wn/${d.icon}@2x.png" style="width:60px"/>
                     <div>${Math.round(d.temp)}°C</div>
                     <div style="color:#9aa8bf">${d.desc}</div>`;
    forecastEl.appendChild(day);
  });
}

// event handlers
goBtn.onclick = ()=> {
  const city = cityInput.value.trim();
  if(!city){ status.textContent = 'Please enter a city'; return; }
  fetchWeather(city);
};
cityInput.onkeydown = (e)=> { if(e.key==='Enter') goBtn.click(); };

// simple geolocation
locBtn.onclick = ()=> {
  if(!navigator.geolocation){ status.textContent='Geolocation unsupported'; return; }
  status.textContent='Getting location...';
  navigator.geolocation.getCurrentPosition(async (pos)=>{
    const {latitude, longitude} = pos.coords;
    // reverse geocode using OpenWeatherMap direct endpoint (supports lat,lon)
    const res = await fetch('/api/weather', {
      method: 'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({city: `${latitude},${longitude}`})
    });
    if(!res.ok){ status.textContent='Location lookup failed'; return; }
    const data = await res.json();
    showResult(data);
  }, ()=> { status.textContent='Permission denied or failed'; });
};

// voice input (speech recognition)
let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.continuous = false;
  recognition.interimResults = false;
  micBtn.onclick = ()=> {
    recognition.start();
    status.textContent = 'Listening...';
  };
  recognition.onresult = (ev)=> {
    const text = ev.results[0][0].transcript;
    cityInput.value = text;
    status.textContent = 'Heard: ' + text;
    fetchWeather(text);
  };
  recognition.onerror = ()=> { status.textContent = 'Voice error'; };
} else {
  micBtn.onclick = ()=> { status.textContent = 'Voice not supported in this browser'; };
}

// snow animation (simple)
(function makeSnow(){
  const s = document.getElementById('snow');
  const flakes = 45;
  for(let i=0;i<flakes;i++){
    const f = document.createElement('div');
    f.className='flake';
    const size = (Math.random()*6)+4;
    f.style.width = f.style.height = size+'px';
    f.style.left = Math.random()*100 + '%';
    f.style.animationDuration = (6+Math.random()*6)+'s';
    f.style.opacity = 0.6*Math.random()+0.2;
    s.appendChild(f);
  }
  const css = document.createElement('style');
  css.innerHTML = `
    #snow .flake{position:fixed; top:-10%; background:linear-gradient(#fff,#bfe); border-radius:50%; z-index:1; pointer-events:none;
      transform:translateY(0); animation-name:fall; animation-timing-function:linear;}
    @keyframes fall{to{transform:translateY(120vh);}}
  `;
  document.head.appendChild(css);
})();
