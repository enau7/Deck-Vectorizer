/**
 * VectorGraph.js
 * A library for visualising named 2D vectors as an interactive spring-physics graph.
 *
 * Usage:
 *   const graph = new VectorGraph('#canvas', nodes, options);
 *   graph.start();
 *
 * Node format:
 *   {
 *     "card-name": {
 *       position: [x, y],          // required – 2D target position (any scale)
 *       image:    "url-or-dataurl", // optional – image drawn inside the node circle
 *       color:    "#hex",           // optional – outline / ring color
 *       label:    "My Label",       // optional – overrides key as display label
 *       radius:   40,               // optional – per-node radius in px
 *       connections: ["other-key"], // optional – explicit edge list
 *       data:     { ... }           // optional – arbitrary metadata (not rendered)
 *     },
 *     ...
 *   }
 *
 * Options (all optional):
 *   {
 *     width:           number,   // canvas width  (default: container width)
 *     height:          number,   // canvas height (default: 600)
 *     padding:         number,   // px padding around the layout (default: 80)
 *     springK:         number,   // spring constant toward target (default: 0.06)
 *     damping:         number,   // velocity damping per frame   (default: 0.82)
 *     repulsion:       number,   // repulsion strength           (default: 8000)
 *     defaultRadius:   number,   // default node radius px       (default: 36)
 *     defaultColor:    string,   // default ring color           (default: "#7F77DD")
 *     ringWidth:       number,   // ring stroke width px         (default: 3)
 *     edgeColor:       string,   // edge stroke color            (default: "#999")
 *     edgeWidth:       number,   // edge stroke width px         (default: 1)
 *     edgeOpacity:     number,   // edge opacity 0–1             (default: 0.35)
 *     labelFont:       string,   // CSS font string              (default: "13px sans-serif")
 *     labelColor:      string,   // label fill color             (default: "#333")
 *     labelBelow:      boolean,  // draw label below node        (default: true)
 *     backgroundColor: string,   // canvas fill (default: "transparent")
 *     autoEdges:       boolean,  // auto-connect nearby nodes    (default: true)
 *     autoEdgeThresh:  number,   // max normalised distance for auto-edge (default: 0.4)
 *     onNodeClick:     fn(key, nodeData) => void
 *     onHover:         fn(key|null, nodeData|null) => void
 *   }
 */

