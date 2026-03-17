/**
 * Projector.js for Three.js (from r128)
 * https://github.com/mrdoob/three.js/blob/r128/examples/js/renderers/Projector.js
 */
(function() {
  'use strict';
  
  console.log('🦐 Loading Projector.js...');
  
  // 确保 THREE 已加载
  if (typeof THREE === 'undefined') {
    console.error('🦐 THREE.js not loaded!');
    return;
  }
  
  class RenderableObject {
    constructor() {
      this.id = 0;
      this.object = null;
      this.z = 0;
      this.renderOrder = 0;
    }
  }

  class RenderableVertex {
    constructor() {
      this.position = new THREE.Vector3();
      this.positionWorld = new THREE.Vector3();
      this.positionCamera = new THREE.Vector3();
      this.normal = new THREE.Vector3();
      this.normalWorld = new THREE.Vector3();
      this.normalCamera = new THREE.Vector3();
      this.color = new THREE.Color();
      this.uv = new THREE.Vector2();
      this.visible = true;
    }
    copy(vertex) {
      this.positionWorld.copy(vertex.positionWorld);
      this.positionCamera.copy(vertex.positionCamera);
      this.position.copy(vertex.position);
      this.normalWorld.copy(vertex.normalWorld);
      this.normalCamera.copy(vertex.normalCamera);
      this.normal.copy(vertex.normal);
      this.color.copy(vertex.color);
      this.uv.copy(vertex.uv);
      this.visible = vertex.visible;
    }
  }

  class RenderableFace {
    constructor() {
      this.id = 0;
      this.v1 = new RenderableVertex();
      this.v2 = new RenderableVertex();
      this.v3 = new RenderableVertex();
      this.normalModel = new THREE.Vector3();
      this.vertexNormalsModel = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
      this.vertexNormalsLength = 0;
      this.color = new THREE.Color();
      this.material = null;
      this.uvs = [[]];
      this.z = 0;
      this.renderOrder = 0;
    }
  }

  class RenderableLine {
    constructor() {
      this.id = 0;
      this.v1 = new RenderableVertex();
      this.v2 = new RenderableVertex();
      this.vertexColors = [new THREE.Color(), new THREE.Color()];
      this.material = null;
      this.z = 0;
      this.renderOrder = 0;
    }
  }

  class RenderableSprite {
    constructor() {
      this.id = 0;
      this.object = null;
      this.x = 0;
      this.y = 0;
      this.z = 0;
      this.rotation = 0;
      this.scale = new THREE.Vector2();
      this.material = null;
      this.renderOrder = 0;
    }
  }

  THREE.Projector = function() {
    console.log('🦐 Projector initialized');
    
    let _object, _objectCount, _objectPool = [], _objectPoolLength = 0,
      _vertex, _vertexCount, _vertexPool = [], _vertexPoolLength = 0,
      _face, _faceCount, _facePool = [], _facePoolLength = 0,
      _line, _lineCount, _linePool = [], _linePoolLength = 0,
      _sprite, _spriteCount, _spritePool = [], _spritePoolLength = 0,
      _renderData = { objects: [], lights: [], elements: [] };

    const _vector3 = new THREE.Vector3(), _vector4 = new THREE.Vector4();
    const _clipBox = new THREE.Box3(new THREE.Vector3(-1, -1, -1), new THREE.Vector3(1, 1, 1));
    const _boundingBox = new THREE.Box3();
    const _points3 = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
    const _viewMatrix = new THREE.Matrix4();
    const _viewProjectionMatrix = new THREE.Matrix4();
    let _modelMatrix, _modelViewMatrix = new THREE.Matrix4();
    const _normalMatrix = new THREE.Matrix3();
    const _frustum = new THREE.Frustum();

    this.projectVector = function(vector, camera) {
      vector.project(camera);
    };

    this.unprojectVector = function(vector, camera) {
      vector.unproject(camera);
    };

    const projectObject = function(object) {
      if (object.visible === false) return;
      if (object instanceof THREE.Light) {
        _renderData.lights.push(object);
      } else if (object instanceof THREE.Mesh || object instanceof THREE.Line || object instanceof THREE.Points) {
        if (object.frustumCulled && object.frustum && _frustum.intersectsObject(object) === false) return;
        addObject(object);
      } else if (object instanceof THREE.Sprite) {
        _object = getNextSpriteInPool();
        _object.object = object;
        if (object.renderOrder !== 0) _object.renderOrder = object.renderOrder;
        _object.x = 0;
        _object.y = 0;
        _object.z = 0;
        _object.rotation = object.rotation;
        _object.scale.copy(object.scale);
        _object.material = object.material;
        _renderData.objects.push(_object);
      }
    };

    const addObject = function(object) {
      _object = getNextObjectInPool();
      _object.id = object.id;
      _object.object = object;
      if (object.renderOrder !== 0) _object.renderOrder = object.renderOrder;
      _object.z = 0;
      _renderData.objects.push(_object);
    };

    this.projectScene = function(scene, camera, sortObjects, sortElements) {
      _faceCount = 0;
      _lineCount = 0;
      _spriteCount = 0;
      _renderData.objects.length = 0;
      _renderData.lights.length = 0;
      _renderData.elements.length = 0;

      _viewMatrix.copy(camera.matrixWorldInverse);
      _viewProjectionMatrix.multiplyMatrices(camera.projectionMatrix, _viewMatrix);
      _frustum.setFromProjectionMatrix(_viewProjectionMatrix);

      projectObject(scene);

      if (sortObjects === true) _renderData.objects.sort(painterSort);

      for (let o = 0, ol = _renderData.objects.length; o < ol; o++) {
        const object = _renderData.objects[o].object;
        const objectRenderOrder = _renderData.objects[o].renderOrder;
        if (object.matrixAutoUpdate) object.updateMatrixWorld();
        _modelMatrix = object.matrixWorld;
        _vertexCount = 0;

        if (object instanceof THREE.Mesh) {
          let vertices = object.geometry.vertices;
          const faces = object.geometry.faces;
          const normals = object.geometry.faceNormals || [];
          const materials = object.material;
          _normalMatrix.getNormalMatrix(_modelMatrix);

          if (vertices !== undefined) {
            for (let v = 0, vl = vertices.length; v < vl; v++) {
              let vertex = vertices[v];
              _vector3.copy(vertex);
              _vector3.applyMatrix4(_modelMatrix);
              const vertexWorld = _vector3.clone();
              const vertexCamera = vertexWorld.clone().applyMatrix4(_viewMatrix);
              const vertexScreen = vertexCamera.clone().applyMatrix4(camera.projectionMatrix);
              const visible = vertexScreen.w > 0;
              _vertex = getNextVertexInPool();
              _vertex.id = v;
              _vertex.positionScreen.copy(vertexScreen);
              _vertex.positionWorld.copy(vertexWorld);
              _vertex.positionCamera.copy(vertexCamera);
              _vertex.visible = visible;
            }
          }

          for (let f = 0, fl = faces.length; f < fl; f++) {
            const face = faces[f];
            let material = materials instanceof Array ? materials[0] : materials;
            if (material === undefined) continue;
            const side = material.side;
            faceVertices = [face.a, face.b, face.c];
            _face = getNextFaceInPool();
            _face.id = f;
            
            if (normals[f]) {
              _face.normalModel.copy(normals[f]);
            }
            if (face.vertexNormals && face.vertexNormals.length === 3) {
              _face.vertexNormalsModel.copy(face.vertexNormals);
              _face.vertexNormalsLength = 3;
            } else {
              _face.vertexNormalsModel = [_face.normalModel.clone()];
              _face.vertexNormalsLength = 1;
            }
            _face.normalModel.applyMatrix3(_normalMatrix).normalize();
            for (let n = 0; n < _face.vertexNormalsModel.length; n++) {
              _face.vertexNormalsModel[n].applyMatrix3(_normalMatrix).normalize();
            }
            _face.vertexColorsModel = face.vertexColors || [];
            _face.material = material;
            
            for (let i = 0; i < 3; i++) {
              const n = faceVertices[i];
              if (_vertexPool[n]) {
                _points3[i].copy(_vertexPool[n].positionWorld);
                _face.v[i].copy(_vertexPool[n]);
              }
            }
            
            _face.v1.positionCamera.applyMatrix4(_viewMatrix);
            _face.v2.positionCamera.applyMatrix4(_viewMatrix);
            _face.v3.positionCamera.applyMatrix4(_viewMatrix);
            
            _face.z = (_face.v1.positionCamera.z + _face.v2.positionCamera.z + _face.v3.positionCamera.z) / 3;
            _face.renderOrder = objectRenderOrder;
            _renderData.elements.push(_face);
          }
        }
      }

      if (sortElements === true) _renderData.elements.sort(painterSort);
      return _renderData;
    };

    function getNextObjectInPool() {
      if (_objectPoolLength === 0) {
        const object = new RenderableObject();
        _objectPool.push(object);
        _objectPoolLength++;
        return _objectPool[--_objectPoolLength];
      }
      return _objectPool[--_objectPoolLength];
    }

    function getNextVertexInPool() {
      if (_vertexPoolLength === 0) {
        const vertex = new RenderableVertex();
        _vertexPool.push(vertex);
        _vertexPoolLength++;
        return _vertexPool[--_vertexPoolLength];
      }
      return _vertexPool[--_vertexPoolLength];
    }

    function getNextFaceInPool() {
      if (_facePoolLength === 0) {
        const face = new RenderableFace();
        _facePool.push(face);
        _facePoolLength++;
        return _facePool[--_facePoolLength];
      }
      return _facePool[--_facePoolLength];
    }

    function getNextSpriteInPool() {
      if (_spritePoolLength === 0) {
        const sprite = new RenderableSprite();
        _spritePool.push(sprite);
        _spritePoolLength++;
        return _spritePool[--_spritePoolLength];
      }
      return _spritePool[--_spritePoolLength];
    }

    function painterSort(a, b) {
      if (a.renderOrder !== b.renderOrder) return a.renderOrder - b.renderOrder;
      return b.z - a.z;
    }
  };
  
  console.log('🦐 THREE.Projector loaded:', typeof THREE.Projector);
})();
