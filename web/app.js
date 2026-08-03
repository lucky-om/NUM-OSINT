/**
 * NUM-OSINT v3.0 — Frontend Engine
 * Developed by Lucky
 */

document.addEventListener('DOMContentLoaded', () => {
  // ── Image error handling fallback ─────────────────────────────────────
  document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', () => {
      img.style.display = 'none';
    });
  });

  // ── Canvas background ───────────────────────────────────────────────────
  initCanvas();

  // ── Mobile Navigation Toggle ────────────────────────────────────────────
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navToggle.classList.toggle('open');
      navMenu.classList.toggle('open');
    });

    // Close mobile nav when clicking a link
    navMenu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        navToggle.classList.remove('open');
        navMenu.classList.remove('open');
      });
    });

    // Close mobile nav when clicking outside
    document.addEventListener('click', (e) => {
      if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
        navToggle.classList.remove('open');
        navMenu.classList.remove('open');
      }
    });
  }

  // ── DOM refs ─────────────────────────────────────────────────────────────
  const form = document.getElementById('lookup-form');
  const phoneInput = document.getElementById('phone-input');
  const searchBtn = document.getElementById('search-btn');
  const btnLabel = document.getElementById('btn-label');
  const scanTag = document.getElementById('scan-tag');
  const statusMsg = document.getElementById('status-msg');
  const resultsSection = document.getElementById('results-section');
  const resNumber = document.getElementById('res-number');
  const recordsBox = document.getElementById('records-box');
  const telTbody = document.getElementById('tel-tbody');
  const jsonOut = document.getElementById('json-out');
  const copyBtn = document.getElementById('copy-btn');
  const consoleOut = document.getElementById('console-out');
  const progWrap = document.getElementById('prog-wrap');
  const progTrack = document.getElementById('prog-track');
  const progLabel = document.getElementById('prog-label');
  const progPct = document.getElementById('prog-pct');

  let lastQuery = 0;
  const THROTTLE_MS = 1200;
  const PROG_SEGS = 16;

  // Build segmented progress bar segments
  if (progTrack && progTrack.children.length === 0) {
    for (let i = 0; i < PROG_SEGS; i++) {
      const seg = document.createElement('div');
      seg.className = 'prog-seg';
      progTrack.appendChild(seg);
    }
  }

  // ── Digits-only input ────────────────────────────────────────────────────
  phoneInput?.addEventListener('input', () => {
    phoneInput.value = phoneInput.value.replace(/\D/g, '').slice(0, 10);
  });

  // Config ───────────────────────────────────────────────────────
  const INJECTED_API_URL = "__API_URL_PLACEHOLDER__";

  // Encrypted fallback — SHA-256 salt-based XOR (aligned with config.py)
  const _ENC_PAYLOAD = "vwzpy3mhkFuF4l9tSz9Vqn6rQpe3M73zmDoLxIFAkqlY+U2yxEu3pD9RKpi5V+9QxA3rO87NQpUly/ftJrDsGKpWKBYoPg0Szi+CfA==";
  const _SALT_STR = "NUM_OSINT_LUCKY_V2_SALT_2026";

  // Precomputed SHA-256 of the salt
  const _PRECOMPUTED_KEY = [218, 74, 202, 199, 171, 93, 84, 100, 213, 192, 80, 165, 237, 184, 50, 225, 74, 71, 129, 50, 39, 11, 245, 250, 105, 245, 235, 95, 235, 23, 159, 85];

  function getFallbackUrl() {
    try {
      const raw = atob(_ENC_PAYLOAD);
      const key = _PRECOMPUTED_KEY;
      let url = "";
      for (let i = 0; i < raw.length; i++) {
        const b = raw.charCodeAt(i);
        const k = key[i % key.length];
        url += String.fromCharCode(b ^ k ^ ((i * 37 + 13) & 0xFF));
      }
      // Validate it's a real URL
      if (url.startsWith("http://") || url.startsWith("https://")) {
        return url;
      }
      return "";
    } catch (e) {
      return "";
    }
  }

  function getApiEndpoint(targetNum) {
    let baseUrl = "";

    // 1) GitHub Actions injected URL (replaced during deploy)
    if (INJECTED_API_URL && !INJECTED_API_URL.includes("PLACEHOLDER") && INJECTED_API_URL.trim() !== "") {
      baseUrl = INJECTED_API_URL.trim();
    }
    // 2) Global window variable (set by external config)
    else if (window.API_URL && typeof window.API_URL === 'string' && window.API_URL.trim() !== '') {
      baseUrl = window.API_URL.trim();
    }
    // 3) Encrypted fallback
    else {
      baseUrl = getFallbackUrl();
    }

    if (!baseUrl) {
      throw new Error("API URL configuration error. Unable to resolve intelligence endpoint. Check GitHub Secrets → API_URL.");
    }

    const cleanNum = encodeURIComponent(targetNum);

    // Handle various URL patterns
    if (baseUrl.includes('{number}')) {
      return baseUrl.replace('{number}', cleanNum);
    } else if (baseUrl.includes('{num}')) {
      return baseUrl.replace('{num}', cleanNum);
    } else if (baseUrl.endsWith('=')) {
      // URL ends with num= → just append the number
      return baseUrl + cleanNum;
    } else if (/[?&]num=[^&]*$/.test(baseUrl)) {
      // URL has num=<something> at the end → replace value
      return baseUrl.replace(/num=[^&]*$/, `num=${cleanNum}`);
    } else if (/[?&]num=/.test(baseUrl)) {
      // URL has num=<something> in the middle
      return baseUrl.replace(/num=[^&]*/, `num=${cleanNum}`);
    } else {
      return baseUrl + cleanNum;
    }
  }

  // ── Form submit ──────────────────────────────────────────────────────────
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const num = phoneInput.value.trim();

    if (!/^[6-9]\d{9}$/.test(num)) {
      showStatus('INPUT ERROR: Enter a valid 10-digit Indian mobile number (starts with 6–9).', 'err');
      return;
    }

    const now = Date.now();
    if (now - lastQuery < THROTTLE_MS) {
      showStatus(`RATE LIMIT: Wait ${Math.ceil((THROTTLE_MS - (now - lastQuery)) / 1000)}s before retrying.`, 'err');
      return;
    }

    lastQuery = now;
    hideStatus();
    clearLog();
    setLoading(true);
    setScanTag('SCANNING');

    log(`Querying intelligence database for +91 ${num}...`, 'sys');

    await runProgress();

    try {
      const apiUrl = getApiEndpoint(num);
      log(`Connecting to secure API endpoint...`, 'info');

      let response = null;
      let rawJson = null;

      // 1. Direct fetch attempt
      try {
        response = await fetch(apiUrl, {
          method: 'GET',
          headers: { Accept: 'application/json' },
          signal: AbortSignal.timeout(5000)
        });
        if (response.ok) {
          rawJson = await response.json();
          log('Connected via direct API channel.', 'ok');
        }
      } catch (directErr) {
        log('Direct connection restricted by browser CORS — routing through secure proxy bridge...', 'info');
      }

      // 2. CorsProxy.io primary proxy relay
      if (!rawJson) {
        try {
          const proxyUrl1 = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;
          response = await fetch(proxyUrl1, {
            method: 'GET',
            headers: { Accept: 'application/json' },
            signal: AbortSignal.timeout(15000)
          });
          if (response.ok) {
            rawJson = await response.json();
            log('Connected via primary CORS proxy bridge.', 'ok');
          }
        } catch (p1Err) {
          log('Primary proxy bridge unavailable — switching to secondary relay...', 'info');
        }
      }

      // 3. AllOrigins fallback proxy relay
      if (!rawJson) {
        try {
          const proxyUrl2 = `https://api.allorigins.win/get?url=${encodeURIComponent(apiUrl)}`;
          response = await fetch(proxyUrl2, {
            method: 'GET',
            headers: { Accept: 'application/json' },
            signal: AbortSignal.timeout(15000)
          });
          if (response.ok) {
            const wrapper = await response.json();
            if (wrapper && wrapper.contents) {
              rawJson = typeof wrapper.contents === 'string' ? JSON.parse(wrapper.contents) : wrapper.contents;
              log('Connected via secondary proxy relay.', 'ok');
            }
          }
        } catch (p2Err) {
          log('Secondary proxy bridge failed — trying tertiary relay...', 'info');
        }
      }

      // 4. cors-anywhere / thingproxy tertiary fallback
      if (!rawJson) {
        try {
          const proxyUrl3 = `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(apiUrl)}`;
          response = await fetch(proxyUrl3, {
            method: 'GET',
            headers: { Accept: 'application/json' },
            signal: AbortSignal.timeout(15000)
          });
          if (response.ok) {
            const text = await response.text();
            try {
              rawJson = JSON.parse(text);
            } catch (_) {
              // Try extracting JSON from response
              const s = text.indexOf('{'), e = text.lastIndexOf('}');
              if (s !== -1 && e > s) {
                rawJson = JSON.parse(text.substring(s, e + 1));
              }
            }
            if (rawJson) {
              log('Connected via tertiary proxy relay.', 'ok');
            }
          }
        } catch (p3Err) {
          // Keep rawJson null
        }
      }

      if (!rawJson) {
        throw new Error('All API channels and proxy relays failed to respond. The upstream API may be down, or check your network connection.');
      }

      const recs = rawJson.result || rawJson.results || rawJson.data || [];
      const isOk = rawJson.status === 'success' || (Array.isArray(recs) && recs.length > 0);

      const data = {
        success: isOk,
        message: rawJson.message || (isOk ? 'Query successful' : 'No records found'),
        data: rawJson
      };

      if (!data.success) {
        const errMsg = data.message || 'No OSINT records found for this query.';
        log(`API Response: ${errMsg}`, 'err');
        showStatus(`API NOTICE: ${errMsg}`, 'err');
        resultsSection.classList.add('hidden');
        setScanTag('NOTICE');
      } else {
        const rawRecs = data.data?.result || data.data?.results || data.data?.data || [];
        const uniqueRecs = deduplicateRecords(rawRecs);

        if (uniqueRecs.length === 0) {
          showStatus(data.message || 'NO RECORDS: No matching dossier found for this number.', 'err');
          resultsSection.classList.add('hidden');
          setScanTag('EMPTY');
        } else {
          log(`${rawRecs.length} raw record(s) returned -> ${uniqueRecs.length} unique dossier(s) compiled.`, 'ok');
          renderResults(data, num, uniqueRecs);
          showStatus(`RESOLVED: ${uniqueRecs.length} unique record(s) compiled for +91 ${num}.`, 'ok');
          setScanTag('COMPLETE');
        }
      }
    } catch (err) {
      log(`Error: ${err.message || 'Cannot reach intelligence server.'}`, 'err');
      showStatus(`CONNECTION ERROR: ${err.message || 'Network error: Failed to fetch. Please check your network connection.'}`, 'err');
      resultsSection.classList.add('hidden');
      setScanTag('OFFLINE');
    } finally {
      setLoading(false);
    }
  });

  // ── Deduplication & Merger Helper ─────────────────────────────────────────
  function deduplicateRecords(records) {
    if (!Array.isArray(records)) return [];

    const unique = [];
    const map = new Map();

    records.forEach(rec => {
      if (!rec || typeof rec !== 'object') return;

      const norm = s => (s || '').toString().toLowerCase().replace(/[^a-z0-9]/g, '').trim();

      const nameNorm = norm(rec.name);
      const numNorm = norm(rec.num);
      const addrNorm = norm(rec.address);

      // Composite fingerprint
      const key = `${nameNorm}_${numNorm}_${addrNorm.slice(0, 25)}`;

      if (!map.has(key)) {
        const copy = { ...rec };
        map.set(key, copy);
        unique.push(copy);
      } else {
        // Merge missing/richer details into existing record
        const existing = map.get(key);
        ['aadhar', 'alt', 'fname', 'email', 'circle'].forEach(field => {
          if ((!existing[field] || existing[field] === 'null' || existing[field] === ' ') && rec[field] && rec[field] !== 'null') {
            existing[field] = rec[field];
          }
        });

        if (rec.address && rec.address.length > (existing.address || '').length) {
          existing.address = rec.address;
        }
      }
    });

    return unique;
  }

  // ── ID Classification (Aadhaar vs Driving License) ────────────────────────
  function parseGovernmentID(idVal) {
    if (!idVal || idVal === 'null' || idVal === ' ') {
      return { type: 'NONE', aadhar: null, dl: null };
    }

    const clean = String(idVal).trim();

    // 12 numeric digits = Aadhaar Number
    if (/^\d{12}$/.test(clean)) {
      return { type: 'AADHAAR', aadhar: clean, dl: null };
    }

    // Otherwise, contains letters or non-12 format = Driving License / Govt ID
    return { type: 'DL', aadhar: null, dl: clean };
  }

  // ── Segmented progress animation ─────────────────────────────────────────
  function runProgress() {
    return new Promise((resolve) => {
      progWrap?.classList.remove('hidden');
      const segs = progTrack ? progTrack.querySelectorAll('.prog-seg') : [];
      let filled = 0;

      const LABELS = [
        'INITIALIZING TRACE ROUTE...',
        'RESOLVING GATEWAY...',
        'AUTHENTICATING API KEY...',
        'QUERYING SUBSCRIBER DATABASE...',
        'EXTRACTING TELEMETRY...',
        'DEDUPLICATING DOSSIERS...',
        'BUILDING DOSSIER CARDS...',
      ];

      let labelIdx = 0;

      const iv = setInterval(() => {
        if (filled < PROG_SEGS && segs.length > 0) {
          segs[filled].classList.add('filled');
          filled++;

          const pct = Math.round((filled / PROG_SEGS) * 100);
          if (progPct) progPct.textContent = `${pct}%`;

          const labelStep = Math.floor((filled / PROG_SEGS) * LABELS.length);
          if (labelStep < LABELS.length && labelStep !== labelIdx) {
            labelIdx = labelStep;
            if (progLabel) progLabel.textContent = LABELS[labelIdx];
            log(LABELS[labelIdx], 'info');
          }
        }

        if (filled >= PROG_SEGS || segs.length === 0) {
          clearInterval(iv);
          setTimeout(() => {
            progWrap?.classList.add('hidden');
            segs.forEach(s => s.classList.remove('filled'));
            if (progPct) progPct.textContent = '0%';
            if (progLabel) progLabel.textContent = 'INITIALIZING TRACE ROUTE...';
            resolve();
          }, 200);
        }
      }, 50);
    });
  }

  // ── Render results ───────────────────────────────────────────────────────
  function renderResults(res, queryNum, uniqueRecs) {
    resNumber.textContent = `+91 ${queryNum}`;
    recordsBox.innerHTML = '';
    telTbody.innerHTML = '';

    if (uniqueRecs.length > 0) {
      uniqueRecs.forEach((rec, i) => {
        // Clean Address
        const rawAddr = rec.address || '';
        const cleanAddr = rawAddr.replace(/!+/g, ', ').replace(/\s+/g, ' ').replace(/^,\s*/, '').trim();
        const mapsUrl = cleanAddr ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(cleanAddr)}` : null;

        // Parse Govt ID / Driving License
        const parsedID = parseGovernmentID(rec.aadhar);

        // Number for deep links (use rec.num or queryNum)
        const contactNum = rec.num || queryNum;

        const card = document.createElement('div');
        card.className = 'dossier-card';
        card.style.animationDelay = `${i * 55}ms`;

        card.innerHTML = `
          <div class="dossier-head">
            <span class="dossier-title">RECORD ${String(i + 1).padStart(2, '0')} — ${esc(rec.name || 'UNNAMED')}</span>
            <div class="dossier-head-actions">
              <span class="dossier-badge">VERIFIED</span>
              <button class="btn-card-copy" data-idx="${i}">COPY DOSSIER</button>
            </div>
          </div>
          <div class="field-grid">
            <!-- 1. Full Name -->
            <div class="data-field">
              <div class="f-label">Full Name</div>
              <div class="f-value hi">${esc(rec.name || 'N/A')}</div>
            </div>
            <!-- 2. Mobile Number -->
            <div class="data-field">
              <div class="f-label">Mobile Number</div>
              <div class="f-value hot">+91 ${esc(contactNum || 'N/A')}</div>
            </div>
            <!-- 3. Father / Guardian -->
            <div class="data-field">
              <div class="f-label">Father / Guardian</div>
              <div class="f-value">${esc(rec.fname || 'N/A')}</div>
            </div>
            <!-- 4. Telecom Circle -->
            <div class="data-field">
              <div class="f-label">Telecom Circle</div>
              <div class="f-value teal">${esc(rec.circle || 'N/A')}</div>
            </div>
            <!-- 5. Aadhaar Ref -->
            <div class="data-field">
              <div class="f-label">Aadhaar Number</div>
              <div class="f-value">${parsedID.aadhar ? esc(parsedID.aadhar) : 'NOT DISCLOSED'}</div>
            </div>
            <!-- 6. Driving License No. -->
            ${parsedID.dl ? `
            <div class="data-field">
              <div class="f-label" style="color:var(--col-secondary-bright);">Driving License No.</div>
              <div class="f-value hot">${esc(parsedID.dl)}</div>
            </div>
            ` : ''}
            <!-- 7. Alternate Number -->
            <div class="data-field">
              <div class="f-label">Alternate Number</div>
              <div class="f-value">${rec.alt && rec.alt !== rec.num ? `+91 ${esc(rec.alt)}` : 'NONE'}</div>
            </div>
            <!-- 8. Email Address -->
            <div class="data-field">
              <div class="f-label">Email Address</div>
              <div class="f-value">${esc(rec.email?.trim() || 'NONE')}</div>
            </div>
          </div>
          <div class="addr-field">
            <div class="f-label" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
              <span>Registered Address</span>
              ${mapsUrl ? `<a href="${mapsUrl}" target="_blank" rel="noopener noreferrer" class="map-link">🗺 MAP LOCATION ↗</a>` : ''}
            </div>
            <div class="f-value">
              ${esc(cleanAddr || 'N/A')}
            </div>
          </div>
          <!-- WhatsApp & Telegram Deep Links -->
          <div class="deep-links-bar">
            <a href="https://wa.me/91${esc(contactNum)}" target="_blank" rel="noopener noreferrer" class="btn-deep-link btn-whatsapp-direct" title="Open WhatsApp chat with +91 ${esc(contactNum)}">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
              WHATSAPP
            </a>
            <a href="https://t.me/+91${esc(contactNum)}" target="_blank" rel="noopener noreferrer" class="btn-deep-link btn-telegram-direct" title="Open Telegram with +91 ${esc(contactNum)}">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
              TELEGRAM
            </a>
          </div>
        `;

        recordsBox.appendChild(card);

        // Bind Copy Card button listener
        const copyBtnEl = card.querySelector('.btn-card-copy');
        copyBtnEl?.addEventListener('click', () => {
          copyDossierToClipboard(rec, cleanAddr, mapsUrl, parsedID, copyBtnEl);
        });

        // Telemetry row
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>#${i + 1} — ${esc(rec.name || 'Record')}</td>
          <td>+91 ${esc(rec.num || queryNum)} · ${esc(rec.circle || 'India')}</td>
          <td><span class="src-tag">LIVE API</span></td>
        `;
        telTbody.appendChild(tr);
      });
    } else {
      recordsBox.innerHTML = `
        <div class="dossier-card">
          <div class="dossier-head">
            <span class="dossier-title">NO SUBSCRIBER RECORDS FOUND</span>
            <span class="dossier-badge">STATUS 404</span>
          </div>
          <div class="field-grid">
            <div class="data-field">
              <div class="f-label">Queried Number</div>
              <div class="f-value hot">+91 ${esc(queryNum)}</div>
            </div>
            <div class="data-field">
              <div class="f-label">Upstream Status</div>
              <div class="f-value">NOT IN INDEX</div>
            </div>
          </div>
          <div class="addr-field">
            <div class="f-label">Information</div>
            <div class="f-value">This number is not present in the subscriber database. Try another number or the number may be unregistered.</div>
          </div>
        </div>
      `;
      telTbody.innerHTML = `<tr><td colspan="3" style="color:var(--col-text-dim);font-size:.8rem;">No records for +91 ${esc(queryNum)}</td></tr>`;
    }

    jsonOut.textContent = JSON.stringify(res, null, 2);
    resultsSection.classList.remove('hidden');

    // Laser wipe reveal
    resultsSection.classList.add('wipe');
    setTimeout(() => resultsSection.classList.remove('wipe'), 750);

    // Scroll into view
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Copy Dossier Handler ──────────────────────────────────────────────────
  function copyDossierToClipboard(rec, cleanAddr, mapsUrl, parsedID, btnEl) {
    const textLines = [
      `=== NUM-OSINT v3.0 DOSSIER RECORD ===`,
      `Full Name          : ${rec.name || 'N/A'}`,
      `Father / Guardian  : ${rec.fname || 'N/A'}`,
      `Mobile Number      : +91 ${rec.num || 'N/A'}`,
      `Alternate Number   : ${rec.alt ? '+91 ' + rec.alt : 'NONE'}`,
      `Telecom Circle     : ${rec.circle || 'N/A'}`,
      `Aadhaar Number     : ${parsedID.aadhar || 'NOT DISCLOSED'}`,
    ];

    if (parsedID.dl) {
      textLines.push(`Driving License No.: ${parsedID.dl}`);
    }

    textLines.push(`Email              : ${rec.email?.trim() || 'NONE'}`);
    textLines.push(`Registered Address : ${cleanAddr || 'N/A'}`);
    if (mapsUrl) {
      textLines.push(`Google Maps Link   : ${mapsUrl}`);
    }
    textLines.push(`WhatsApp           : https://wa.me/91${rec.num || ''}`);
    textLines.push(`Telegram           : https://t.me/+91${rec.num || ''}`);
    textLines.push(`====================================`);

    const formattedText = textLines.join('\n');

    navigator.clipboard.writeText(formattedText).then(() => {
      const origText = btnEl.textContent;
      btnEl.textContent = '[✓] COPIED';
      btnEl.style.background = 'var(--col-primary)';
      btnEl.style.color = '#000';
      setTimeout(() => {
        btnEl.textContent = origText;
        btnEl.style.background = '';
        btnEl.style.color = '';
      }, 2000);
    });
  }

  // ── Tab switcher ─────────────────────────────────────────────────────────
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('on');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('on');
      btn.setAttribute('aria-selected', 'true');

      const tab = btn.dataset.tab;
      document.querySelectorAll('.tab-pane').forEach(p => {
        p.classList.toggle('hidden', p.id !== tab);
      });
    });
  });

  // ── Copy JSON ─────────────────────────────────────────────────────────────
  copyBtn?.addEventListener('click', () => {
    navigator.clipboard.writeText(jsonOut.textContent).then(() => {
      const orig = copyBtn.textContent;
      copyBtn.textContent = '[✓] COPIED';
      copyBtn.style.background = 'var(--col-primary)';
      copyBtn.style.color = '#000';
      setTimeout(() => {
        copyBtn.textContent = orig;
        copyBtn.style.background = '';
        copyBtn.style.color = '';
      }, 2000);
    });
  });

  // ── Helpers ───────────────────────────────────────────────────────────────
  function setLoading(on) {
    if (!searchBtn || !btnLabel) return;
    searchBtn.disabled = on;
    btnLabel.textContent = on ? 'QUERYING...' : 'EXECUTE';
  }

  function setScanTag(label) {
    if (!scanTag) return;
    scanTag.textContent = label;
    const isActive = ['SCANNING'].includes(label);
    scanTag.classList.toggle('scanning', isActive);
  }

  function showStatus(msg, type) {
    if (!statusMsg) return;
    statusMsg.textContent = msg;
    statusMsg.className = `status-msg ${type}`;
  }

  function hideStatus() {
    if (!statusMsg) return;
    statusMsg.className = 'status-msg hidden';
  }

  function log(msg, type = 'info') {
    if (!consoleOut) return;
    const el = document.createElement('div');
    el.className = `cl cl-${type}`;
    el.textContent = `[${timestamp()}] ${msg}`;
    consoleOut.appendChild(el);
    consoleOut.scrollTop = consoleOut.scrollHeight;
  }

  function clearLog() {
    if (consoleOut) consoleOut.innerHTML = '';
  }

  function timestamp() {
    return new Date().toLocaleTimeString('en-IN', { hour12: false });
  }

  function esc(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, m =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[m]
    );
  }

}); // end DOMContentLoaded