(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory();
  } else {
    root.VectorGraph = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // ── helpers ────────────────────────────────────────────────────────────────

  function defaults(obj, defs) {
    const out = Object.assign({}, defs);
    for (const k in obj) if (obj[k] !== undefined) out[k] = obj[k];
    return out;
  }

  function euclidSq(a, b) {
    const dx = a[0] - b[0], dy = a[1] - b[1];
    return dx * dx + dy * dy;
  }

  // ── VectorGraph class ──────────────────────────────────────────────────────

  function VectorGraph(containerOrSelector, nodeMap, userOptions) {

    // ── resolve container ──
    this._container =
      typeof containerOrSelector === 'string'
        ? document.querySelector(containerOrSelector)
        : containerOrSelector;

    if (!this._container) throw new Error('VectorGraph: container not found');

    // ── options ──
    const containerW = this._container.clientWidth || 800;
    const containerH = this._container.clientHeight || 600;

    this.opts = defaults(userOptions || {}, {
      width:           containerW,
      height:          containerH,
      padding:         80,
      springK:         0.06,
      damping:         0.82,
      repulsion:       8000,
      defaultRadius:   36,
      defaultColor:    '#7F77DD',
      ringWidth:       3,
      edgeColor:       '#999999',
      edgeWidth:       1,
      edgeOpacity:     0.35,
      labelFont:       '13px sans-serif',
      labelColor:      '#333333',
      labelBelow:      true,
      drawLabel:       true,
      backgroundColor: 'transparent',
      autoEdges:       true,
      autoEdgeThresh:  0.4,
      onNodeClick:     null,
      onHover:         null,
    });

    // ── build internal node list ──
    this._keys = Object.keys(nodeMap);
    if (this._keys.length === 0) throw new Error('VectorGraph: nodeMap is empty');

    // normalise positions into canvas px
    this._rawPositions = this._keys.map(k => nodeMap[k].position);
    this._targetPx     = this._normalisePositions(this._rawPositions);

    this._nodes = this._keys.map((k, i) => {
      const def = nodeMap[k];
      return {
        key:      k,
        label:    def.label   !== undefined ? def.label   : k,
        color:    def.color   !== undefined ? def.color   : this.opts.defaultColor,
        radius:   def.radius  !== undefined ? def.radius  : this.opts.defaultRadius,
        image:    def.image   !== undefined ? def.image   : null,
        connections: def.connections || null,
        data:     def.data    || {},
        // physics state (canvas px)
        x:        this._targetPx[i].x + (Math.random() - 0.5) * this.opts.width, //* 0.05,
        y:        this._targetPx[i].y + (Math.random() - 0.5) * this.opts.height, //* 0.05,
        vx:       0,
        vy:       0,
        // loaded image element
        _img:     null,
        _imgLoaded: false,
      };
    });

    // ── build edge list ──
    this._edges = this._buildEdges(nodeMap);

    // ── preload images ──
    this._loadImages();

    // ── canvas setup ──
    this._canvas = document.createElement('canvas');
    this._canvas.width  = this.opts.width;
    this._canvas.height = this.opts.height;
    this._canvas.style.display = 'block';
    this._canvas.style.cursor  = 'default';
    this._container.innerHTML = '';
    this._container.appendChild(this._canvas);
    this._ctx = this._canvas.getContext('2d');

    // ── interaction state ──
    this._hoveredIdx = -1;
    this._dragIdx    = -1;
    this._dragOffX   = 0;
    this._dragOffY   = 0;
    this._raf        = null;
    this._running    = false;

    // ── bind events ──
    this._bindEvents();
  }

  // ── normalise positions to canvas space ──

  VectorGraph.prototype._normalisePositions = function (positions) {
    let mnX = Infinity, mxX = -Infinity, mnY = Infinity, mxY = -Infinity;
    for (const [x, y] of positions) {
      mnX = Math.min(mnX, x); mxX = Math.max(mxX, x);
      mnY = Math.min(mnY, y); mxY = Math.max(mxY, y);
    }
    const pad = this.opts.padding;
    const W   = this.opts.width, H = this.opts.height;
    const sx  = (W - 2 * pad) / Math.max(mxX - mnX, 0.001);
    const sy  = (H - 2 * pad) / Math.max(mxY - mnY, 0.001);
    const sc  = Math.min(sx, sy);
    const ox  = (W - (mxX + mnX) * sx) / 2;
    const oy  = (H - (mxY + mnY) * sy) / 2;
    return positions.map(([x, y]) => ({ x: x * sx + ox, y: y * sy + oy }));
  };

  // ── build edge list ──

  VectorGraph.prototype._buildEdges = function (nodeMap) {
    const edges = [];
    const seen  = new Set();
    const n     = this._keys.length;

    const addEdge = (i, j) => {
      const key = i < j ? `${i},${j}` : `${j},${i}`;
      if (!seen.has(key)) { seen.add(key); edges.push({ i, j }); }
    };

    // explicit connections declared in node data
    for (let i = 0; i < n; i++) {
      const conns = this._nodes[i].connections;
      if (!conns) continue;
      for (const targetKey of conns) {
        const j = this._keys.indexOf(targetKey);
        if (j >= 0) addEdge(i, j);
      }
    }

    // auto-edges based on embedding position proximity
    if (this.opts.autoEdges) {
      const tgt    = this._targetPx;
      const W      = this.opts.width, H = this.opts.height;
      const maxD2  = (this.opts.autoEdgeThresh * Math.min(W, H)) ** 2;
      for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
          if (euclidSq([tgt[i].x, tgt[i].y], [tgt[j].x, tgt[j].y]) <= maxD2) {
            addEdge(i, j);
          }
        }
      }
    }

    return edges;
  };

  // ── image preloading ──

  VectorGraph.prototype._loadImages = function () {
    for (const node of this._nodes) {
      if (!node.image) continue;
      const img = new Image();
      img.onload  = () => { node._img = img; node._imgLoaded = true; };
      img.onerror = () => { node._img = null; node._imgLoaded = false; };
      img.src = node.image;
    }
  };

  // ── event binding ──

  VectorGraph.prototype._bindEvents = function () {
    const c = this._canvas;

    const getCanvasPos = (e) => {
      const r  = c.getBoundingClientRect();
      const sc = c.width / r.width;
      const touch = e.touches ? e.touches[0] : e;
      return {
        x: (touch.clientX - r.left) * sc,
        y: (touch.clientY - r.top)  * sc,
      };
    };

    const hitNode = (mx, my) => {
      for (let i = this._nodes.length - 1; i >= 0; i--) {
        const nd  = this._nodes[i];
        const dx  = nd.x - mx, dy = nd.y - my;
        if (dx * dx + dy * dy < (nd.radius + 4) ** 2) return i;
      }
      return -1;
    };

    c.addEventListener('mousemove', (e) => {
      const { x, y } = getCanvasPos(e);
      if (this._dragIdx >= 0) {
        this._nodes[this._dragIdx].x  = x + this._dragOffX;
        this._nodes[this._dragIdx].y  = y + this._dragOffY;
        this._nodes[this._dragIdx].vx = 0;
        this._nodes[this._dragIdx].vy = 0;
        return;
      }
      const idx = hitNode(x, y);
      if (idx !== this._hoveredIdx) {
        this._hoveredIdx = idx;
        c.style.cursor   = idx >= 0 ? 'pointer' : 'default';
        if (this.opts.onHover) {
          this.opts.onHover(
            idx >= 0 ? this._nodes[idx].key  : null,
            idx >= 0 ? this._nodes[idx].data : null,
          );
        }
      }
    });

    c.addEventListener('mousedown', (e) => {
      const { x, y } = getCanvasPos(e);
      const idx = hitNode(x, y);
      if (idx >= 0) {
        this._dragIdx  = idx;
        this._dragOffX = this._nodes[idx].x - x;
        this._dragOffY = this._nodes[idx].y - y;
        e.preventDefault();
      }
    });

    c.addEventListener('mouseup', () => { this._dragIdx = -1; });
    c.addEventListener('mouseleave', () => {
      this._dragIdx    = -1;
      this._hoveredIdx = -1;
      c.style.cursor   = 'default';
    });

    c.addEventListener('click', (e) => {
      if (!this.opts.onNodeClick) return;
      const { x, y } = getCanvasPos(e);
      const idx = hitNode(x, y);
      if (idx >= 0) this.opts.onNodeClick(this._nodes[idx].key, this._nodes[idx].data);
    });

    // touch support
    c.addEventListener('touchstart', (e) => {
      const { x, y } = getCanvasPos(e);
      const idx = hitNode(x, y);
      if (idx >= 0) {
        this._dragIdx  = idx;
        this._dragOffX = this._nodes[idx].x - x;
        this._dragOffY = this._nodes[idx].y - y;
      }
    }, { passive: true });

    c.addEventListener('touchmove', (e) => {
      if (this._dragIdx < 0) return;
      const { x, y } = getCanvasPos(e);
      this._nodes[this._dragIdx].x  = x + this._dragOffX;
      this._nodes[this._dragIdx].y  = y + this._dragOffY;
      this._nodes[this._dragIdx].vx = 0;
      this._nodes[this._dragIdx].vy = 0;
    }, { passive: true });

    c.addEventListener('touchend', () => { this._dragIdx = -1; });
  };

  // ── physics step ──

  VectorGraph.prototype._step = function () {
    const nodes = this._nodes;
    const n     = nodes.length;
    const K     = this.opts.springK;
    const REP   = this.opts.repulsion;
    const DAMP  = this.opts.damping;

    // spring each node toward its target
    for (let i = 0; i < n; i++) {
      if (this._dragIdx === i) continue;
      nodes[i].vx += (this._targetPx[i].x - nodes[i].x) * K;
      nodes[i].vy += (this._targetPx[i].y - nodes[i].y) * K;
    }

    // pairwise repulsion
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx  = nodes[i].x - nodes[j].x;
        const dy  = nodes[i].y - nodes[j].y;
        const d2  = dx * dx + dy * dy + 1;
        const inv = 1 / Math.sqrt(d2);
        const f   = REP / d2;
        const fx  = f * dx * inv, fy = f * dy * inv;
        if (this._dragIdx !== i) { nodes[i].vx += fx; nodes[i].vy += fy; }
        if (this._dragIdx !== j) { nodes[j].vx -= fx; nodes[j].vy -= fy; }
      }
    }

    // integrate + damp
    for (let i = 0; i < n; i++) {
      if (this._dragIdx === i) continue;
      nodes[i].vx *= DAMP;
      nodes[i].vy *= DAMP;
      nodes[i].x  += nodes[i].vx;
      nodes[i].y  += nodes[i].vy;
    }
  };

  // ── draw ──

  VectorGraph.prototype._draw = function () {
    const ctx  = this._ctx;
    const W    = this.opts.width, H = this.opts.height;
    const nodes = this._nodes;
    const o    = this.opts;

    ctx.clearRect(0, 0, W, H);

    if (o.backgroundColor !== 'transparent') {
      ctx.fillStyle = o.backgroundColor;
      ctx.fillRect(0, 0, W, H);
    }

    // ── edges ──
    ctx.save();
    ctx.strokeStyle = o.edgeColor;
    ctx.lineWidth   = o.edgeWidth;
    ctx.globalAlpha = o.edgeOpacity;

    for (const { i, j } of this._edges) {
      ctx.beginPath();
      ctx.moveTo(nodes[i].x, nodes[i].y);
      ctx.lineTo(nodes[j].x, nodes[j].y);
      ctx.stroke();
    }
    ctx.restore();

    // ── nodes ──
    for (let idx = 0; idx < nodes.length; idx++) {
      const nd     = nodes[idx];
      const isHov  = idx === this._hoveredIdx;
      const r      = nd.radius;

      ctx.save();

      // outer glow on hover
      if (isHov) {
        ctx.shadowColor = nd.color;
        ctx.shadowBlur  = 14;
      }

      // colored ring
      ctx.beginPath();
      ctx.arc(nd.x, nd.y, r + o.ringWidth, 0, Math.PI * 2);
      ctx.fillStyle = nd.color;
      ctx.fill();

      // clip circle for image / fill
      ctx.beginPath();
      ctx.arc(nd.x, nd.y, r, 0, Math.PI * 2);
      ctx.save();
      ctx.clip();

      if (nd._imgLoaded && nd._img) {
        // draw image inside circle
        ctx.drawImage(nd._img, nd.x - r, nd.y - r, r * 2, r * 2);
      } else {
        // filled circle with lighter version of ring color
        ctx.fillStyle = _lighten(nd.color, 0.6);
        ctx.fillRect(nd.x - r, nd.y - r, r * 2, r * 2);
        // initials
        ctx.fillStyle    = nd.color;
        ctx.font         = `bold ${Math.round(r * 0.55)}px sans-serif`;
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';

        const shorthand = _shorthand(nd.label);
        if (shorthand.length == 1) {
          ctx.fillText(shorthand[0], nd.x, nd.y);
        } else {
          ctx.fillText(shorthand[0], nd.x, nd.y - r * 0.3);
          ctx.fillText(shorthand[1], nd.x, nd.y + r * 0.3);
        }
      }

      ctx.restore(); // un-clip

      ctx.restore(); // un-shadow

      // ── label ──
      if (this.opts.drawLabel === false) continue;
      const labelY = o.labelBelow
        ? nd.y + r + o.ringWidth + 14
        : nd.y - r - o.ringWidth - 6;

      ctx.font         = o.labelFont;
      ctx.textAlign    = 'center';
      ctx.textBaseline = o.labelBelow ? 'top' : 'bottom';

      // background pill for legibility
      const tw = ctx.measureText(nd.label).width;
      ctx.fillStyle   = 'rgba(255,255,255,0.75)';
      ctx.beginPath();
      ctx.roundRect(nd.x - tw / 2 - 5, labelY - 2, tw + 10, 18, 4);
      ctx.fill();

      ctx.fillStyle = o.labelColor;
      ctx.fillText(nd.label, nd.x, labelY);
    }
  };

  // ── loop ──

  VectorGraph.prototype._loop = function () {
    this._step();
    this._draw();
    if (this._running) this._raf = requestAnimationFrame(this._loop.bind(this));
  };

  // ── public API ────────────────────────────────────────────────────────────

  /** Start the animation loop. */
  VectorGraph.prototype.start = function () {
    if (this._running) return this;
    this._running = true;
    this._raf     = requestAnimationFrame(this._loop.bind(this));
    return this;
  };

  /** Stop the animation loop. */
  VectorGraph.prototype.stop = function () {
    this._running = false;
    if (this._raf) cancelAnimationFrame(this._raf);
    return this;
  };

  /** Redraw a single static frame (useful when stopped). */
  VectorGraph.prototype.render = function () {
    this._draw();
    return this;
  };

  /**
   * Update the node map at runtime.
   * Existing nodes keep their current positions; new ones are scattered randomly.
   */
  VectorGraph.prototype.update = function (nodeMap) {
    const newKeys   = Object.keys(nodeMap);
    const positions = newKeys.map(k => nodeMap[k].position);
    const newTargets= this._normalisePositions(positions);
    const oldMap    = {};
    for (const nd of this._nodes) oldMap[nd.key] = nd;

    this._keys    = newKeys;
    this._targetPx= newTargets;
    this._nodes   = newKeys.map((k, i) => {
      const def  = nodeMap[k];
      const prev = oldMap[k];
      const nd   = {
        key:    k,
        label:  def.label  !== undefined ? def.label  : k,
        color:  def.color  !== undefined ? def.color  : this.opts.defaultColor,
        radius: def.radius !== undefined ? def.radius : this.opts.defaultRadius,
        image:  def.image  !== undefined ? def.image  : null,
        connections: def.connections || null,
        data:   def.data || {},
        x:    prev ? prev.x : newTargets[i].x + (Math.random() - 0.5) * this.opts.width,
        y:    prev ? prev.y : newTargets[i].y + (Math.random() - 0.5) * this.opts.height,
        vx:   prev ? prev.vx : 0,
        vy:   prev ? prev.vy : 0,
        _img: null,
        _imgLoaded: false,
      };
      if (prev && prev._imgLoaded) { nd._img = prev._img; nd._imgLoaded = true; }
      return nd;
    });

    this._edges = this._buildEdges(nodeMap);
    this._loadImages();
    return this;
  };

  /** Scatter all nodes back to random positions (re-triggers the spring animation). */
  VectorGraph.prototype.scatter = function () {
    for (let i = 0; i < this._nodes.length; i++) {
      this._nodes[i].x  = this._targetPx[i].x + (Math.random() - 0.5) * this.opts.width  * 0.8;
      this._nodes[i].y  = this._targetPx[i].y + (Math.random() - 0.5) * this.opts.height * 0.8;
      this._nodes[i].vx = 0;
      this._nodes[i].vy = 0;
    }
    return this;
  };

  /** Resize the canvas. Re-normalises target positions. */
  VectorGraph.prototype.resize = function (width, height) {
    this.opts.width  = width;
    this.opts.height = height;
    this._canvas.width  = width;
    this._canvas.height = height;
    this._targetPx = this._normalisePositions(this._rawPositions);
    return this;
  };

  /** Set an option at runtime. */
  VectorGraph.prototype.setOption = function (key, value) {
    this.opts[key] = value;
    return this;
  };

  // ── private utils ─────────────────────────────────────────────────────────

  function _shorthand(str) {
    if (!str) return '?';
    return str.trim().split(/\s+/).slice(0, 2).map(w => w.slice(0, 3).toUpperCase());
  }

  function _lighten(hex, amount) {
    // parse hex, blend toward white
    let r = 0, g = 0, b = 0;
    if (hex && hex[0] === '#') {
      const h = hex.slice(1);
      if (h.length === 3) {
        r = parseInt(h[0] + h[0], 16);
        g = parseInt(h[1] + h[1], 16);
        b = parseInt(h[2] + h[2], 16);
      } else {
        r = parseInt(h.slice(0, 2), 16);
        g = parseInt(h.slice(2, 4), 16);
        b = parseInt(h.slice(4, 6), 16);
      }
    }
    r = Math.round(r + (255 - r) * amount);
    g = Math.round(g + (255 - g) * amount);
    b = Math.round(b + (255 - b) * amount);
    return `rgb(${r},${g},${b})`;
  }

  return VectorGraph;
}));
