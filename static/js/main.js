/**
 * Mac GunJon - Is Bot | Main JavaScript
 * Initializes AOS, Lucide icons, GSAP, Typed.js, and core functionality
 */

document.addEventListener('DOMContentLoaded', function() {

  /* ---- Lucide Icons ---- */
  function initLucide() {
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  }
  initLucide();
  /* Retry once after 1s in case CDN loaded late */
  setTimeout(initLucide, 1000);
  /* Redraw ecosystem lines after icons render */
  setTimeout(drawEcoLines, 200);

  /* ---- AOS (Animate On Scroll) ---- */
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 600,
      easing: 'ease-out-cubic',
      once: true,
      offset: 50,
      disable: false
    });
    /* Safety: if AOS doesn't trigger elements after 3s, force them visible */
    setTimeout(function() {
      document.querySelectorAll('[data-aos]').forEach(function(el) {
        if (!el.classList.contains('aos-animate')) {
          el.classList.add('aos-animate');
        }
      });
    }, 3000);
  } else {
    /* AOS not loaded at all — remove data-aos so content is visible */
    document.querySelectorAll('[data-aos]').forEach(function(el) {
      el.removeAttribute('data-aos');
    });
  }

  /* ---- GSAP ScrollTrigger ---- */
  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);

    /* Header shadow on scroll */
    var header = document.getElementById('siteHeader');
    if (header) {
      window.addEventListener('scroll', function() {
        if (window.scrollY > 10) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      });
    }

    /* Stat counter animation */
    document.querySelectorAll('[data-count]').forEach(function(el) {
      var target = parseInt(el.getAttribute('data-count'), 10);
      gsap.from(el, {
        textContent: 0,
        duration: 1.5,
        ease: 'power2.out',
        snap: { textContent: 1 },
        scrollTrigger: {
          trigger: el,
          start: 'top 90%',
          once: true
        }
      });
    });

    /* Product card stagger animation */
    document.querySelectorAll('.product-card').forEach(function(card, i) {
      gsap.from(card, {
        y: 30,
        opacity: 0,
        duration: 0.5,
        delay: i * 0.05,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: card,
          start: 'top 95%',
          once: true
        }
      });
    });
  }

  /* ---- Typed.js (Hero Section) ---- */
  if (typeof Typed !== 'undefined') {
    var typedElement = document.getElementById('typed-text');
    if (typedElement) {
      new Typed('#typed-text', {
        strings: ['Bots', 'Websites', 'Automation', 'Courses'],
        typeSpeed: 50,
        backSpeed: 30,
        loop: true,
        showCursor: true,
        cursorChar: '|'
      });
    }
  }

  /* ---- CSRF Helper ---- */
  window.getCsrfToken = function() {
    var name = 'csrftoken';
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var parts = cookies[i].trim().split('=');
      if (parts[0] === name) return decodeURIComponent(parts[1]);
    }
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  };

  /* ---- Cookie Consent ---- */
  window.acceptCookies = function(type) {
    var banner = document.getElementById('cookieConsent');
    if (banner) banner.style.display = 'none';
    localStorage.setItem('cookie_consent', type);
    document.cookie = 'cookie_consent=' + type + ';path=/;max-age=31536000';
  };

  var consent = localStorage.getItem('cookie_consent');
  if (!consent) {
    var banner = document.getElementById('cookieConsent');
    if (banner) banner.style.display = 'block';
  }

  /* ---- Auto-dismiss Toasts ---- */
  document.querySelectorAll('[data-toast]').forEach(function(t) {
    setTimeout(function() {
      t.style.opacity = '0';
      t.style.transform = 'translateX(100px)';
      t.style.transition = 'all 0.3s ease';
      setTimeout(function() { t.remove(); }, 300);
    }, 4000);
  });

  /* ---- Mobile Nav Toggler ---- */
  var navToggler = document.getElementById('navToggler');
  var mobileNav = document.getElementById('mobileNav');
  if (navToggler && mobileNav) {
    navToggler.addEventListener('click', function() {
      var isOpen = mobileNav.style.display === 'flex';
      mobileNav.style.display = isOpen ? 'none' : 'flex';
    });
  }

  /* ---- Chatbot Widget ---- */
  (function() {
    var toggle = document.getElementById('chatbotToggle');
    var closeBtn = document.getElementById('chatbotClose');
    var panel = document.getElementById('chatbotPanel');
    var input = document.getElementById('chatInput');
    var sendBtn = document.getElementById('chatSendBtn');
    var messages = document.getElementById('chatMessages');
    var isOpen = false;

    if (!toggle || !panel) return;

    function openPanel() {
      isOpen = true;
      panel.classList.add('open');
      if (input) input.focus();
    }

    function closePanel() {
      isOpen = false;
      panel.classList.remove('open');
    }

    toggle.addEventListener('click', function() {
      isOpen ? closePanel() : openPanel();
    });
    if (closeBtn) closeBtn.addEventListener('click', closePanel);

    function escapeHtml(s) {
      var div = document.createElement('div');
      div.appendChild(document.createTextNode(s));
      return div.innerHTML;
    }

    function appendMsg(text, role) {
      var wrap = document.createElement('div');
      wrap.className = 'chat-msg ' + role;
      var iconName = role === 'bot' ? 'bot' : 'user';
      wrap.innerHTML = '<div class="avatar"><i data-lucide="' + iconName + '"></i></div>' +
        '<div class="bubble">' + escapeHtml(text) + '</div>';
      messages.appendChild(wrap);
      if (typeof lucide !== 'undefined') lucide.createIcons({ nodes: [wrap] });
      messages.scrollTop = messages.scrollHeight;
    }

    function appendTyping() {
      var wrap = document.createElement('div');
      wrap.className = 'chat-msg bot typing-indicator-wrap';
      wrap.innerHTML = '<div class="avatar"><i data-lucide="bot"></i></div>' +
        '<div class="bubble" style="padding:.55rem .85rem;">' +
        '<span style="display:inline-flex;gap:4px;align-items:center;">' +
        '<span style="width:6px;height:6px;background:var(--text-muted);border-radius:50%;animation:typing 1s infinite .0s;display:inline-block;"></span>' +
        '<span style="width:6px;height:6px;background:var(--text-muted);border-radius:50%;animation:typing 1s infinite .2s;display:inline-block;"></span>' +
        '<span style="width:6px;height:6px;background:var(--text-muted);border-radius:50%;animation:typing 1s infinite .4s;display:inline-block;"></span>' +
        '</span></div>';
      messages.appendChild(wrap);
      if (typeof lucide !== 'undefined') lucide.createIcons({ nodes: [wrap] });
      messages.scrollTop = messages.scrollHeight;
      return wrap;
    }

    async function sendMessage() {
      var text = input.value.trim();
      if (!text) return;
      appendMsg(text, 'user');
      input.value = '';
      sendBtn.disabled = true;

      var typingEl = appendTyping();

      try {
        var res = await fetch(chatbotMessageUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ message: text })
        });
        var data = await res.json();
        typingEl.remove();
        appendMsg(data.response, 'bot');
      } catch (err) {
        typingEl.remove();
        appendMsg('Sorry, something went wrong. Please try again.', 'bot');
      } finally {
        sendBtn.disabled = false;
        input.focus();
      }
    }

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (input) input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') sendMessage();
    });
  })();

  /* ---- Smooth Scroll for Anchors ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ---- Auto-submit Filter Selects ---- */
  document.querySelectorAll('[data-auto-submit]').forEach(function(el) {
    el.addEventListener('change', function() {
      this.closest('form').submit();
    });
  });

  /* ---- Form Validation ---- */
  document.querySelectorAll('.needs-validation').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  /* ---- Ecosystem Lines ---- */
  var ecoSvg = document.getElementById('ecoSvg');
  var ecoHub = document.getElementById('ecoHub');

  function drawEcoLines() {
    if (!ecoSvg || !ecoHub) return;
    var grid = ecoSvg.parentElement;
    var gR = grid.getBoundingClientRect();
    var hubCore = ecoHub.querySelector('.eco-hub-core');
    if (!hubCore) return;
    var hR = hubCore.getBoundingClientRect();

    var hcx = hR.left + hR.width / 2 - gR.left;
    var hcy = hR.top + hR.height / 2 - gR.top;
    var hlx = hR.left - gR.left;
    var hrx = hR.right - gR.left;

    ecoSvg.setAttribute('width', gR.width);
    ecoSvg.setAttribute('height', gR.height);
    ecoSvg.setAttribute('viewBox', '0 0 ' + gR.width + ' ' + gR.height);

    var defs = '<defs>';
    grid.querySelectorAll('.eco-card').forEach(function(c) {
      var col = c.getAttribute('data-color');
      defs += '<filter id="glow-' + col.replace('#', '') + '" x="-20%" y="-20%" width="140%" height="140%">' +
        '<feGaussianBlur stdDeviation="3" result="blur" />' +
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>' +
        '</filter>';
    });
    defs += '</defs>';

    var html = '';
    var idx = 0;

    grid.querySelectorAll('.eco-side-l .eco-card').forEach(function(c) {
      var cr = c.getBoundingClientRect();
      var icon = c.querySelector('.eco-card-ic');
      if (!icon) return;
      var ir = icon.getBoundingClientRect();
      var sx = cr.right - gR.left;
      var sy = ir.top + ir.height / 2 - gR.top;
      var col = c.getAttribute('data-color');
      var gid = 'glow-' + col.replace('#', '');
      html += '<g class="eco-line-g" data-card="' + idx + '">' +
        '<line x1="' + sx + '" y1="' + sy + '" x2="' + hcx + '" y2="' + hcy + '" stroke="' + col + '" filter="url(#' + gid + ')" class="eco-line"/>' +
        '<circle cx="' + sx + '" cy="' + sy + '" r="3" fill="' + col + '" class="eco-dot"/>' +
        '<circle cx="' + hcx + '" cy="' + hcy + '" r="3" fill="' + col + '" class="eco-dot"/>' +
        '</g>';
      idx++;
    });

    grid.querySelectorAll('.eco-side-r .eco-card').forEach(function(c) {
      var cr = c.getBoundingClientRect();
      var icon = c.querySelector('.eco-card-ic');
      if (!icon) return;
      var ir = icon.getBoundingClientRect();
      var ex = cr.left - gR.left;
      var ey = ir.top + ir.height / 2 - gR.top;
      var col = c.getAttribute('data-color');
      var gid = 'glow-' + col.replace('#', '');
      html += '<g class="eco-line-g" data-card="' + idx + '">' +
        '<line x1="' + hcx + '" y1="' + hcy + '" x2="' + ex + '" y2="' + ey + '" stroke="' + col + '" filter="url(#' + gid + ')" class="eco-line"/>' +
        '<circle cx="' + hcx + '" cy="' + hcy + '" r="3" fill="' + col + '" class="eco-dot"/>' +
        '<circle cx="' + ex + '" cy="' + ey + '" r="3" fill="' + col + '" class="eco-dot"/>' +
        '</g>';
      idx++;
    });

    ecoSvg.innerHTML = defs + html;
  }

  function onEcoCardHover() {
    var svg = document.getElementById('ecoSvg');
    if (!svg) return;
    document.querySelectorAll('.eco-card').forEach(function(card, i) {
      var col = card.getAttribute('data-color');
      card.style.setProperty('--card-accent', col);
      card.addEventListener('mouseenter', function() {
        svg.querySelectorAll('.eco-line-g').forEach(function(g) {
          g.classList.toggle('eco-line-active', parseInt(g.getAttribute('data-card')) === i);
        });
        card.style.borderColor = col;
        card.style.boxShadow = '0 16px 40px ' + col + '1a, 0 4px 12px rgba(0,0,0,.04)';
      });
      card.addEventListener('mouseleave', function() {
        svg.querySelectorAll('.eco-line-g').forEach(function(g) {
          g.classList.remove('eco-line-active');
        });
        card.style.borderColor = '';
        card.style.boxShadow = '';
      });
    });
  }

  function animateEcoCards() {
    var cards = document.querySelectorAll('.eco-card');
    if (!cards.length) return;
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            var idx = Array.prototype.indexOf.call(cards, entry.target);
            setTimeout(function() {
              entry.target.classList.add('eco-card-visible');
            }, idx * 80);
            obs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15 });
      cards.forEach(function(c) { obs.observe(c); });
    } else {
      cards.forEach(function(c) { c.classList.add('eco-card-visible'); });
    }
  }

  setTimeout(drawEcoLines, 600);
  setTimeout(function() { drawEcoLines(); onEcoCardHover(); animateEcoCards(); }, 1500);

  var _ecoT;
  window.addEventListener('resize', function() {
    clearTimeout(_ecoT);
    _ecoT = setTimeout(drawEcoLines, 120);
  });

  /* ---- Testimonial Slider ---- */
  (function() {
    var wrap = document.querySelector('.testimonial-slider-wrap');
    if (!wrap) return;

    var track = wrap.querySelector('.testimonial-slider-track');
    var slides = wrap.querySelectorAll('.testimonial-slide');
    var prevBtn = wrap.querySelector('.ts-arrow-prev');
    var nextBtn = wrap.querySelector('.ts-arrow-next');
    var dotsContainer = wrap.querySelector('.ts-dots');
    var counterEl = wrap.querySelector('.ts-counter');

    var slideCount = slides.length;
    var current = 0;
    var autoPlayTimer = null;
    var slidesPerView = getSlidesPerView();
    var autoPlayInterval = 5000;
    var isDragging = false;
    var dragStartX = 0;
    var dragOffset = 0;
    var isHovered = false;

    function getSlidesPerView() {
      if (window.innerWidth <= 768) return 1;
      if (window.innerWidth <= 992) return 2;
      return 3;
    }

    var maxIndex = Math.max(0, slideCount - slidesPerView);

    function buildDots() {
      if (!dotsContainer) return;
      dotsContainer.innerHTML = '';
      var dotCount = maxIndex + 1;
      for (var i = 0; i < dotCount; i++) {
        var dot = document.createElement('button');
        dot.className = 'ts-dot' + (i === current ? ' active' : '');
        dot.setAttribute('type', 'button');
        dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
        dot.addEventListener('click', function(idx) {
          return function() { goTo(idx, true); };
        }(i));
        dotsContainer.appendChild(dot);
      }
    }

    function goTo(index, userAction) {
      if (index < 0) index = 0;
      if (index > maxIndex) index = maxIndex;
      if (index === current) return;
      current = index;
      var offset = -(current * (100 / slidesPerView));
      track.style.transform = 'translateX(' + offset + '%)';
      prevBtn.disabled = current === 0;
      nextBtn.disabled = current >= maxIndex;
      var dots = dotsContainer.querySelectorAll('.ts-dot');
      for (var i = 0; i < dots.length; i++) {
        dots[i].classList.toggle('active', i === current);
      }
      if (counterEl) counterEl.innerHTML = (current + 1) + ' / <span id="tsTotal">' + slideCount + '</span>';
    }

    function startAutoPlay() {
      stopAutoPlay();
      if (isHovered) return;
      autoPlayTimer = setInterval(function() {
        if (current < maxIndex) {
          goTo(current + 1, false);
        } else {
          goTo(0, false);
        }
      }, autoPlayInterval);
    }

    function stopAutoPlay() {
      if (autoPlayTimer) {
        clearInterval(autoPlayTimer);
        autoPlayTimer = null;
      }
    }

    /* Drag / Swipe */
    function onDragStart(e) {
      isDragging = true;
      dragStartX = e.type.indexOf('touch') === 0 ? e.touches[0].clientX : e.clientX;
      track.style.transition = 'none';
      wrap.classList.add('ts-dragging');
    }
    function onDragMove(e) {
      if (!isDragging) return;
      var x = e.type.indexOf('touch') === 0 ? e.touches[0].clientX : e.clientX;
      dragOffset = x - dragStartX;
      var baseOffset = -(current * (100 / slidesPerView));
      var dragPercent = (dragOffset / wrap.offsetWidth) * 100;
      track.style.transform = 'translateX(' + (baseOffset + dragPercent) + '%)';
    }
    function onDragEnd() {
      if (!isDragging) return;
      isDragging = false;
      track.style.transition = '';
      wrap.classList.remove('ts-dragging');
      var threshold = 60;
      if (dragOffset < -threshold && current < maxIndex) {
        goTo(current + 1, true);
      } else if (dragOffset > threshold && current > 0) {
        goTo(current - 1, true);
      } else {
        goTo(current, true);
      }
      dragOffset = 0;
      if (!isHovered) startAutoPlay();
    }

    track.addEventListener('mousedown', onDragStart);
    window.addEventListener('mousemove', onDragMove);
    window.addEventListener('mouseup', onDragEnd);
    track.addEventListener('touchstart', onDragStart, { passive: true });
    window.addEventListener('touchmove', onDragMove, { passive: true });
    window.addEventListener('touchend', onDragEnd);

    /* Keyboard */
    function onKeyDown(e) {
      if (e.key === 'ArrowLeft') { goTo(current - 1, true); stopAutoPlay(); startAutoPlay(); }
      if (e.key === 'ArrowRight') { goTo(current + 1, true); stopAutoPlay(); startAutoPlay(); }
    }
    wrap.addEventListener('keydown', onKeyDown);
    wrap.setAttribute('tabindex', '0');

    /* Hover */
    wrap.addEventListener('mouseenter', function() { isHovered = true; stopAutoPlay(); });
    wrap.addEventListener('mouseleave', function() { isHovered = false; startAutoPlay(); });

    /* Buttons */
    if (prevBtn) prevBtn.addEventListener('click', function() { stopAutoPlay(); goTo(current - 1, true); if (!isHovered) startAutoPlay(); });
    if (nextBtn) nextBtn.addEventListener('click', function() { stopAutoPlay(); goTo(current + 1, true); if (!isHovered) startAutoPlay(); });

    function onResize() {
      var newSpv = getSlidesPerView();
      if (newSpv !== slidesPerView) {
        slidesPerView = newSpv;
        maxIndex = Math.max(0, slideCount - slidesPerView);
        if (current > maxIndex) current = maxIndex;
        buildDots();
        goTo(current, true);
      }
    }

    var resizeTimer;
    window.addEventListener('resize', function() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(onResize, 150);
    });

    maxIndex = Math.max(0, slideCount - slidesPerView);
    buildDots();
    startAutoPlay();
  })();

  });

