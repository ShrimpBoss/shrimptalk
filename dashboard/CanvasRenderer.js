/**
 * Simplified CanvasRenderer for Three.js r128
 * Basic triangle rasterization for fallback when WebGL is not available
 */
(function() {
  THREE.CanvasRenderer = function(parameters) {
    parameters = parameters || {};
    const _this = this;
    let _context;
    const _canvas = parameters.canvas || document.createElement('canvas');
    let _canvasWidth, _canvasHeight;
    let _canvasWidthHalf, _canvasHeightHalf;
    const _clearColor = new THREE.Color(0x000000);
    const _clearAlpha = parameters.alpha === true ? 0 : 1;
    const _projector = new THREE.Projector();
    
    this.domElement = _canvas;
    this.autoClear = true;
    this.autoSort = true;
    this.autoUpdateMatrix = true;
    
    this.info = { render: { vertices: 0, faces: 0 } };
    
    this.setSize = function(width, height) {
      _canvas.width = width;
      _canvas.height = height;
      _canvasWidth = _canvas.width;
      _canvasHeight = _canvas.height;
      _canvasWidthHalf = Math.floor(_canvasWidth / 2);
      _canvasHeightHalf = Math.floor(_canvasHeight / 2);
      _context.setTransform(1, 0, 0, -1, _canvasWidthHalf, _canvasHeightHalf);
    };
    
    this.setClearColor = function(color, alpha) {
      _clearColor.set(color);
      _clearAlpha = alpha !== undefined ? alpha : 1;
    };
    
    this.clear = function() {
      _context.setTransform(1, 0, 0, -1, _canvasWidthHalf, _canvasHeightHalf);
      _context.clearRect(-_canvasWidthHalf, -_canvasHeightHalf, _canvasWidth, _canvasHeight);
      if (_clearAlpha > 0) {
        _context.fillStyle = 'rgba(' + Math.floor(_clearColor.r * 255) + ',' + Math.floor(_clearColor.g * 255) + ',' + Math.floor(_clearColor.b * 255) + ',' + _clearAlpha + ')';
        _context.fillRect(-_canvasWidthHalf, -_canvasHeightHalf, _canvasWidth, _canvasHeight);
      }
      _context.globalCompositeOperation = 'source-over';
      _context.lineWidth = 1;
      _context.lineCap = 'butt';
      _context.lineJoin = 'miter';
      _context.strokeStyle = '#000000';
      _context.fillStyle = '#000000';
    };
    
    this.render = function(scene, camera) {
      if (camera.autoUpdateMatrix !== false) camera.updateMatrixWorld();
      if (scene.matrixAutoUpdate) scene.updateMatrixWorld();
      
      const _renderData = _projector.projectScene(scene, camera, this.autoSort, this.autoSort);
      const _elements = _renderData.elements;
      
      console.log('🦐 CanvasRenderer: 场景对象数量:', _renderData.objects ? _renderData.objects.length : 'undefined');
      console.log('🦐 CanvasRenderer: 渲染元素数量:', _elements.length);
      if (_elements.length > 0) {
        console.log('🦐 CanvasRenderer: 第一个元素类型:', _elements[0].constructor.name);
      }
      
      this.clear();
      
      let renderedFaces = 0;
      for (let e = 0, el = _elements.length; e < el; e++) {
        const element = _elements[e];
        const material = element.material;
        if (material === undefined || material.opacity === 0) continue;
        
        if (element instanceof THREE.RenderableFace) {
          renderFace3(element, material);
          renderedFaces++;
        }
      }
      
      console.log('🦐 CanvasRenderer: 实际渲染面数:', renderedFaces);
    };
    
    function renderFace3(element, material) {
      const v1 = element.v1;
      const v2 = element.v2;
      const v3 = element.v3;
      
      if (!v1.visible || !v2.visible || !v3.visible) return;
      
      const x1 = v1.positionScreen.x;
      const y1 = v1.positionScreen.y;
      const x2 = v2.positionScreen.x;
      const y2 = v2.positionScreen.y;
      const x3 = v3.positionScreen.x;
      const y3 = v3.positionScreen.y;
      
      _context.beginPath();
      _context.moveTo(x1, y1);
      _context.lineTo(x2, y2);
      _context.lineTo(x3, y3);
      _context.closePath();
      
      const color = material.color;
      if (!color) {
        _context.fillStyle = '#FF6B6B';
      } else {
        _context.fillStyle = '#' + color.getHexString();
      }
      
      if (material.transparent && material.opacity !== undefined) {
        _context.globalAlpha = material.opacity;
      }
      
      _context.fill();
      _context.globalAlpha = 1;
    }
    
    // Initialize canvas context
    _context = _canvas.getContext('2d');
    _context.setTransform(1, 0, 0, -1, 0, 0);
  };
  
  THREE.CanvasRenderer.prototype = {
    constructor: THREE.CanvasRenderer
  };
})();
