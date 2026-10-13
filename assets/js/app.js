/* MCLab · original static website · no runtime dependencies */
(() => {
  'use strict';
  const D = window.MCLAB_DATA;
  if (!D) { document.getElementById('main').textContent = 'Website data could not be loaded. Please check data/site-data.js.'; return; }
  const C = D.config;
  const isPublished = p => ['Published','Early Access'].includes(p.status);
  const isAccepted = p => isPublished(p) || p.status === 'Accepted';
  // Date-based project status is refreshed at page load, even between deployments.
  const currentDate = new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  D.projects.forEach(p => { if(p.statusMode === 'auto') p.status = currentDate.slice(0,p.start.length) < p.start ? 'Upcoming' : currentDate.slice(0,p.end.length) > p.end ? 'Completed' : 'Ongoing'; });
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeURL = value => {
    const s = String(value || '').trim();
    if (window.MCLAB_SINGLE_PREVIEW && /^data:image\/(?:jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(s)) return s;
    if (!s || /^(?:javascript|data|vbscript):/i.test(s) || /[<>"'\\\x00-\x1f]/.test(s)) return '';
    return /^(?:https?:\/\/|mailto:|tel:|\.?\.?\/|[a-zA-Z0-9_-]+[/.])/.test(s) ? esc(s) : '';
  };
  const isPreview = Boolean(window.MCLAB_SINGLE_PREVIEW);
  const files = {home:'index',people:'people',professor:'professor',research:'research',publications:'publications',projects:'projects',news:'news',join:'join'};
  const titles = {home:'Mobility Control Laboratory · DGIST',people:'People',professor:'Kanghyun Nam',research:'Research',publications:'Publications',projects:'Projects',news:'News & Lab Life',join:'Join Us & Contact'};
  const link = (page, anchor = '') => isPreview ? `#/${page}${anchor ? '/'+anchor : ''}` : `${files[page] || page}.html${anchor ? '#'+anchor : ''}`;
  const ext = (url, label, cls='text-link') => safeURL(url) ? `<a class="${cls}" href="${safeURL(url)}" target="_blank" rel="noopener noreferrer">${label}</a>` : '';
  const arrow = '<span class="arrow" aria-hidden="true">↗</span>';
  const right = '<span class="arrow" aria-hidden="true">→</span>';
  const initial = name => String(name).trim().split(/\s+/).map(x=>x[0]).slice(0,2).join('');
  const glyphs = {
    search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
    close:'<path d="m6 6 12 12M18 6 6 18"/>',
    motion:'<path d="M5 15h26M9 15l4-8h15l4 8v10H7V15m5 10v4m16-4v4M14 7v8m11-8v8"/><circle cx="12" cy="20" r="1.5"/><circle cx="27" cy="20" r="1.5"/><path d="m2 9 3-3-3-3m30 0 3 3-3 3"/>',
    xbywire:'<circle cx="18" cy="18" r="12"/><circle cx="18" cy="18" r="4"/><path d="m14 16-8-3m16 3 8-3m-12 9v8M3 3l4 4m22 22 4 4M29 7l4-4M7 29l-4 4"/>',
    learning:'<circle cx="8" cy="8" r="3"/><circle cx="8" cy="28" r="3"/><circle cx="18" cy="18" r="3"/><circle cx="28" cy="8" r="3"/><circle cx="28" cy="28" r="3"/><path d="m10 10 6 6m4 4 6 6m-16 0 6-6m4-4 6-6M11 8h14M8 11v14m20-14v14M11 28h14"/>',
    teleoperation:'<path d="M7 30h22m-18 0 3-6h8l3 6M5 8h26v16H5z"/><path d="M11 17c4-5 10-5 14 0m-10 3c2-2 4-2 6 0M15 4a8 8 0 0 1 6 0"/>'
  };
  const icon = (name, cls='') => `<svg class="${cls}" viewBox="0 0 ${['motion','xbywire','learning','teleoperation'].includes(name)?36:24} ${['motion','xbywire','learning','teleoperation'].includes(name)?36:24}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${glyphs[name] || glyphs.motion}</svg>`;
  const mark = '<svg viewBox="0 0 30 30" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 22V8l7 10 5-12 5 12 7-10v14"/></svg>';
  const sourceNote = key => key==='publications' ? '<p class="source-note">Publication status is recorded explicitly; submission is not acceptance.</p>' : '';
  const simpleHero = title => `<section class="page-hero simple-page-hero"><div class="container"><h1>${title}</h1></div></section>`;
  const pageHero = (label,title,desc,sub='') => `<section class="page-hero"><div class="container"><div class="eyebrow">${label}</div><h1>${title}</h1><p>${desc}</p>${sub}</div></section>`;
  const sectionHead = (eyebrow,title,extra='') => `<div class="section-header"><div><div class="eyebrow">${eyebrow}</div><h2>${title}</h2></div>${extra}</div>`;
  const tagRow = tags => `<div class="tag-row">${tags.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>`;
  let currentPage='home';
  let visiblePublications=[];
  let activeBib = null;

  function header() {
    const menu = [['home','Home'],['people','People'],['research','Research'],['publications','Publications'],['projects','Projects'],['news','News']];
    $('#masthead').innerHTML = `${isPreview?'<div class="preview-badge"><strong>MCLab · Local preview</strong> All pages are interactive. This file is not a published website.</div>':''}<div class="institution-bar"><div class="container"><a class="institution-name" href="https://www.dgist.ac.kr/" target="_blank" rel="noopener noreferrer"><span class="dgist-type">DGIST</span><span class="divider"></span><span class="department-text">ROBOTICS &amp; MECHATRONICS ENGINEERING</span></a><span class="location">DAEGU, REPUBLIC OF KOREA</span></div></div>`;
    $('#site-header').innerHTML = `<div class="container nav-row"><a class="brand" href="${link('home')}" aria-label="MCLab home"><span class="brand-name">MC<span>Lab</span></span></a><nav id="primary-nav" class="primary-nav" aria-label="Main navigation">${menu.map(([id,label])=>`<a class="nav-link ${currentPage===id || (currentPage==='professor'&&id==='people')?'active':''}" ${currentPage===id?'aria-current="page"':''} href="${link(id)}">${label}</a>`).join('')}</nav><div class="nav-actions"><button class="icon-btn" id="open-search" title="Search this site (/)" aria-label="Search this site">${icon('search')}</button><button class="icon-btn" id="theme-toggle" title="Toggle color theme" aria-label="Toggle dark mode" aria-pressed="false">${icon('sun')}</button><a class="nav-join ${currentPage==='join'?'active':''}" href="${link('join')}">Join us ${right}</a><button class="icon-btn menu-toggle" id="menu-toggle" aria-controls="primary-nav" aria-expanded="false" aria-label="Open navigation menu">${icon('menu')}</button></div></div>`;
    $('#menu-toggle').addEventListener('click',()=>{
      const expanded=$('#menu-toggle').getAttribute('aria-expanded')==='true';
      $('#primary-nav').classList.toggle('open',!expanded);
      $('#menu-toggle').setAttribute('aria-expanded',String(!expanded));
      $('#menu-toggle').setAttribute('aria-label',expanded?'Open navigation menu':'Close navigation menu');
    });
    $('#open-search').addEventListener('click',openSearch);
    $('#theme-toggle').addEventListener('click',()=>{
      const dark=document.documentElement.dataset.theme!=='dark';
      document.documentElement.dataset.theme=dark?'dark':'light';
      $('#theme-toggle').setAttribute('aria-pressed',String(dark));
      try{localStorage.setItem('mclab-theme',dark?'dark':'light');}catch(_){}
    });
    $('#theme-toggle').setAttribute('aria-pressed',String(document.documentElement.dataset.theme==='dark'));
  }
  function footer(){
    const e6Map='https://www.google.com/maps/search/?api=1&query='+encodeURIComponent('DGIST E6 building, 333 Techno Jungang-daero, Daegu, South Korea');
    $('#site-footer').innerHTML=`<div class="container"><div class="footer-compact"><div class="footer-compact-brand"><a class="footer-brand" href="${link('home')}">MC<span>Lab</span></a><span>Mobility Control Laboratory · DGIST</span></div><nav class="footer-compact-nav" aria-label="Footer navigation"><a href="${link('research')}">Research</a><a href="${link('people')}">People</a><a href="${link('publications')}">Publications</a><a href="${link('projects')}">Projects</a><a href="${link('join')}">Join the Team</a></nav><a class="footer-compact-email" href="mailto:${esc(C.email)}">${esc(C.email)} ${arrow}</a></div><div class="footer-location"><div class="footer-location-address"><span lang="ko">우편번호 42988 · 대구광역시 달성군 현풍읍 테크노중앙대로 333, DGIST E6</span><span lang="en">333 Techno Jungang-daero, Hyeonpung-eup, Dalseong-gun, Daegu 42988, Republic of Korea · DGIST E6</span></div><a class="footer-map-link" href="${e6Map}" target="_blank" rel="noopener noreferrer" aria-label="Find DGIST E6 on Google Maps"><span aria-hidden="true">📍</span><span>DGIST E6 · Google Maps</span> ${arrow}</a></div></div>`;
  }
  function motionBoard(){
    if(C.heroImage && safeURL(C.heroImage))return `<div class="photo-hero"><figure class="hero-main-photo"><img class="hero-custom-image" src="${safeURL(C.heroImage)}" alt="${esc(C.heroAlt||'MCLab research platform')}" fetchpriority="high" decoding="async"><figcaption><span>MCLAB · EXPERIMENTAL PLATFORM</span><strong>${esc(C.heroCaption||'Research in motion.')}</strong></figcaption></figure><div class="hero-photo-pair">${(C.heroGallery||[]).map(g=>`<figure><img src="${safeURL(g.image)}" alt="${esc(g.alt||g.title)}" decoding="async"><figcaption>${esc(g.title)}</figcaption></figure>`).join('')}</div></div>`;
    return `<div class="motion-board"><div class="board-top"><span>VEHICLE MOTION INTELLIGENCE</span><span class="research-dot">MCLAB RESEARCH</span></div><svg class="board-svg" viewBox="0 0 500 335" role="img" aria-label="Conceptual illustration of coordinated steering, braking, driving, and suspension around an electric vehicle"><defs><linearGradient id="car-fill" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#d5e4ff"/></linearGradient><linearGradient id="road-fill" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#dbe7fa" stop-opacity=".12"/><stop offset=".5" stop-color="#b9cdef" stop-opacity=".3"/><stop offset="1" stop-color="#dbe7fa" stop-opacity=".12"/></linearGradient><filter id="car-shadow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="10" stdDeviation="9" flood-color="#284d91" flood-opacity=".15"/></filter></defs><path d="M-30 326C159 238 290 333 550-15" stroke="url(#road-fill)" stroke-width="127" fill="none"/><path d="M-50 332C135 247 285 343 555-18" stroke="#9ab5e0" stroke-width="1.2" fill="none" stroke-dasharray="7 7"/><path d="M11 268C170 203 302 249 478 12" stroke="#6688c0" opacity=".24" stroke-width="1" fill="none"/><path d="M64 348C242 283 355 283 530 45" stroke="#6688c0" opacity=".24" stroke-width="1" fill="none"/><circle cx="257" cy="164" r="126" fill="none" stroke="#a1b9e1" stroke-dasharray="3 6" opacity=".8"/><circle cx="257" cy="164" r="100" fill="none" stroke="#c6d6ef"/><path d="M154 233C191 226 251 172 269 114S302 28 325 8" fill="none" stroke="#2f67e7" stroke-width="2.5" stroke-dasharray="5 5"/><g transform="translate(249 165) rotate(26)" filter="url(#car-shadow)"><rect x="-45" y="-56" width="13" height="33" rx="4" fill="#244d92"/><rect x="32" y="-56" width="13" height="33" rx="4" fill="#244d92"/><rect x="-45" y="38" width="13" height="33" rx="4" fill="#244d92"/><rect x="32" y="38" width="13" height="33" rx="4" fill="#244d92"/><path d="M-35 61V-57Q-35-86-16-91h32q19 5 19 34V61Q34 84 19 89h-38q-15-5-16-28Z" fill="url(#car-fill)" stroke="#6d94d8" stroke-width="1.5"/><path d="M-25-36q25-9 50 0l-7 29h-36Z" fill="#aec8ed" stroke="#7fa6db"/><path d="M-20 9h40v40h-40Z" fill="#e8f1ff" stroke="#b5ccef"/><path d="m-18 53-5 19q23 7 46 0l-5-19Z" fill="#a8c3e9" stroke="#7fa6db"/><path d="M-27-69h11m32 0h11M-29 4v41m58-41v41" stroke="#4077d3" stroke-width="2" stroke-linecap="round"/><path d="M-28-21H28M-28 54H28" stroke="#3165c9" stroke-dasharray="3 3"/><circle r="8" cy="17" fill="#2e65de"/><path d="M-3 17h6m-3-3v6" stroke="white" stroke-width="1.3"/></g><g font-family="Arial,sans-serif"><g transform="translate(25 51)"><rect width="128" height="46" rx="9" fill="white" stroke="#d1ddf0"/><circle cx="20" cy="23" r="7" fill="#eaf0ff" stroke="#83a6e7"/><path d="M16 23h8m-4-4v8" stroke="#3366ce"/><text x="36" y="20" font-size="9" font-weight="700" fill="#1b355f">STEERING</text><text x="36" y="34" font-size="8" fill="#6d809e">Shape the response</text></g><g transform="translate(355 78)"><rect width="127" height="46" rx="9" fill="white" stroke="#d1ddf0"/><circle cx="20" cy="23" r="7" fill="#eaf0ff" stroke="#83a6e7"/><circle cx="20" cy="23" r="3" fill="none" stroke="#3366ce"/><text x="36" y="20" font-size="9" font-weight="700" fill="#1b355f">BRAKING</text><text x="36" y="34" font-size="8" fill="#6d809e">Maintain stability</text></g><g transform="translate(14 232)"><rect width="129" height="46" rx="9" fill="white" stroke="#d1ddf0"/><path d="m21 11-7 12h6l-1 11 8-14h-6Z" fill="#dce8ff" stroke="#5f8cd5"/><text x="36" y="20" font-size="9" font-weight="700" fill="#1b355f">DRIVING</text><text x="36" y="34" font-size="8" fill="#6d809e">Deliver the motion</text></g><g transform="translate(351 245)"><rect width="137" height="46" rx="9" fill="white" stroke="#d1ddf0"/><path d="m21 12-6 5 10 5-10 5 6 6" fill="none" stroke="#668ed4" stroke-width="1.5"/><text x="36" y="20" font-size="9" font-weight="700" fill="#1b355f">SUSPENSION</text><text x="36" y="34" font-size="8" fill="#6d809e">Balance the ride</text></g></g><g stroke="#91afde" stroke-width="1" fill="none"><path d="m153 75 24 4 18 25"/><path d="m355 101-37 7-11 17"/><path d="m143 253 31-9 15-21"/><path d="m351 267-32-10-18-29"/></g><g fill="#2964e3"><circle cx="195" cy="104" r="3"/><circle cx="307" cy="125" r="3"/><circle cx="189" cy="223" r="3"/><circle cx="301" cy="228" r="3"/></g></svg><div class="board-bottom"><div><span>OUR APPROACH</span><br><strong>Physics-informed. Data-enabled.</strong></div><span style="font-size:23px;color:#3168de;letter-spacing:-2px" aria-hidden="true">↗</span></div></div><p class="board-caption">Conceptual research illustration · not experimental data</p>`;
  }
  function researchCards(){return `<div class="research-grid">${D.research.map(r=>`<a class="research-card" href="${link('research',r.id)}"><div class="research-card-top">${icon(r.id==='motion'?'motion':r.id==='xbywire'?'xbywire':r.id==='learning'?'learning':'teleoperation','research-icon')}<span class="num">${esc(r.number)}</span></div><h3>${esc(r.title)}</h3><p>${esc(r.description)}</p><div class="card-bottom"><span>EXPLORE RESEARCH</span>${arrow}</div></a>`).join('')}</div>`;}
  function paperArt(index){
    const inner=[
      '<path d="M10 55c25 0 20-40 45-40s20 65 45 65 20-50 45-50 20 35 45 35 22-45 46-45"/><path d="M10 61c25 0 20-39 45-39s20 64 45 64 20-48 45-48 20 36 45 36 22-45 46-45" opacity=".35" stroke-dasharray="3 4"/><path d="M14 86h220M14 8v78" stroke-width="1" opacity=".35"/>',
      '<g><path d="m35 20 53 24-53 25m0-25 53-24m-53 49 53-25m0 0 58-24-58 49 58-25m0-24 55 24-55 25" stroke-width="1" opacity=".6"/><circle cx="35" cy="20" r="5"/><circle cx="35" cy="44" r="5"/><circle cx="35" cy="69" r="5"/><circle cx="88" cy="20" r="5"/><circle cx="88" cy="44" r="5"/><circle cx="88" cy="69" r="5"/><circle cx="146" cy="20" r="5"/><circle cx="146" cy="44" r="5"/><circle cx="146" cy="69" r="5"/><circle cx="201" cy="44" r="7"/></g>',
      '<path d="M14 78h223M14 7v71" stroke-width="1" opacity=".4"/><path d="M15 61c33-37 34 33 65-10s30 15 56-12 50 33 92-12" opacity=".35" stroke-width="13"/><path d="M15 61c33-37 34 33 65-10s30 15 56-12 50 33 92-12"/><path d="M15 65c33-31 34 29 65-10s30 11 56-12 50 27 92-10" stroke-dasharray="3 4" stroke-width="1"/>'
    ][index%3];
    return `<div class="paper-art" aria-hidden="true"><svg viewBox="0 0 250 96" fill="none" stroke="currentColor" stroke-width="2.2">${inner}</svg></div>`;
  }
  function paperLinks(p){
    return `<div class="paper-links">${p.doi?ext('https://doi.org/'+p.doi,'Publisher '+arrow,'resource-btn'):''}${p.pdf?ext(p.pdf,'PDF '+arrow,'resource-btn'):''}${p.url?ext(p.url,'Paper '+arrow,'resource-btn'):''}${p.video?ext(p.video,'Video '+arrow,'resource-btn'):''}${p.code?ext(p.code,'Code '+arrow,'resource-btn'):''}${p.project?ext(p.project,'Project '+arrow,'resource-btn'):''}${isPublished(p)?`<button class="resource-btn" data-bib="${esc(p.id)}" aria-label="View BibTeX for ${esc(p.title)}">BibTeX</button>`:''}</div>`;
  }
  function selectedPapers(){return `<div class="selected-grid">${D.publications.filter(p=>p.featured&&isPublished(p)).slice(0,3).map((p,i)=>`<article class="selected-card">${p.image&&safeURL(p.image)?`<div class="selected-image"><img loading="lazy" src="${safeURL(p.image)}" alt="Research illustration for ${esc(p.title)}"></div>`:paperArt(i)}<div class="selected-body"><div><span class="pill">${esc(p.year)} &nbsp;·&nbsp; ${esc(p.type)}</span></div><h3><a href="${link('publications',p.id)}">${esc(p.title)}</a></h3><div class="venue">${esc(p.venue)}</div>${paperLinks(p)}</div></article>`).join('')}</div>`;}
  function cta(){return `<section class="section compact"><div class="container"><div class="cta-band"><div><h2>Great ideas move better together.</h2><p>We welcome curious students, researchers, and collaborators working toward the next generation of mobility.</p></div><a class="btn btn-light" href="${link('join')}">Join MCLab ${right}</a></div></div></section>`;}
  function missionSection(){return `<section class="section soft mission-section"><div class="container mission-grid"><div><div class="eyebrow">ABOUT MCLAB</div><h2>Control technologies.<br>Real mobility.</h2><span class="pill">${esc(C.jointLab)}</span></div><div><p class="mission-copy">${esc(C.mission)}</p><p class="mission-ko" lang="ko">${esc(C.missionKo)}</p><div class="mission-stats"><span><strong>${(D.researchPrograms||[]).length}</strong> research programs</span><span><strong>${(D.researchTopics||[]).length}</strong> research themes</span></div></div></div></section>`;}
  function home(){
    // Home news: a photo-led editorial stream, preserving original lab images.
    // Intentionally exclude lab-team, which was removed from the homepage by request.
    const photos=['tsinghua-exchange','conference-moments','spring-gathering','graduation-moments','winter-workshop'];
    const gallery=photos.map(id=>D.gallery.find(g=>g.id===id)).filter(g=>g&&safeURL(g.image));
    const newsCaptions={
      'tsinghua-exchange':'Sharing ideas and building international research connections.',
      'conference-moments':'Presenting our research and connecting with the automotive engineering community.',
      'spring-gathering':'Growing stronger together through moments beyond the lab.',
      'graduation-moments':'Celebrating milestones and the people behind our research.',
      'winter-workshop':'Exchanging ideas and strengthening teamwork beyond everyday research.',
      'vehicle-testing':'Bringing vehicle control research closer to real-world mobility.'
    };
    const newsGallery=gallery.map(g=>`<a class="home-news-photo" href="${link('news',g.id)}"><img src="${safeURL(g.image)}" alt="${esc(g.alt||g.title)}" loading="lazy"><span class="home-news-caption"><strong>${esc(g.title)}</strong><small>${esc(newsCaptions[g.id]||g.text||g.title)}</small></span></a>`).join('');
    return `<section class="hero philosophy-home video-home"><video class="home-background-video" autoplay muted loop playsinline preload="metadata" aria-hidden="true" tabindex="-1" onerror="this.style.display=\'none\'"><source src="assets/video/gemini_generated_video.mp4" type="video/mp4"></video><div class="home-video-shade" aria-hidden="true"></div><div class="container philosophy-hero-inner">
      <div class="philosophy-kicker">DGIST · MOBILITY CONTROL LABORATORY</div>
      <h1>Intelligence<br><span>in motion.</span></h1>
      <p class="philosophy-lead">Engineering safer, smarter, and more efficient mobility.</p>
      <p class="philosophy-statement">We unite <strong>vehicle dynamics</strong>, <strong>intelligent control</strong>, and <strong>AI</strong> to turn physical insight into reliable motion — from electrified chassis systems to next-generation mobility.</p>
      <div class="philosophy-actions"><a class="btn" href="${link('research')}">Explore our research ${arrow}</a><a class="btn btn-outline" href="${link('people')}">Meet MCLab ${right}</a></div>
      <div class="philosophy-section-label">MCLAB PHILOSOPHY</div>
      <div class="philosophy-values philosophy-pillars philosophy-minimal" aria-label="MCLab research, education and social philosophy">
        <div class="philosophy-pillar"><span class="pillar-label">RESEARCH</span><strong>Physics Meets Intelligence.</strong><p lang="ko">물리와 AI의 융합으로 미래 모빌리티 혁신</p></div>
        <div class="philosophy-pillar"><span class="pillar-label">EDUCATION</span><strong>Learn by Doing.</strong><p lang="ko">실험과 도전을 통한 연구역량 성장</p></div>
        <div class="philosophy-pillar"><span class="pillar-label">SOCIAL</span><strong>Respect &amp; Collaboration.</strong><p lang="ko">존중과 협력으로 실질적 가치 창출</p></div>
      </div>
    </div></section>
    <section class="section home-news-notice"><div class="container home-news-notice-grid">
      <div class="home-news-column"><div class="home-column-heading"><h2>MCLab NEWS</h2><a href="${link('news')}">View all ${right}</a></div>
        <div class="home-news-gallery">${newsGallery||'<p>News and lab photographs will be posted here.</p>'}</div>
      </div>
      <div class="home-notice-column"><div class="home-column-heading"><h2>NOTICE</h2><a href="${link('join')}">Join us ${right}</a></div>
        <article class="home-notice-card"><span class="notice-category">RECRUITMENT · 연구원 모집</span>
          <h3>Join MCLab</h3><p class="recruitment-closed" role="status">2027년 봄학기 모집 완료 <span lang="en">· Spring 2027 Recruitment Closed</span></p>
          <div class="recruitment-language" lang="ko">
            <p><strong>모집 대상</strong> · 학부연구생, 석사 및 박사과정 학생</p>
            <p><strong>연구 분야</strong> · X-by-Wire, 통합 차량 모션제어, AI 기반 모델링·제어, Mobility AI</p>
            <p><strong>연구 지원</strong> · 장학금·연구장려금(지원 자격 및 재원에 따름), 산학협력 및 국제학회 참여 기회</p>
            <p><strong>지원 방법</strong> · 이력서 또는 간단한 연구계획서를 이메일로 제출</p>
          </div>
          <div class="recruitment-language recruitment-language-en" lang="en">
            <p><strong>Positions</strong> · Undergraduate interns, M.S. and Ph.D. students</p>
            <p><strong>Research</strong> · X-by-Wire, integrated motion control, AI-assisted modeling and control, Mobility AI</p>
            <p><strong>Support</strong> · Scholarships and stipends (subject to eligibility and funding), industry collaboration and international conferences</p>
            <p><strong>Apply</strong> · Email your CV or brief research statement</p>
          </div>
          <p class="home-notice-contact"><strong>✉</strong> <a href="mailto:khnam@dgist.ac.kr">khnam@dgist.ac.kr</a></p>
          <div class="home-recruitment-video"><video autoplay muted loop playsinline preload="metadata" aria-label="MCLab mobility research demonstration video"><source src="assets/video/MCLab.mp4" type="video/mp4"></video></div>
          <a class="text-link" href="${link('join')}"><span class="application-click-icon" aria-hidden="true">👆</span> Application &amp; details ${right}</a>
        </article>
      </div>
    </div></section>`;
  }
  function piCard(full=false){
    return `<article class="pi-feature"><div class="profile-art">${D.pi.photo&&safeURL(D.pi.photo)?`<img src="${safeURL(D.pi.photo)}" alt="${esc(D.pi.name)}">`:`<span class="profile-initials">KN</span><span class="portrait-label">MCLAB · PRINCIPAL INVESTIGATOR</span>`}</div><div><span class="pill">PRINCIPAL INVESTIGATOR</span><h2>${esc(D.pi.name)}<span class="pi-degree">, Ph.D.</span><span class="ko-name" lang="ko">${esc(D.pi.nameKo)}</span></h2><p>${esc(D.pi.role)} · DGIST<br>${esc(C.department)}</p>${tagRow(D.pi.interests)}<div class="button-row">${!full?`<a class="btn small" href="${link('professor')}">Faculty profile ${right}</a>`:''}<a class="btn btn-outline small" href="mailto:${esc(D.pi.email)}"><span aria-hidden="true">✉️</span> ${esc(D.pi.email)} ${arrow}</a><a class="btn btn-outline small" href="https://scholar.google.com/citations?user=5tYGteAAAAAJ" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">🎓</span> Google Scholar ${arrow}</a></div></div></article>`;
  }
  function people(){
    const groups=[...new Set(D.people.map(p=>p.group))];
    return `${simpleHero('OUR TEAM')}<section class="section"><div class="container">${piCard()}${groups.map((group,i)=>{const ps=D.people.filter(p=>p.group===group);return `<section class="people-section" id="group-${i}"><h2>${esc(group)}</h2><div class="people-grid">${ps.map(p=>`<article class="person-card" id="${esc(p.id)}"><div class="person-art">${p.photo&&safeURL(p.photo)?`<img loading="lazy" src="${safeURL(p.photo)}" alt="${esc(p.name)}">`:`<span class="initials" aria-hidden="true">${esc(initial(p.name))}</span>`}</div><div class="person-body"><h3>${esc(p.name)}</h3>${p.nameKo?`<p class="person-name-ko" lang="ko">${esc(p.nameKo)}</p>`:''}<p class="person-role">${esc(p.id==="wonchang-yang"?"Integrated M.S.–Ph.D. Student":p.role.replace(/^Ph\.D\. Candidate$/,"Ph.D. Student").replace(/^Undergraduate Intern \(\d+(?:st|nd|rd|th) year\)$/,"Undergraduate Intern"))}</p><p class="person-interest">${esc(p.interest)}</p>${p.joined||p.graduated?`<p class="person-dates">${p.joined?'Joined '+esc(p.joined):''}${p.joined&&p.graduated?' · ':''}${p.graduated?'Graduated '+esc(p.graduated):''}</p>`:''}${p.affiliation?`<p class="person-affiliation">${esc(p.affiliation)}</p>`:''}${p.website?ext(p.website,'Profile '+arrow,'person-email'):''}${p.email?`<a class="person-email" href="mailto:${esc(p.email)}"><span class="person-mail-icon" aria-hidden="true">✉</span><span>${esc(p.email)}</span></a>`:''}</div></article>`).join('')}</div></section>`;}).join('')}</div></section>${cta()}`;
  }
  function cvRows(arr,kind){return arr.map(a=>`<div class="cv-line"><div class="cv-year">${esc(a.year||a.period)}</div><div><h3>${esc(a.degree||a.role||a.title)}</h3><p>${esc(a.school||a.org||a.detail||'')}${a.school&&a.detail?'<br>'+esc(a.detail).replace(/\n/g,'<br>'):''}</p></div></div>`).join('');}
  function professor(){return `${pageHero('PRINCIPAL INVESTIGATOR',esc(D.pi.name),esc(D.pi.role)+' · '+esc(C.department)+', DGIST')}<section class="section"><div class="container">${piCard(true)}<div class="faculty-contact"><span>🏢 Office ${esc(C.office)} · Lab ${esc(C.labRoom)}</span><a href="tel:${esc(C.phone)}">📞 Tel. ${esc(C.phone)}</a><a href="mailto:${esc(C.email)}">✉️ E-mail 1: ${esc(C.email)}</a>${C.secondaryEmail?`<a href="mailto:${esc(C.secondaryEmail)}">✉️ E-mail 2: ${esc(C.secondaryEmail)}</a>`:''}</div><div class="profile-grid"><section><h2>Education</h2>${cvRows(D.pi.education)}</section><section><h2>Academic &amp; industry experience</h2>${cvRows(D.pi.experience)}</section><section><h2>Editorial service</h2>${cvRows(D.pi.service)}<h3 class="subsection-title">Journal reviewing</h3><ul class="reviewer-list">${(D.pi.reviewing||[]).map(j=>`<li>${esc(j)}</li>`).join('')}</ul></section><section><h2>Honors &amp; laboratory milestones</h2>${cvRows(D.pi.awards)}</section></div>${sourceNote('people')}</div></section>`;}
  function research(){
    const programs=D.researchPrograms||[], topics=D.researchTopics||[];
    return `${pageHero('RESEARCH','<span class="research-hero-headline">AI-Assisted Modeling,<br>Control &amp; Learning<br><em>for Mobility.</em></span>','Physics-informed intelligence for vehicle dynamics, electrified chassis systems, and autonomous mobility.',`<nav class="subnav" aria-label="Research programs">${programs.map(g=>`<a href="${link('research',g.id)}">${esc(g.titleKo)}</a>`).join('')}</nav>`)}<section class="section integrated-framework-feature"><div class="container">
      <div class="framework-heading"><span class="framework-index">01 · FEATURED RESEARCH</span><h2>Integrated Motion Control Framework</h2>
      <p>Our integrated vehicle motion control architecture combines driver intent and road preview with physics-informed, AI-assisted control. Vehicle-level force and moment demands are generated through feedforward and conditional feedback control, optimally allocated across steering, driving, braking and suspension, and tracked by robust actuator controllers. Vehicle-state estimation closes the loop to support safe, efficient and responsive mobility.</p></div>
      <figure class="framework-figure"><img src="assets/images/research/integrated-motion-control-framework.png" alt="MCLab integrated motion control framework: driver input, motion preview, motion reference, feedforward and feedback, optimal allocation, robust actuation and vehicle state estimation" loading="eager" onerror="this.closest('figure').style.display='none'"><figcaption>MCLab · Integrated Motion Control Framework</figcaption></figure>
      <div class="framework-points"><span>Motion preview &amp; reference</span><span>AI-assisted control</span><span>Optimal actuator allocation</span><span>Robust real-time actuation</span></div>
      </div></section><section class="section"><div class="container">${programs.map(g=>`<section class="research-program" id="${esc(g.id)}"><div class="program-heading"><span class="program-number">${esc(g.number)}</span><div><h2>${esc(g.title)}</h2><p class="program-ko" lang="ko">${esc(g.titleKo)}</p><p>${esc(g.description)}</p></div></div><div class="topic-grid">${topics.filter(t=>t.program===g.id).map(t=>`<article class="topic-card" id="${esc(t.id)}">${t.image?`<button type="button" class="research-image-button" data-image-open="${safeURL(t.image)}" data-image-title="${esc(t.title)}" aria-label="Enlarge research image: ${esc(t.title)}"><img loading="lazy" class="topic-image" src="${safeURL(t.image)}" alt="${esc(t.title)}"><span>View image <span aria-hidden="true">↗</span></span></button>`:''}<h3>${esc(t.title)}</h3><p>${esc(t.description)}</p>${t.video?ext(t.video,'Research video '+arrow):''}</article>`).join('')}</div></section>`).join('')}</div></section>${cta()}`;
  }
  function publications(){
    const years=[...new Set(D.publications.map(p=>p.year).filter(Boolean))].sort((a,b)=>b-a);
    return `${simpleHero('PUBLICATIONS')}<section class="section"><div class="container"><div class="toolbar publications-toolbar"><label class="search-field"><span class="field-label">Search publications</span><input type="search" class="input" id="pub-search" placeholder="Title, author, venue, or keyword" aria-controls="pub-results"></label><label><span class="field-label">Year</span><select class="select" id="pub-year"><option value="all">All years</option>${years.map(y=>`<option value="${y}">${y}</option>`).join('')}<option value="none">Not assigned</option></select></label><label class="type-field"><span class="field-label">Publication type</span><select class="select" id="pub-type"><option value="all">All types</option><option>Journal</option><option>Conference</option></select></label><label><span class="field-label">Affiliation period</span><select class="select" id="pub-era"><option value="all">All periods</option><option>DGIST</option><option>Before DGIST</option></select></label><div class="publication-toolbar-actions"><button class="resource-btn" id="export-bib" type="button">Export filtered BibTeX ↓</button></div></div><div id="pub-results"></div></div></section>`;
  }
  function jcrBadge(p){
    if(p.type!=='Journal'||!isPublished(p)||Number(p.year)!==2026)return '';
    // Display only supplied ranking annotations. Do not infer JCR quartiles from journal names.
    const source=(p.sourceRanking||'').trim();
    const pct=source.match(/JCR\s*Top\s*(\d+(?:\.\d+)?)\s*%/i);
    if(pct){
      const value=Number(pct[1]);
      if(value<=5)return ` <strong class="pub-jcr pub-jcr-top">(JCR Top ${esc(pct[1])}%)</strong>`;
      if(value<=25)return ' <strong class="pub-jcr">(JCR Q1)</strong>';
      if(value<=50)return ' <strong class="pub-jcr">(JCR Q2)</strong>';
      return '';
    }
    const quartile=source.match(/JCR\s*(Q[12])\b/i);
    return quartile?` <strong class="pub-jcr">(JCR ${esc(quartile[1].toUpperCase())})</strong>`:'';
  }
  function pubRows(ps){
    // Number published papers separately for each publication year.
    // Reverse source order within a year so the oldest listed paper starts at 1.
    const publicationNumbers=new Map();
    const papersByYear=new Map();
    D.publications.filter(isPublished).forEach(p=>{
      const year=String(p.year||'Undated');
      if(!papersByYear.has(year))papersByYear.set(year,[]);
      papersByYear.get(year).push(p);
    });
    papersByYear.forEach(papers=>papers.reverse().forEach((p,i)=>publicationNumbers.set(p.id,i+1)));
    const groups=new Map();
    ps.forEach(p=>{const key=isPublished(p)?String(p.year||'Undated'):(p.status==='Accepted'?'Accepted · forthcoming':p.status==='Preprint'?'Preprints':'Work in Progress');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p);});
    return [...groups].map(([year,rows])=>`<div class="pub-year"><h2>${esc(year)}</h2></div>${rows.map(p=>`<article class="pub-row ${!isPublished(p)&&!['Accepted','Preprint'].includes(p.status)?'pub-row-wip':''}" id="${esc(p.id)}"><div><div class="pub-meta">${isPublished(p)?'':`<span class="pill amber">${esc(['Under review','Submitted','In preparation'].includes(p.status)?'Under review':p.status)}</span>`}<span class="pill pub-type-badge ${p.type==='Journal'?'pub-type-journal':p.type==='Conference'?'pub-type-conference':'neutral'}">${esc(p.type)}</span>${p.era==='Before DGIST'?'<span class="pill neutral">Before DGIST</span>':''}${!isPublished(p)&&p.year?`<span class="pill neutral">${p.year}</span>`:''}</div><h3>${isPublished(p)?`<span class="pub-title-number">[${publicationNumbers.get(p.id)}]</span> `:''}${esc(p.title)}</h3><p class="pub-authors">${esc(p.authors).replace(/K\. H\. Nam\*?/g,m=>`<strong>${m}</strong>`)}</p><div class="pub-venue">${esc(p.venue)}${p.details?' · '+esc(p.details):''}${isPublished(p)&&p.year?' · '+p.year:''}${jcrBadge(p)}</div>${p.image&&safeURL(p.image)?`<img class="publication-image" src="${safeURL(p.image)}" alt="Research illustration for ${esc(p.title)}" loading="lazy">`:''}${paperLinks(p)}</div></article>`).join('')}`).join('');
  }
  function setupPubs(anchor){
    let status='all';
    const target=D.publications.find(p=>p.id===anchor);if(target)status='all';
    const update=()=>{
      const q=$('#pub-search').value.trim().toLocaleLowerCase();
      const y=$('#pub-year').value,t=$('#pub-type').value,era=$('#pub-era').value;
      visiblePublications=D.publications.filter(p=>(status==='all'||(status==='Published'?isPublished(p):p.status===status))&&(y==='all'||(y==='none'?!p.year:String(p.year)===y))&&(t==='all'||p.type===t)&&(era==='all'||p.era===era)&&(!q||[p.title,p.authors,p.venue,p.doi,p.status].join(' ').toLocaleLowerCase().includes(q)));
      
      $('#pub-results').innerHTML=visiblePublications.length?pubRows(visiblePublications):'<div class="empty-state"><h3>No matching publications</h3><p>Try another keyword, year, type, or status.</p><button class="btn small" id="reset-pubs">Reset filters</button></div>';
      
      $$('[data-pub-status]').forEach(b=>{b.classList.toggle('active',b.dataset.pubStatus===status);b.setAttribute('aria-pressed',String(b.dataset.pubStatus===status));});
      $('#reset-pubs')?.addEventListener('click',()=>{$('#pub-search').value='';$('#pub-year').value='all';$('#pub-type').value='all';$('#pub-era').value='all';status='all';update();});
    };
    $$('[data-pub-status]').forEach(b=>b.addEventListener('click',()=>{status=b.dataset.pubStatus;update();}));
    ['#pub-search','#pub-year','#pub-type','#pub-era'].forEach(s=>$(s).addEventListener(s==='#pub-search'?'input':'change',update));
    $('#export-bib').addEventListener('click',()=>{
      if(!visiblePublications.length){$('#pub-count').textContent='There are no records to export. Adjust the filters first.';return;}
      downloadText(visiblePublications.map(toBib).join('\n\n'),'mclab-publications.bib','application/x-bibtex');
    });update();
  }
  function projects(){return `${simpleHero('PROJECTS')}<section class="section"><div class="container"><div class="toolbar project-toolbar"><label><span class="field-label">Search projects</span><input type="search" class="input" id="project-search" placeholder="Project title, sponsor, or keyword"></label><label><span class="field-label">Funding category</span><select class="select" id="project-category"><option value="all">All categories</option><option>Government</option><option>Industry</option><option>Institutional</option></select></label></div><div class="filter-row"><div class="filter-buttons" role="group" aria-label="Project status">${['Ongoing','Completed'].map((s,i)=>`<button class="filter-button ${i===0?'active':''}" data-project-status="${s}" aria-pressed="${i===0}">${s==='all'?'All projects':s}</button>`).join('')}</div><span class="result-count" id="project-count" role="status" aria-live="polite"></span></div><div class="project-grid" id="project-results"></div></div></section>`;}
  function projectCards(ps){return ps.map(p=>`<article class="project-card project-editorial ${p.category==='Industry'?'project-industry':'project-government'}" id="${esc(p.id)}">
    <div class="project-top"><span class="project-code ${p.category==='Industry'?'project-code-industry':'project-code-government'}">${esc(p.category==='Industry'?'Industry':'Government')}</span><span class="pill ${p.status==='Ongoing'?'green':p.status==='Upcoming'?'amber':'neutral'} ${p.category==='Industry'&&(p.status==='Ongoing'||p.status==='Upcoming')?'industry-active-status':''}">${esc(p.status)}</span></div>
    <h3>${esc(p.title)}</h3>

    <dl class="project-facts">
      <div><dt>Role</dt><dd>${esc(p.category==='Industry'||p.id==='g1'||p.id==='g6'?'PI':'Co-PI')}</dd></div>
      <div><dt>Period</dt><dd>${esc(p.start.replace('-','.'))} – ${esc(p.end.replace('-','.'))}</dd></div>
      <div><dt>Funding Source</dt><dd>${esc(p.funder)}</dd></div>
    </dl>
    ${p.summary?`<p class="project-summary">${esc(p.summary)}</p>`:''}
    ${p.attachment||p.url?`<div class="paper-links">${p.attachment?ext(p.attachment,'Public summary · PDF '+arrow,'resource-btn'):''}${p.url?ext(p.url,'Project link '+arrow,'resource-btn'):''}</div>`:''}
  </article>`).join('');}
  function setupProjects(anchor){
    let status=D.projects.find(p=>p.id===anchor)?.status==='Completed'?'Completed':'Ongoing';
    const update=()=>{const q=$('#project-search').value.toLocaleLowerCase().trim(),cat=$('#project-category').value;const ps=D.projects.filter(p=>(status==='all'||(status==='Completed'?p.status==='Completed':p.status!=='Completed'))&&(cat==='all'||p.category===cat)&&(!q||[p.title,p.funder,p.code].join(' ').toLocaleLowerCase().includes(q))).sort((a,b)=>{const rank={Government:0,Institutional:1,Industry:2};return (rank[a.category]??3)-(rank[b.category]??3)});$('#project-results').innerHTML=ps.length?projectCards(ps):'<div class="empty-state" style="grid-column:1/-1"><h3>No matching projects</h3><p>Try another keyword, category, or status.</p></div>';$('#project-count').textContent=`${ps.length} project${ps.length===1?'':'s'} shown`;$$('[data-project-status]').forEach(b=>{b.classList.toggle('active',b.dataset.projectStatus===status);b.setAttribute('aria-pressed',String(b.dataset.projectStatus===status));});};
    $$('[data-project-status]').forEach(b=>b.addEventListener('click',()=>{status=b.dataset.projectStatus;update();}));$('#project-search').addEventListener('input',update);$('#project-category').addEventListener('change',update);update();
  }
  function news(){return `${pageHero('NEWS & LAB LIFE','A lab is more than its research.','Milestones, new beginnings, and moments shared by the MCLab community.')}<section class="section"><div class="container">${[...D.news].sort((a,b)=>b.date.localeCompare(a.date)).map(n=>`<article class="timeline-item" id="${esc(n.id)}"><span class="pill">${esc(n.tag||'Lab news')}</span><time class="news-date" datetime="${esc(n.date)}">${esc(n.date)}</time><h2>${esc(n.title)}</h2>${n.image?`<img class="news-image" src="${safeURL(n.image)}" alt="${esc(n.title)}" loading="lazy">`:''}<p>${esc(n.text)}</p>${n.source?ext(n.source,'Original announcement '+arrow):''}</article>`).join('')}<div style="margin-top:22px">${sectionHead('MOMENTS TOGETHER','Lab gallery.')}${D.gallery.length?`<div class="gallery-grid">${[...D.gallery].filter(g=>safeURL(g.image)).reverse().sort((a,b)=>(b.date||'').localeCompare(a.date||'')).map(g=>`<figure class="gallery-card" id="${esc(g.id)}"><button type="button" class="gallery-image-button" data-image-open="${safeURL(g.image)}" data-image-title="${esc(g.title)}" aria-label="Enlarge photo: ${esc(g.title)}"><img loading="lazy" src="${safeURL(g.image)}" alt="${esc(g.alt||g.title)}"></button><figcaption><strong>${esc(g.title)}</strong>${g.date?`<time datetime="${esc(g.date)}"> · ${esc(g.date)}</time>`:''}<p>${esc(g.text||g.alt||g.title)}</p></figcaption></figure>`).join('')}</div>`:`<div class="callout">Original photo albums are available on the previous lab website. ${ext(C.sourceUrl,'View lab photos '+arrow)}</div>`}</div>${sourceNote('news')}</div></section>`;}
  function join(){
    const topicsKo=[
      ['모집 대상','학부연구생, 석사 및 박사과정 학생'],
      ['연구 분야','X-by-Wire 시스템, 차량 통합모션제어, Lv4 자율주행 대응 원격주행·통신지연보상, AI 기반 모델개발 및 상태추정, 학습 기반 고정밀 모션제어'],
      ['연구 지원','장학금·연구장려금(지원 자격 및 재원에 따름), 산학협력 및 국제학회 참여 기회'],
      ['지원 방법','이력서 또는 간단한 연구계획서를 이메일로 제출']
    ];
    const topicsEn=[
      ['Positions','Undergraduate interns, M.S. and Ph.D. students'],
      ['Research','X-by-Wire systems, integrated vehicle motion control, delay-compensated teleoperation for Level 4 autonomous vehicles, AI-based modeling and state estimation, learning-based precision motion control'],
      ['Support','Scholarships and stipends (subject to eligibility and funding), industry collaboration and international conferences'],
      ['Apply','Email your CV or brief research statement']
    ];
    const areasKo=[
      ['전동화 X-by-Wire 샤시 시스템제어','',['SbW·EMB·능동현가·Active Anti-Roll Bar의 모델링 및 제어','액추에이터 힘·토크 추정, 정밀 추종 및 강인제어','마찰·외란 보상과 고장진단·안전 상태전환']],
      ['고성능 차량 통합모션제어 및 차세대 원격주행','',['조향·제동·구동·현가 통합제어 및 최적 타이어 힘 분배','핸들링·승차감·에너지 효율을 위한 예측·최적제어','통신 지연·지터·패킷 손실 예측·보상, 양방향 원격조향 및 HIL 검증']],
      ['AI 기반 샤시 모델개발 및 차량 상태추정','',['물리·AI 융합 샤시모델 및 Sim-to-Real 가상센서 개발','타이어 힘·노면 마찰·차체 운동상태 추정','실시간 AI 추론 기반 모델 적응·이상감지·고장진단']],
      ['학습 기반 고정밀 모션제어 및 실시간 AI 응용','',['전동 액추에이터 위치·속도·토크 고정밀 제어','Learning-DOB·Sliding Mode Control과 학습 기반 마찰·외란 보상','실시간 임베디드 보드 기반 AI 추론 및 전동화 샤시제어']]
    ];
    const areasEn=[
      ['X-by-Wire and Electrified Chassis System Control','',['Modeling and control of SbW, EMB, active suspension and active anti-roll bars','Actuator force/torque estimation, precision tracking and robust control','Friction/disturbance compensation, fault diagnosis and safe-state transitions']],
      ['Integrated Vehicle Motion Control and Next-Generation Teleoperation','',['Coordinated steering, braking, propulsion and suspension control with optimal tire-force allocation','Predictive/optimal control for handling, ride comfort and energy efficiency','Prediction and compensation of latency, jitter and packet loss; bilateral remote steering and HIL validation']],
      ['AI-Based Chassis Modeling and Vehicle State Estimation','',['Physics–AI hybrid models and Sim-to-Real virtual sensors','Tire-force, road-friction and vehicle-motion-state estimation','Real-time AI inference for model adaptation, anomaly detection and fault diagnosis']],
      ['Learning-Based Precision Motion Control and Real-Time AI','',['High-precision position, speed and torque control of electrified actuators','DOB/sliding-mode control with learning-based friction and disturbance compensation','Real-time AI inference and electrified chassis control on embedded hardware']]
    ];
    const areaPanels=(areas)=>`<div class="join-research-areas">${areas.map(([title,meta,points],i)=>`<section class="join-research-area"><div class="join-research-heading"><span class="join-research-number">${String(i+1).padStart(2,'0')}</span><h3>${title}</h3></div>${meta?`<p class="join-research-meta">${meta}</p>`:''}<ul>${points.map(point=>`<li>${point}</li>`).join('')}</ul></section>`).join('')}</div>`;
    const panel=(language,title,status,items,button,areas)=>`<article class="join-language-panel" lang="${language}"><div class="join-panel-top"><div class="join-panel-heading"><h2>${title}</h2><p class="join-panel-status" role="status">${status}</p></div><div class="join-panel-signature" aria-hidden="true"><strong>MCLAB</strong><span>PEOPLE DRIVE TOMORROW</span></div></div><dl class="join-panel-details">${items.map(([term,description])=>`<div class="join-panel-item"><dt>${term}</dt><dd>${description}</dd></div>`).join('')}</dl><div class="join-research-label">${language==='ko'?'세부 연구분야':'Research Areas'}</div>${areaPanels(areas)}<div class="join-panel-footer"><a class="btn" href="mailto:khnam@dgist.ac.kr?subject=${encodeURIComponent('MCLab research opportunity inquiry')}">${button} ${right}</a><a href="mailto:khnam@dgist.ac.kr" class="join-panel-email">khnam@dgist.ac.kr</a></div></article>`;
    return `${pageHero('JOIN THE TEAM','Research opportunities at MCLab.','')}<section class="section join-bilingual-section"><div class="container"><div class="join-bilingual-grid">${panel('ko','연구원 모집','2027년 봄학기 모집 완료',topicsKo,'지원 문의',areasKo)}${panel('en','Join MCLab','Spring 2027 Recruitment Closed',topicsEn,'Contact us',areasEn)}</div></div></section><section class="join-contact-section" id="contact"><div class="container"><div class="join-contact-strip"><div class="join-contact-identity"><span class="join-contact-kicker">MCLab · DGIST</span><strong>Prof. ${esc(D.pi.name)}</strong><span>${esc(C.department)}</span></div><div class="join-contact-details"><a href="mailto:${esc(C.email)}">${esc(C.email)}</a><a href="tel:${esc(C.phone)}">${esc(C.phone)}</a><span>Office ${esc(C.office)} · Lab ${esc(C.labRoom)}</span></div><div class="join-contact-address">DGIST · ${esc(C.address)}</div></div></div></section>`;
  }
  function toBib(p){
    const clean=s=>String(s||'').replace(/\\/g,'\\textbackslash{}').replace(/([{}%&#_$])/g,'\\$1');
    const author=p.authors.replace(/\*/g,'').replace(/,?\s+and\s+/g,', ').split(/,\s*/).filter(Boolean).map(x=>/et al\./i.test(x)?'others':clean(x)).join(' and ');
    const published=isAccepted(p);
    const type=published?(p.type==='Conference'?'inproceedings':'article'):'unpublished';
    const fields=[`  title = {${clean(p.title)}}`,`  author = {${author}}`];
    if(published)fields.push(`  ${p.type==='Conference'?'booktitle':'journal'} = {${clean(p.venue)}}`);
    if(p.year)fields.push(`  year = {${p.year}}`);
    if(published){
      const detail=p.details||'';
      const volume=detail.match(/vol\.\s*(\d+)/i), issue=detail.match(/no\.\s*(\d+)/i), pages=detail.match(/pp\.\s*(\d+)\s*[–—-]\s*(\d+)/i), article=detail.match(/article\s+(\d+)/i);
      if(volume)fields.push(`  volume = {${volume[1]}}`);
      if(issue)fields.push(`  number = {${issue[1]}}`);
      if(pages&&Number(pages[2])>=Number(pages[1]))fields.push(`  pages = {${pages[1]}--${pages[2]}}`);
      if(article)fields.push(`  eid = {${article[1]}}`);
    }
    if(p.doi){fields.push(`  doi = {${clean(p.doi)}}`);fields.push(`  url = {https://doi.org/${clean(p.doi)}}`);}
    if(!published)fields.push(`  note = {${clean(p.status)}; venue: ${clean(p.venue)}. Not an accepted publication.}`);
    else if(p.status==='Accepted')fields.push('  note = {Accepted for publication; final bibliographic details pending.}');
    if(p.era==='Before DGIST'&&p.authors.includes('et al.'))fields.push('  note = {Author list abbreviated in the source; verify before citing.}');
    return `@${type}{mclab_${p.id.replace(/-/g,'_')},\n${fields.join(',\n')}\n}`;
  }
  function downloadText(text,name,mime='text/plain'){
    const url=URL.createObjectURL(new Blob([text],{type:mime+';charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function openBib(id){
    activeBib=D.publications.find(p=>p.id===id);if(!activeBib)return;
    $('#bib-text').value=toBib(activeBib);$('#bib-status').textContent='';$('#bib-dialog').showModal();
  }
  function setupDialogs(){
    $('#dialogs').innerHTML=`<dialog id="search-dialog" class="search-dialog" aria-labelledby="search-title"><div class="dialog-header"><h2 id="search-title">Search MCLab</h2><button class="icon-btn" data-close-dialog="search-dialog" aria-label="Close search">${icon('close')}</button></div><label for="site-search" class="field-label">Search people, research, publications, and projects</label><input class="input" id="site-search" type="search" placeholder="Try steer-by-wire, state estimation, or Nam…" autocomplete="off"><div class="search-results" id="search-results" role="region" aria-label="Search results"></div><p class="search-help" id="search-help" role="status" aria-live="polite">Type at least two characters. Press Esc to close.</p></dialog><dialog id="bib-dialog" class="bib-dialog" aria-labelledby="bib-title"><div class="dialog-header"><h2 id="bib-title">Citation · BibTeX</h2><button class="icon-btn" data-close-dialog="bib-dialog" aria-label="Close citation">${icon('close')}</button></div><label for="bib-text" class="field-label">Bibliographic record</label><textarea id="bib-text" class="bib-code" readonly spellcheck="false"></textarea><p class="search-help">Generated from the lab’s public list. Verify author lists and publisher metadata before submission.</p><div class="dialog-footer"><button class="btn small" id="copy-bib">Copy BibTeX</button><button class="btn btn-outline small" id="download-bib">Download .bib ↓</button></div><p class="status-message" id="bib-status" role="status" aria-live="polite"></p></dialog>`;
    $$('[data-close-dialog]').forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.closeDialog).close()));
    $$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}}));
    $('#copy-bib').addEventListener('click',async()=>{const t=$('#bib-text');try{if(!navigator.clipboard)throw Error('Clipboard unavailable');await navigator.clipboard.writeText(t.value);$('#bib-status').textContent='Citation copied.';}catch(_){t.focus();t.select();const done=document.execCommand&&document.execCommand('copy');$('#bib-status').textContent=done?'Citation copied.':'Text selected. Press Ctrl+C (Windows) or ⌘C (Mac) to copy.';}});
    $('#download-bib').addEventListener('click',()=>{if(activeBib)downloadText(toBib(activeBib),activeBib.id+'.bib','application/x-bibtex');});
    const records=[
      ...Object.entries(titles).filter(([p])=>p!=='home').map(([p,title])=>({type:'Page',title,detail:'',page:p,anchor:''})),
      {type:'Faculty',title:D.pi.name,detail:D.pi.interests.join(' '),page:'professor',anchor:''},
      ...D.people.map(p=>({type:p.role,title:p.name,detail:[p.interest,p.nameKo,p.email,p.affiliation].join(' '),page:'people',anchor:p.id})),
      ...D.research.map(r=>({type:'Research',title:r.title,detail:r.detail,page:'research',anchor:r.id})),
      ...(D.researchTopics||[]).map(r=>({type:'Research theme',title:r.title,detail:r.description,page:'research',anchor:r.id})),
      ...D.publications.map(p=>({type:p.status+' · '+p.type,title:p.title,detail:p.authors+' '+p.venue,page:'publications',anchor:p.id})),
      ...D.projects.map(p=>({type:p.status+' · Project',title:p.title,detail:p.funder,page:'projects',anchor:p.id})),
      ...D.news.map(n=>({type:'News',title:n.title,detail:n.text,page:'news',anchor:n.id}))
    ];
    $('#site-search').addEventListener('input',()=>{const q=$('#site-search').value.toLocaleLowerCase().trim();if(q.length<2){$('#search-results').innerHTML='';$('#search-help').textContent='Type at least two characters. Press Esc to close.';return;}const found=records.filter(r=>(r.title+' '+r.detail).toLocaleLowerCase().includes(q));$('#search-results').innerHTML=found.length?found.slice(0,35).map(r=>`<a class="search-result" href="${link(r.page,r.anchor)}"><span class="result-type">${esc(r.type)}</span>${esc(r.title)}</a>`).join(''):'<div class="empty-state"><h3>No results found</h3><p>Try a broader research keyword or a family name.</p></div>';$('#search-help').textContent=`${found.length} result${found.length===1?'':'s'}${found.length>35?' · showing first 35':''}. Press Esc to close.`;});
    $('#search-results').addEventListener('click',e=>{if(e.target.closest('a'))$('#search-dialog').close();});
  }
  function openSearch(){$('#search-dialog').showModal();$('#site-search').focus();}
  const views={home,people,professor,research,publications,projects,news,join};
  function route(){
    let anchor='';
    if(isPreview){const parts=location.hash.replace(/^#\//,'').split('/');currentPage=views[parts[0]]?parts[0]:'home';anchor=parts[1]||'';}else{currentPage=document.body.dataset.page||'home';anchor=decodeURIComponent(location.hash.slice(1));}
    if(!views[currentPage])currentPage='home';
    document.title=currentPage==='home'?titles.home:`${titles[currentPage]} | MCLab · DGIST`;
    header();$('#main').innerHTML=views[currentPage]();footer();
    if(currentPage==='publications')setupPubs(anchor);
    if(currentPage==='projects')setupProjects(anchor);
    if(isPreview)window.scrollTo(0,0);
    if(anchor)setTimeout(()=>document.getElementById(anchor)?.scrollIntoView({block:'start',behavior:'instant'}),50);
    $$('img').forEach(img=>img.addEventListener('error',()=>{img.style.display='none';const p=img.closest('.person-art,.profile-art');if(p&&!p.querySelector('.initials,.profile-initials')){const s=document.createElement('span');s.className='initials';s.textContent=initial(img.alt||'MCLab');p.append(s);}}));
  }
  document.addEventListener('click',e=>{const b=e.target.closest('[data-bib]');if(b)openBib(b.dataset.bib);});
  document.addEventListener('keydown',e=>{
    const typing=/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)||document.activeElement.isContentEditable;
    if((e.key==='/'&&!typing)||((e.ctrlKey||e.metaKey)&&e.key==='k')){e.preventDefault();openSearch();}
    if(e.key==='Escape'){$$('dialog[open]').forEach(d=>d.close());$('#primary-nav')?.classList.remove('open');$('#menu-toggle')?.setAttribute('aria-expanded','false');}
  });
  document.querySelector('.skip-link')?.addEventListener('click',e=>{e.preventDefault();$('#main').focus();$('#main').scrollIntoView();});
  function setupImageViewer(){
    $('#dialogs').insertAdjacentHTML('beforeend',`<dialog id="image-dialog" class="image-dialog" aria-labelledby="image-title"><div class="dialog-header"><h2 id="image-title">Research image</h2><button type="button" class="icon-btn" id="close-image" aria-label="Close image">${icon('close')}</button></div><div class="image-viewer-stage"><img id="image-viewer-photo" alt=""></div><p class="image-viewer-note">Original laboratory image · Web-optimized copy</p></dialog>`);
    const dialog=$('#image-dialog');
    $('#close-image').addEventListener('click',()=>dialog.close());
    dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
    document.addEventListener('click',e=>{const button=e.target.closest('[data-image-open]');if(!button)return;const source=safeURL(button.dataset.imageOpen);if(!source)return;$('#image-title').textContent=button.dataset.imageTitle||'Laboratory image';$('#image-viewer-photo').src=button.dataset.imageOpen;$('#image-viewer-photo').alt=button.dataset.imageTitle||'Laboratory image';dialog.showModal();});
  }

  setupDialogs();
  setupImageViewer();
  window.addEventListener('hashchange',route);
  route();
  // Public exports used only by the local quality checks and optional editor.
  window.MCLAB_UTILS={toBib};
})();