/* ---- Particle Canvas Background ---- */
(function() {
  var state = {
    max: 70,
    canvas: null,
    context: null,
    particles: [],
    colors: ['#FF5507', '#070E14', '#070E14', '#070E14', '#070E14', '#070E14']
  };

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  function sample(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function randomFromArray(arr) {
    return sample(shuffle(arr));
  }

  function Particle(id) {
    this.id = id;
    this.type = randomizeType();
    this.coords = {
      x: Math.round(Math.random() * state.canvas.width),
      y: Math.round(Math.random() * state.canvas.height)
    };
    this.velocity = {
      x: (Math.random() < 0.5 ? -1 : 1) * (Math.random() * 0.7),
      y: (Math.random() < 0.5 ? -1 : 1) * (Math.random() * 0.7)
    };
    this.alpha = 0.1;
    this.hex = randomFromArray(state.colors);
    this.color = hexToRGBA(this.hex, this.alpha);
    this.strokeWidth = Math.random() * (Math.random() > 0.5 ? 1.5 : 2.5);

    switch(this.type) {
      case 'bubble':
        this.diameter = getCircleDiameter();
        break;
      case 'line':
        this.angle = Math.atan2(this.coords.y, this.coords.x);
        this.length = randomFromArray([5, 7, 3, 10]);
        this.rotateSpeed = randomFromArray([10, 30, 60, 120]);
        this.rotateClockwise = Math.random() < 0.5;
        break;
    }
  }

  function getCircleDiameter() {
    var d = 0;
    while (d < 2) { d = (Math.random() * 7) * 2; }
    return d;
  }

  function randomizeType() {
    var types = Array(4).fill('bubble');
    types.push('line');
    return randomFromArray(types);
  }

  function hexToRGBA(hex, alpha) {
    var h = hex.replace('#', '');
    var r = parseInt(h.substring(0, 2), 16);
    var g = parseInt(h.substring(2, 4), 16);
    var b = parseInt(h.substring(4, 6), 16);
    return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
  }

  Particle.prototype.update = function() {
    if (this.alpha < 1) {
      this.alpha += 0.01;
      this.color = hexToRGBA(this.hex, this.alpha);
    }
    this.coords.x += this.velocity.x;
    this.coords.y += this.velocity.y;
    if (this.type === 'line') {
      var angle = Math.PI / this.rotateSpeed;
      this.angle += this.rotateClockwise ? -Math.abs(angle) : Math.abs(angle);
    }
    return this.withinBounds();
  };

  Particle.prototype.withinBounds = function() {
    var boundX = (state.canvas.width / 2) + 5;
    var boundY = (state.canvas.height / 2) + 5;
    var x = this.coords.x / 2;
    var y = this.coords.y / 2;
    return !((x > boundX || x < -5) || (y > boundY || y < -5));
  };

  Particle.prototype.draw = function() {
    state.context.lineWidth = this.strokeWidth;
    state.context.strokeStyle = this.color;
    state.context.save();
    switch (this.type) {
      case 'line':
        state.context.translate(this.coords.x / 2, this.coords.y / 2);
        state.context.rotate(this.angle);
        state.context.beginPath();
        state.context.moveTo(-this.length / 2, 0);
        state.context.lineTo(this.length / 2, 0);
        break;
      case 'bubble':
        state.context.beginPath();
        state.context.arc(this.coords.x, this.coords.y, this.diameter, 0, Math.PI * 2, false);
        break;
    }
    state.context.stroke();
    state.context.restore();
  };

  function updateCanvasSize() {
    state.canvas.width = state.canvas.parentNode.offsetWidth * 2;
    state.canvas.height = state.canvas.parentNode.offsetHeight * 2;
    state.canvas.style.width = state.canvas.parentNode.offsetWidth + 'px';
    state.canvas.style.height = state.canvas.parentNode.offsetHeight + 'px';
  }

  var pids = 0;

  function generate() {
    if (state.particles.length < state.max) {
      for (var i = state.particles.length; i < state.max; i++) {
        state.particles.push(new Particle(pids++));
      }
    }
  }

  function update() {
    if (state.particles.length < state.max - 5) generate();
    state.particles = state.particles.filter(function(p) { return p.update(); });
    state.context.clearRect(0, 0, state.canvas.width, state.canvas.height);
    state.particles.forEach(function(p) { p.draw(); });
    requestAnimationFrame(update);
  }

  function initParticles() {
    state.canvas = document.querySelector('#canvas-particles');
    if (!state.canvas) return;
    state.context = state.canvas.getContext('2d');
    updateCanvasSize();
    generate();
    update();
    window.addEventListener('resize', updateCanvasSize);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initParticles);
  } else {
    initParticles();
  }
})();

/* ---- Cart Quantity Controls (Global) ---- */
function changeQty(productId, delta) {
  var form = document.getElementById('qtyForm' + productId);
  if (!form) return;
  var input = form.querySelector('input[name="quantity"]');
  if (input) {
    var val = parseInt(input.value, 10) + delta;
    val = Math.max(1, Math.min(99, val));
    input.value = val;
    form.submit();
  }
}