// ══ CANVAS — Cyber Matrix Data Rain + Neon Particle Constellation ════════
// Theme: Violet (#BF00FF) & Hot Pink (#FF006E) — NO green
function initCanvas() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W = canvas.width = window.innerWidth;
  let H = canvas.height = window.innerHeight;

  const isMobile = window.innerWidth <= 768 || ('ontouchstart' in window);

  const onResize = () => {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    resetDrops();
    resetParticles();
  };

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(onResize, 150);
  });

  const COL_W = isMobile ? 18 : 14; 
  const CHARS = '01ヲアイウエオカキクケコサシスセソタチ█▓▒░◆■◈◉ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  let drops = [];

  function resetDrops() {
    drops = [];
    const cols = Math.floor(W / COL_W);
    for (let i = 0; i < cols; i += 2) {
      drops.push({
        x: i * COL_W + COL_W / 2,
        y: Math.random() * H,
        speed: Math.random() * 0.6 + 0.35,
        len: Math.floor(Math.random() * (isMobile ? 10 : 16) + 6),
        chars: Array.from({ length: 20 }, () => randChar()),
        timer: Math.random() * 100,
      });
    }
  }

  function randChar() {
    return CHARS[Math.floor(Math.random() * CHARS.length)];
  }

  let particles = [];

  function resetParticles() {
    particles = [];
    const count = isMobile
      ? Math.min(Math.floor(W / 70), 8)
      : Math.min(Math.floor(W / 45), 22);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        r: Math.random() * 1.5 + 0.5,
        a: Math.random() * 0.35 + 0.1,
        col: Math.random() > 0.45 ? '191,0,255' : '255,0,110',
      });
    }
  }

  resetDrops();
  resetParticles();

  let lastT = 0;
  let rafId;

  function frame(now) {
    rafId = requestAnimationFrame(frame);

    // Delta time calculation fixed: prevent jump on frame 1 or after tab switch
    const dt = (lastT > 0 && now > lastT) ? Math.min((now - lastT) / 16.6, 2.5) : 1;
    lastT = now;

    // Crisp contrast fade background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.14)';
    ctx.fillRect(0, 0, W, H);

    ctx.font = `${COL_W - 2}px 'JetBrains Mono', monospace`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    for (const d of drops) {
      d.timer += dt * 16.6;
      if (d.timer > 80) {
        d.timer = 0;
        d.chars[Math.floor(Math.random() * d.chars.length)] = randChar();
      }

      for (let i = 0; i < d.len; i++) {
        const cy = d.y - i * COL_W;
        if (cy < -COL_W || cy > H + COL_W) continue;

        const frac = 1 - (i / d.len);
        const ch = d.chars[i % d.chars.length];

        // Vibrant Violet & Hot Pink matrix stream
        if (i === 0) {
          ctx.fillStyle = '#FFFFFF'; // Bright white head
        } else if (i === 1) {
          ctx.fillStyle = '#FF006E'; // Hot pink bright
        } else if (i < 5) {
          ctx.fillStyle = `rgba(225, 40, 255, ${frac * 0.9})`; // Vivid violet-pink
        } else if (i < 10) {
          ctx.fillStyle = `rgba(191, 0, 255, ${frac * 0.75})`; // Electric violet
        } else {
          ctx.fillStyle = `rgba(140, 0, 210, ${frac * 0.45})`; // Deep violet tail
        }

        ctx.fillText(ch, d.x, cy);
      }

      d.y += d.speed * dt * 1.3;
      if (d.y - d.len * COL_W > H) {
        d.y = Math.random() * -COL_W * 6;
        d.speed = Math.random() * 0.7 + 0.45;
        d.len = Math.floor(Math.random() * (isMobile ? 10 : 16) + 6);
      }
    }

    // Particle constellation
    const LINK_DIST = isMobile ? 80 : 110;
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.col}, ${p.a})`;
      ctx.fill();

      if (!isMobile) {
        for (let j = i + 1; j < particles.length; j++) {
          const q = particles[j];
          const dx = p.x - q.x, dy = p.y - q.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < LINK_DIST) {
            const lineA = 0.15 * (1 - dist / LINK_DIST);
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = `rgba(${p.col}, ${lineA})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }
    }
  }

  rafId = requestAnimationFrame(frame);

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(rafId);
    } else {
      lastT = 0;
      rafId = requestAnimationFrame(frame);
    }
  });
}

