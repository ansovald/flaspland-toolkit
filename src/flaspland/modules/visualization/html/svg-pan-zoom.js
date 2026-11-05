// Based on svg-pan-zoom v3.6.2
// https://github.com/bumbu/svg-pan-zoom
// This browser bundle contains the control icons, viewport, SVG utilities, and public API.
!(function loadBundle (moduleDefinitions, moduleCache, entryModuleIds) {
  function loadModule (moduleId, isEntryPoint) {
    if (!moduleCache[moduleId]) {
      if (!moduleDefinitions[moduleId]) {
        var nodeRequire = 'function' == typeof require && require
        if (!isEntryPoint && nodeRequire) return nodeRequire(moduleId, !0)
        if (previousBundleRequire) return previousBundleRequire(moduleId, !0)
        var missingModuleError = new Error("Cannot find module '" + moduleId + "'")
        throw ((missingModuleError.code = 'MODULE_NOT_FOUND'), missingModuleError)
      }
      var moduleRecord = (moduleCache[moduleId] = { exports: {} })
      moduleDefinitions[moduleId][0].call(
        moduleRecord.exports,
        function requireFromModule (requestedModuleName) {
          return loadModule(
            moduleDefinitions[moduleId][1][requestedModuleName] ||
              requestedModuleName
          )
        },
        moduleRecord,
        moduleRecord.exports,
        loadBundle,
        moduleDefinitions,
        moduleCache,
        entryModuleIds
      )
    }
    return moduleCache[moduleId].exports
  }
  for (
    var previousBundleRequire = 'function' == typeof require && require,
      entryIndex = 0;
    entryIndex < entryModuleIds.length;
    entryIndex++
  )
    loadModule(entryModuleIds[entryIndex])
  return loadModule
})(
  {
    // Adds the optional zoom controls to the SVG.
    1: [
      function (requireModule, moduleRecord, exports) {
        var svgUtilities = requireModule('./svg-utilities')
        moduleRecord.exports = {
          enable: function (instance) {
            var defsElement = instance.svg.querySelector('defs')
            if (
              (defsElement ||
                ((defsElement = document.createElementNS(svgUtilities.svgNS, 'defs')),
                instance.svg.appendChild(defsElement)),
              !defsElement.querySelector('style#svg-pan-zoom-controls-styles'))
            ) {
              var controlsStyle = document.createElementNS(svgUtilities.svgNS, 'style')
              controlsStyle.setAttribute('id', 'svg-pan-zoom-controls-styles'),
                controlsStyle.setAttribute('type', 'text/css'),
                (controlsStyle.textContent =
                  '.svg-pan-zoom-control { cursor: pointer; fill: black; fill-opacity: 0.333; } .svg-pan-zoom-control:hover { fill-opacity: 0.8; } .svg-pan-zoom-control-background { fill: white; fill-opacity: 0.5; } .svg-pan-zoom-control-background { fill-opacity: 0.8; }'),
                defsElement.appendChild(controlsStyle)
            }
            var controlsGroup = document.createElementNS(svgUtilities.svgNS, 'g')
            controlsGroup.setAttribute('id', 'svg-pan-zoom-controls'),
              controlsGroup.setAttribute(
                'transform',
                'translate(' +
                  (instance.width - 70) +
                  ' ' +
                  (instance.height - 76) +
                  ') scale(0.75)'
              ),
              controlsGroup.setAttribute('class', 'svg-pan-zoom-control'),
              controlsGroup.appendChild(this._createZoomInControl(instance)),
              controlsGroup.appendChild(this._createZoomResetControl(instance)),
              controlsGroup.appendChild(this._createZoomOutControl(instance)),
              instance.svg.appendChild(controlsGroup),
              (instance.controlIcons = controlsGroup)
          },
          _createZoomInControl: function (instance) {
            var controlGroup = document.createElementNS(svgUtilities.svgNS, 'g')
            controlGroup.setAttribute('id', 'svg-pan-zoom-zoom-in'),
              controlGroup.setAttribute('transform', 'translate(30.5 5) scale(0.015)'),
              controlGroup.setAttribute('class', 'svg-pan-zoom-control'),
              controlGroup.addEventListener(
                'click',
                function () {
                  instance.getPublicInstance().zoomIn()
                },
                !1
              ),
              controlGroup.addEventListener(
                'touchstart',
                function () {
                  instance.getPublicInstance().zoomIn()
                },
                !1
              )
            var controlBackground = document.createElementNS(svgUtilities.svgNS, 'rect')
            controlBackground.setAttribute('x', '0'),
              controlBackground.setAttribute('y', '0'),
              controlBackground.setAttribute('width', '1500'),
              controlBackground.setAttribute('height', '1400'),
              controlBackground.setAttribute('class', 'svg-pan-zoom-control-background'),
              controlGroup.appendChild(controlBackground)
            var zoomInIconPath = document.createElementNS(svgUtilities.svgNS, 'path')
            return (
              zoomInIconPath.setAttribute(
                'd',
                'M1280 576v128q0 26 -19 45t-45 19h-320v320q0 26 -19 45t-45 19h-128q-26 0 -45 -19t-19 -45v-320h-320q-26 0 -45 -19t-19 -45v-128q0 -26 19 -45t45 -19h320v-320q0 -26 19 -45t45 -19h128q26 0 45 19t19 45v320h320q26 0 45 19t19 45zM1536 1120v-960 q0 -119 -84.5 -203.5t-203.5 -84.5h-960q-119 0 -203.5 84.5t-84.5 203.5v960q0 119 84.5 203.5t203.5 84.5h960q119 0 203.5 -84.5t84.5 -203.5z'
              ),
              zoomInIconPath.setAttribute('class', 'svg-pan-zoom-control-element'),
              controlGroup.appendChild(zoomInIconPath),
              controlGroup
            )
          },
          _createZoomResetControl: function (instance) {
            var controlGroup = document.createElementNS(svgUtilities.svgNS, 'g')
            controlGroup.setAttribute('id', 'svg-pan-zoom-reset-pan-zoom'),
              controlGroup.setAttribute('transform', 'translate(5 35) scale(0.4)'),
              controlGroup.setAttribute('class', 'svg-pan-zoom-control'),
              controlGroup.addEventListener(
                'click',
                function () {
                  instance.getPublicInstance().reset()
                },
                !1
              ),
              controlGroup.addEventListener(
                'touchstart',
                function () {
                  instance.getPublicInstance().reset()
                },
                !1
              )
            var controlBackground = document.createElementNS(svgUtilities.svgNS, 'rect')
            controlBackground.setAttribute('x', '2'),
              controlBackground.setAttribute('y', '2'),
              controlBackground.setAttribute('width', '182'),
              controlBackground.setAttribute('height', '58'),
              controlBackground.setAttribute('class', 'svg-pan-zoom-control-background'),
              controlGroup.appendChild(controlBackground)
            var resetIconLetter = document.createElementNS(svgUtilities.svgNS, 'path')
            resetIconLetter.setAttribute(
              'd',
              'M33.051,20.632c-0.742-0.406-1.854-0.609-3.338-0.609h-7.969v9.281h7.769c1.543,0,2.701-0.188,3.473-0.562c1.365-0.656,2.048-1.953,2.048-3.891C35.032,22.757,34.372,21.351,33.051,20.632z'
            ),
              resetIconLetter.setAttribute('class', 'svg-pan-zoom-control-element'),
              controlGroup.appendChild(resetIconLetter)
            var resetIconBackground = document.createElementNS(svgUtilities.svgNS, 'path')
            return (
              resetIconBackground.setAttribute(
                'd',
                'M170.231,0.5H15.847C7.102,0.5,0.5,5.708,0.5,11.84v38.861C0.5,56.833,7.102,61.5,15.847,61.5h154.384c8.745,0,15.269-4.667,15.269-10.798V11.84C185.5,5.708,178.976,0.5,170.231,0.5z M42.837,48.569h-7.969c-0.219-0.766-0.375-1.383-0.469-1.852c-0.188-0.969-0.289-1.961-0.305-2.977l-0.047-3.211c-0.03-2.203-0.41-3.672-1.142-4.406c-0.732-0.734-2.103-1.102-4.113-1.102h-7.05v13.547h-7.055V14.022h16.524c2.361,0.047,4.178,0.344,5.45,0.891c1.272,0.547,2.351,1.352,3.234,2.414c0.731,0.875,1.31,1.844,1.737,2.906s0.64,2.273,0.64,3.633c0,1.641-0.414,3.254-1.242,4.84s-2.195,2.707-4.102,3.363c1.594,0.641,2.723,1.551,3.387,2.73s0.996,2.98,0.996,5.402v2.32c0,1.578,0.063,2.648,0.19,3.211c0.19,0.891,0.635,1.547,1.333,1.969V48.569z M75.579,48.569h-26.18V14.022h25.336v6.117H56.454v7.336h16.781v6H56.454v8.883h19.125V48.569z M104.497,46.331c-2.44,2.086-5.887,3.129-10.34,3.129c-4.548,0-8.125-1.027-10.731-3.082s-3.909-4.879-3.909-8.473h6.891c0.224,1.578,0.662,2.758,1.316,3.539c1.196,1.422,3.246,2.133,6.15,2.133c1.739,0,3.151-0.188,4.236-0.562c2.058-0.719,3.087-2.055,3.087-4.008c0-1.141-0.504-2.023-1.512-2.648c-1.008-0.609-2.607-1.148-4.796-1.617l-3.74-0.82c-3.676-0.812-6.201-1.695-7.576-2.648c-2.328-1.594-3.492-4.086-3.492-7.477c0-3.094,1.139-5.664,3.417-7.711s5.623-3.07,10.036-3.07c3.685,0,6.829,0.965,9.431,2.895c2.602,1.93,3.966,4.73,4.093,8.402h-6.938c-0.128-2.078-1.057-3.555-2.787-4.43c-1.154-0.578-2.587-0.867-4.301-0.867c-1.907,0-3.428,0.375-4.565,1.125c-1.138,0.75-1.706,1.797-1.706,3.141c0,1.234,0.561,2.156,1.682,2.766c0.721,0.406,2.25,0.883,4.589,1.43l6.063,1.43c2.657,0.625,4.648,1.461,5.975,2.508c2.059,1.625,3.089,3.977,3.089,7.055C108.157,41.624,106.937,44.245,104.497,46.331z M139.61,48.569h-26.18V14.022h25.336v6.117h-18.281v7.336h16.781v6h-16.781v8.883h19.125V48.569z M170.337,20.14h-10.336v28.43h-7.266V20.14h-10.383v-6.117h27.984V20.14z'
              ),
              resetIconBackground.setAttribute('class', 'svg-pan-zoom-control-element'),
              controlGroup.appendChild(resetIconBackground),
              controlGroup
            )
          },
          _createZoomOutControl: function (instance) {
            var controlGroup = document.createElementNS(svgUtilities.svgNS, 'g')
            controlGroup.setAttribute('id', 'svg-pan-zoom-zoom-out'),
              controlGroup.setAttribute('transform', 'translate(30.5 70) scale(0.015)'),
              controlGroup.setAttribute('class', 'svg-pan-zoom-control'),
              controlGroup.addEventListener(
                'click',
                function () {
                  instance.getPublicInstance().zoomOut()
                },
                !1
              ),
              controlGroup.addEventListener(
                'touchstart',
                function () {
                  instance.getPublicInstance().zoomOut()
                },
                !1
              )
            var controlBackground = document.createElementNS(svgUtilities.svgNS, 'rect')
            controlBackground.setAttribute('x', '0'),
              controlBackground.setAttribute('y', '0'),
              controlBackground.setAttribute('width', '1500'),
              controlBackground.setAttribute('height', '1400'),
              controlBackground.setAttribute('class', 'svg-pan-zoom-control-background'),
              controlGroup.appendChild(controlBackground)
            var zoomOutIconPath = document.createElementNS(svgUtilities.svgNS, 'path')
            return (
              zoomOutIconPath.setAttribute(
                'd',
                'M1280 576v128q0 26 -19 45t-45 19h-896q-26 0 -45 -19t-19 -45v-128q0 -26 19 -45t45 -19h896q26 0 45 19t19 45zM1536 1120v-960q0 -119 -84.5 -203.5t-203.5 -84.5h-960q-119 0 -203.5 84.5t-84.5 203.5v960q0 119 84.5 203.5t203.5 84.5h960q119 0 203.5 -84.5 t84.5 -203.5z'
              ),
              zoomOutIconPath.setAttribute('class', 'svg-pan-zoom-control-element'),
              controlGroup.appendChild(zoomOutIconPath),
              controlGroup
            )
          },
          disable: function (instance) {
            instance.controlIcons &&
              (instance.controlIcons.parentNode.removeChild(instance.controlIcons),
              (instance.controlIcons = null))
          }
        }
      },
      { './svg-utilities': 5 }
    ],
    // Tracks viewport geometry and schedules SVG transformation updates.
    2: [
      function (requireModule, moduleRecord, exports) {
        function ShadowViewport (viewportElement, options) {
          this.init(viewportElement, options)
        }
        var svgUtilities = requireModule('./svg-utilities'),
          utilities = requireModule('./utilities')
        ;(ShadowViewport.prototype.init = function (viewportElement, options) {
          ;(this.viewport = viewportElement),
            (this.options = options),
            (this.originalState = { zoom: 1, x: 0, y: 0 }),
            (this.activeState = { zoom: 1, x: 0, y: 0 }),
            (this.updateCTMCached = utilities.proxy(this.updateCTM, this)),
            (this.requestAnimationFrame = utilities.createRequestAnimationFrame(
              this.options.refreshRate
            )),
            (this.viewBox = { x: 0, y: 0, width: 0, height: 0 }),
            this.cacheViewBox()
          var o = this.processCTM()
          this.setCTM(o), this.updateCTM()
        }),
          (ShadowViewport.prototype.cacheViewBox = function () {
            var viewBoxAttribute = this.options.svg.getAttribute('viewBox')
            if (viewBoxAttribute) {
              var viewBoxValues = viewBoxAttribute
                .split(/[\s\,]/)
                .filter(function (t) {
                  return t
                })
                .map(parseFloat)
              ;(this.viewBox.x = viewBoxValues[0]),
                (this.viewBox.y = viewBoxValues[1]),
                (this.viewBox.width = viewBoxValues[2]),
                (this.viewBox.height = viewBoxValues[3])
              var fitZoom = Math.min(
                this.options.width / this.viewBox.width,
                this.options.height / this.viewBox.height
              )
              ;(this.activeState.zoom = fitZoom),
                (this.activeState.x =
                  (this.options.width - this.viewBox.width * fitZoom) / 2),
                (this.activeState.y =
                  (this.options.height - this.viewBox.height * fitZoom) / 2),
                this.updateCTMOnNextFrame(),
                this.options.svg.removeAttribute('viewBox')
            } else this.simpleViewBoxCache()
          }),
          (ShadowViewport.prototype.simpleViewBoxCache = function () {
            var viewportBounds = this.viewport.getBBox()
            ;(this.viewBox.x = viewportBounds.x),
              (this.viewBox.y = viewportBounds.y),
              (this.viewBox.width = viewportBounds.width),
              (this.viewBox.height = viewportBounds.height)
          }),
          (ShadowViewport.prototype.getViewBox = function () {
            return utilities.extend({}, this.viewBox)
          }),
          (ShadowViewport.prototype.processCTM = function () {
            var fitZoom,
              transformationMatrix = this.getCTM()
            ;(this.options.fit || this.options.contain) &&
              ((fitZoom = this.options.fit
                ? Math.min(
                    this.options.width / this.viewBox.width,
                    this.options.height / this.viewBox.height
                  )
                : Math.max(
                    this.options.width / this.viewBox.width,
                    this.options.height / this.viewBox.height
                  )),
              (transformationMatrix.a = fitZoom),
              (transformationMatrix.d = fitZoom),
              (transformationMatrix.e = -this.viewBox.x * fitZoom),
              (transformationMatrix.f = -this.viewBox.y * fitZoom))
            if (this.options.center) {
              var centeredOffsetX =
                  0.5 *
                  (this.options.width -
                    (this.viewBox.width + 2 * this.viewBox.x) *
                      transformationMatrix.a),
                centeredOffsetY =
                  0.5 *
                  (this.options.height -
                    (this.viewBox.height + 2 * this.viewBox.y) *
                      transformationMatrix.a)
              ;(transformationMatrix.e = centeredOffsetX),
                (transformationMatrix.f = centeredOffsetY)
            }
            return (
              (this.originalState.zoom = transformationMatrix.a),
              (this.originalState.x = transformationMatrix.e),
              (this.originalState.y = transformationMatrix.f),
              transformationMatrix
            )
          }),
          (ShadowViewport.prototype.getOriginalState = function () {
            return utilities.extend({}, this.originalState)
          }),
          (ShadowViewport.prototype.getState = function () {
            return utilities.extend({}, this.activeState)
          }),
          (ShadowViewport.prototype.getZoom = function () {
            return this.activeState.zoom
          }),
          (ShadowViewport.prototype.getRelativeZoom = function () {
            return this.activeState.zoom / this.originalState.zoom
          }),
          (ShadowViewport.prototype.computeRelativeZoom = function (zoom) {
            return zoom / this.originalState.zoom
          }),
          (ShadowViewport.prototype.getPan = function () {
            return { x: this.activeState.x, y: this.activeState.y }
          }),
          (ShadowViewport.prototype.getCTM = function () {
            var transformationMatrix = this.options.svg.createSVGMatrix()
            return (
              (transformationMatrix.a = this.activeState.zoom),
              (transformationMatrix.b = 0),
              (transformationMatrix.c = 0),
              (transformationMatrix.d = this.activeState.zoom),
              (transformationMatrix.e = this.activeState.x),
              (transformationMatrix.f = this.activeState.y),
              transformationMatrix
            )
          }),
          (ShadowViewport.prototype.setCTM = function (transformationMatrix) {
            var zoomChanged = this.isZoomDifferent(transformationMatrix),
              panChanged = this.isPanDifferent(transformationMatrix)
            if (zoomChanged || panChanged) {
              if (
                (zoomChanged &&
                  (!1 ===
                  this.options.beforeZoom(
                    this.getRelativeZoom(),
                    this.computeRelativeZoom(transformationMatrix.a)
                  )
                    ? ((transformationMatrix.a = transformationMatrix.d =
                        this.activeState.zoom),
                      (zoomChanged = !1))
                    : (this.updateCache(transformationMatrix),
                      this.options.onZoom(this.getRelativeZoom()))),
                panChanged)
              ) {
                var panResult = this.options.beforePan(this.getPan(), {
                    x: transformationMatrix.e,
                    y: transformationMatrix.f
                  }),
                  keepCurrentX = !1,
                  keepCurrentY = !1
                !1 === panResult
                  ? ((transformationMatrix.e = this.getPan().x),
                    (transformationMatrix.f = this.getPan().y),
                    (keepCurrentX = keepCurrentY = !0))
                  : utilities.isObject(panResult) &&
                    (!1 === panResult.x
                      ? ((transformationMatrix.e = this.getPan().x),
                        (keepCurrentX = !0))
                      : utilities.isNumber(panResult.x) &&
                        (transformationMatrix.e = panResult.x),
                    !1 === panResult.y
                      ? ((transformationMatrix.f = this.getPan().y),
                        (keepCurrentY = !0))
                      : utilities.isNumber(panResult.y) &&
                        (transformationMatrix.f = panResult.y)),
                  (keepCurrentX && keepCurrentY) ||
                  !this.isPanDifferent(transformationMatrix)
                    ? (panChanged = !1)
                    : (this.updateCache(transformationMatrix),
                      this.options.onPan(this.getPan()))
              }
              ;(zoomChanged || panChanged) && this.updateCTMOnNextFrame()
            }
          }),
          (ShadowViewport.prototype.isZoomDifferent = function (matrix) {
            return this.activeState.zoom !== matrix.a
          }),
          (ShadowViewport.prototype.isPanDifferent = function (matrix) {
            return this.activeState.x !== matrix.e || this.activeState.y !== matrix.f
          }),
          (ShadowViewport.prototype.updateCache = function (matrix) {
            ;(this.activeState.zoom = matrix.a),
              (this.activeState.x = matrix.e),
              (this.activeState.y = matrix.f)
          }),
          (ShadowViewport.prototype.pendingUpdate = !1),
          (ShadowViewport.prototype.updateCTMOnNextFrame = function () {
            this.pendingUpdate ||
              ((this.pendingUpdate = !0),
              this.requestAnimationFrame.call(window, this.updateCTMCached))
          }),
          (ShadowViewport.prototype.updateCTM = function () {
            var transformationMatrix = this.getCTM()
            svgUtilities.setCTM(this.viewport, transformationMatrix, this.defs),
              (this.pendingUpdate = !1),
              this.options.onUpdatedCTM &&
                this.options.onUpdatedCTM(transformationMatrix)
          }),
          (moduleRecord.exports = function (viewportElement, options) {
            return new ShadowViewport(viewportElement, options)
          })
      },
      { './svg-utilities': 5, './utilities': 7 }
    ],
    // Exposes the package through AMD, CommonJS, or the browser global.
    3: [
      function (requireModule, moduleRecord, exports) {
        var browserWindow,
          svgPanZoom = requireModule('./svg-pan-zoom.js')
        ;(browserWindow = window),
          document,
          'function' == typeof define && define.amd
            ? define('svg-pan-zoom', function () {
                return svgPanZoom
              })
            : void 0 !== moduleRecord &&
              moduleRecord.exports &&
              ((moduleRecord.exports = svgPanZoom),
              (browserWindow.svgPanZoom = svgPanZoom))
      },
      { './svg-pan-zoom.js': 4 }
    ],
    // Implements SVG panning, zooming, event handling, and the chainable API.
    4: [
      function (requireModule, moduleRecord, exports) {
        function SvgPanZoom (svgElement, options) {
          this.init(svgElement, options)
        }
        var wheelEvents = requireModule('./uniwheel'),
          controlIcons = requireModule('./control-icons'),
          utilities = requireModule('./utilities'),
          svgUtilities = requireModule('./svg-utilities'),
          createViewport = requireModule('./shadow-viewport'),
          defaultOptions = {
            viewportSelector: '.svg-pan-zoom_viewport',
            panEnabled: !0,
            controlIconsEnabled: !1,
            zoomEnabled: !0,
            dblClickZoomEnabled: !0,
            mouseWheelZoomEnabled: !0,
            preventMouseEventsDefault: !0,
            zoomScaleSensitivity: 0.1,
            minZoom: 0.5,
            maxZoom: 10,
            fit: !0,
            contain: !1,
            center: !0,
            refreshRate: 'auto',
            beforeZoom: null,
            onZoom: null,
            beforePan: null,
            onPan: null,
            customEventsHandler: null,
            eventsListenerElement: null,
            onUpdatedCTM: null
          },
          passiveListenerOptions = { passive: !0 }
        ;(SvgPanZoom.prototype.init = function (svgElement, options) {
          var instance = this
          ;(this.svg = svgElement),
            (this.defs = svgElement.querySelector('defs')),
            svgUtilities.setupSvgAttributes(this.svg),
            (this.options = utilities.extend(
              utilities.extend({}, defaultOptions),
              options
            )),
            (this.state = 'none')
          var svgSize = svgUtilities.getBoundingClientRectNormalized(svgElement)
          ;(this.width = svgSize.width),
            (this.height = svgSize.height),
            (this.viewport = createViewport(
              svgUtilities.getOrCreateViewport(
                this.svg,
                this.options.viewportSelector
              ),
              {
                svg: this.svg,
                width: this.width,
                height: this.height,
                fit: this.options.fit,
                contain: this.options.contain,
                center: this.options.center,
                refreshRate: this.options.refreshRate,
                beforeZoom: function (previousZoom, nextZoom) {
                  if (instance.viewport && instance.options.beforeZoom)
                    return instance.options.beforeZoom(previousZoom, nextZoom)
                },
                onZoom: function (zoom) {
                  if (instance.viewport && instance.options.onZoom)
                    return instance.options.onZoom(zoom)
                },
                beforePan: function (currentPan, nextPan) {
                  if (instance.viewport && instance.options.beforePan)
                    return instance.options.beforePan(currentPan, nextPan)
                },
                onPan: function (pan) {
                  if (instance.viewport && instance.options.onPan)
                    return instance.options.onPan(pan)
                },
                onUpdatedCTM: function (transformationMatrix) {
                  if (instance.viewport && instance.options.onUpdatedCTM)
                    return instance.options.onUpdatedCTM(transformationMatrix)
                }
              }
            ))
          var publicInstance = this.getPublicInstance()
          publicInstance.setBeforeZoom(this.options.beforeZoom),
            publicInstance.setOnZoom(this.options.onZoom),
            publicInstance.setBeforePan(this.options.beforePan),
            publicInstance.setOnPan(this.options.onPan),
            publicInstance.setOnUpdatedCTM(this.options.onUpdatedCTM),
            this.options.controlIconsEnabled && controlIcons.enable(this),
            (this.lastMouseWheelEventTime = Date.now()),
            this.setupHandlers()
        }),
          (SvgPanZoom.prototype.setupHandlers = function () {
            var instance = this,
              previousInputEvent = null
            if (
              ((this.eventListeners = {
                mousedown: function (event) {
                  var handled = instance.handleMouseDown(
                    event,
                    previousInputEvent
                  )
                  return (previousInputEvent = event), handled
                },
                touchstart: function (event) {
                  var handled = instance.handleMouseDown(
                    event,
                    previousInputEvent
                  )
                  return (previousInputEvent = event), handled
                },
                mouseup: function (event) {
                  return instance.handleMouseUp(event)
                },
                touchend: function (event) {
                  return instance.handleMouseUp(event)
                },
                mousemove: function (event) {
                  return instance.handleMouseMove(event)
                },
                touchmove: function (event) {
                  return instance.handleMouseMove(event)
                },
                mouseleave: function (event) {
                  return instance.handleMouseUp(event)
                },
                touchleave: function (event) {
                  return instance.handleMouseUp(event)
                },
                touchcancel: function (event) {
                  return instance.handleMouseUp(event)
                }
              }),
              null != this.options.customEventsHandler)
            ) {
              this.options.customEventsHandler.init({
                svgElement: this.svg,
                eventsListenerElement: this.options.eventsListenerElement,
                instance: this.getPublicInstance()
              })
              var haltedEventNames =
                this.options.customEventsHandler.haltEventListeners
              if (haltedEventNames && haltedEventNames.length)
                for (
                  var eventIndex = haltedEventNames.length - 1;
                  0 <= eventIndex;
                  eventIndex--
                )
                  this.eventListeners.hasOwnProperty(
                    haltedEventNames[eventIndex]
                  ) &&
                    delete this.eventListeners[haltedEventNames[eventIndex]]
            }
            for (var eventName in this.eventListeners)
              (this.options.eventsListenerElement || this.svg).addEventListener(
                eventName,
                this.eventListeners[eventName],
                !this.options.preventMouseEventsDefault &&
                  passiveListenerOptions
              )
            this.options.mouseWheelZoomEnabled &&
              ((this.options.mouseWheelZoomEnabled = !1),
              this.enableMouseWheelZoom())
          }),
          (SvgPanZoom.prototype.enableMouseWheelZoom = function () {
            if (!this.options.mouseWheelZoomEnabled) {
              var instance = this
              this.wheelListener = function (event) {
                return instance.handleMouseWheel(event)
              }
              var allowDefaultEvents = !this.options.preventMouseEventsDefault
              wheelEvents.on(
                this.options.eventsListenerElement || this.svg,
                this.wheelListener,
                allowDefaultEvents
              ),
                (this.options.mouseWheelZoomEnabled = !0)
            }
          }),
          (SvgPanZoom.prototype.disableMouseWheelZoom = function () {
            if (this.options.mouseWheelZoomEnabled) {
              var allowDefaultEvents = !this.options.preventMouseEventsDefault
              wheelEvents.off(
                this.options.eventsListenerElement || this.svg,
                this.wheelListener,
                allowDefaultEvents
              ),
                (this.options.mouseWheelZoomEnabled = !1)
            }
          }),
          (SvgPanZoom.prototype.handleMouseWheel = function (event) {
            if (this.options.zoomEnabled && 'none' === this.state) {
              this.options.preventMouseEventsDefault &&
                (event.preventDefault
                  ? event.preventDefault()
                  : (event.returnValue = !1))
              var wheelDelta = event.deltaY || 1,
                elapsedSinceWheelEvent =
                  Date.now() - this.lastMouseWheelEventTime,
                wheelSensitivity = 3 + Math.max(0, 30 - elapsedSinceWheelEvent)
              ;(this.lastMouseWheelEventTime = Date.now()),
                'deltaMode' in event &&
                  0 === event.deltaMode &&
                  event.wheelDelta &&
                  (wheelDelta =
                    0 === event.deltaY
                      ? 0
                      : Math.abs(event.wheelDelta) / event.deltaY),
                (wheelDelta =
                  -0.3 < wheelDelta && wheelDelta < 0.3
                    ? wheelDelta
                    : ((0 < wheelDelta ? 1 : -1) *
                        Math.log(Math.abs(wheelDelta) + 10)) /
                      wheelSensitivity)
              var screenToSvgMatrix = this.svg.getScreenCTM().inverse(),
                zoomCenter = svgUtilities
                  .getEventPoint(event, this.svg)
                  .matrixTransform(screenToSvgMatrix),
                zoomFactor = Math.pow(
                  1 + this.options.zoomScaleSensitivity,
                  -1 * wheelDelta
                )
              this.zoomAtPoint(zoomFactor, zoomCenter)
            }
          }),
          (SvgPanZoom.prototype.zoomAtPoint = function (
            zoomFactor,
            svgPoint,
            useRelativeZoom
          ) {
            var originalViewportState = this.viewport.getOriginalState()
            useRelativeZoom
              ? ((zoomFactor = Math.max(
                  this.options.minZoom * originalViewportState.zoom,
                  Math.min(
                    this.options.maxZoom * originalViewportState.zoom,
                    zoomFactor
                  )
                )),
                (zoomFactor /= this.getZoom()))
              : this.getZoom() * zoomFactor <
                this.options.minZoom * originalViewportState.zoom
              ? (zoomFactor =
                  (this.options.minZoom * originalViewportState.zoom) /
                  this.getZoom())
              : this.getZoom() * zoomFactor >
                  this.options.maxZoom * originalViewportState.zoom &&
                (zoomFactor =
                  (this.options.maxZoom * originalViewportState.zoom) /
                  this.getZoom())
            var currentMatrix = this.viewport.getCTM(),
              pointInViewport = svgPoint.matrixTransform(
                currentMatrix.inverse()
              ),
              pointCenteredScale = this.svg
                .createSVGMatrix()
                .translate(pointInViewport.x, pointInViewport.y)
                .scale(zoomFactor)
                .translate(-pointInViewport.x, -pointInViewport.y),
              nextMatrix = currentMatrix.multiply(pointCenteredScale)
            nextMatrix.a !== currentMatrix.a &&
              this.viewport.setCTM(nextMatrix)
          }),
          (SvgPanZoom.prototype.zoom = function (zoomFactor, useRelativeZoom) {
            this.zoomAtPoint(
              zoomFactor,
              svgUtilities.getSvgCenterPoint(this.svg, this.width, this.height),
              useRelativeZoom
            )
          }),
          (SvgPanZoom.prototype.publicZoom = function (
            zoomFactor,
            useRelativeZoom
          ) {
            useRelativeZoom &&
              (zoomFactor = this.computeFromRelativeZoom(zoomFactor)),
              this.zoom(zoomFactor, useRelativeZoom)
          }),
          (SvgPanZoom.prototype.publicZoomAtPoint = function (
            zoomFactor,
            point,
            useRelativeZoom
          ) {
            if (
              (useRelativeZoom &&
                (zoomFactor = this.computeFromRelativeZoom(zoomFactor)),
              'SVGPoint' !== utilities.getType(point))
            ) {
              if (!('x' in point && 'y' in point))
                throw new Error('Given point is invalid')
              point = svgUtilities.createSVGPoint(this.svg, point.x, point.y)
            }
            this.zoomAtPoint(zoomFactor, point, useRelativeZoom)
          }),
          (SvgPanZoom.prototype.getZoom = function () {
            return this.viewport.getZoom()
          }),
          (SvgPanZoom.prototype.getRelativeZoom = function () {
            return this.viewport.getRelativeZoom()
          }),
          (SvgPanZoom.prototype.computeFromRelativeZoom = function (relativeZoom) {
            return relativeZoom * this.viewport.getOriginalState().zoom
          }),
          (SvgPanZoom.prototype.resetZoom = function () {
            var originalViewportState = this.viewport.getOriginalState()
            this.zoom(originalViewportState.zoom, !0)
          }),
          (SvgPanZoom.prototype.resetPan = function () {
            this.pan(this.viewport.getOriginalState())
          }),
          (SvgPanZoom.prototype.reset = function () {
            this.resetZoom(), this.resetPan()
          }),
          (SvgPanZoom.prototype.handleDblClick = function (event) {
            var zoomFactor
            if (
              (this.options.preventMouseEventsDefault &&
                (event.preventDefault
                  ? event.preventDefault()
                  : (event.returnValue = !1)),
              this.options.controlIconsEnabled) &&
              -1 <
                (event.target.getAttribute('class') || '').indexOf(
                  'svg-pan-zoom-control'
                )
            )
              return !1
            zoomFactor = event.shiftKey
              ? 1 / (2 * (1 + this.options.zoomScaleSensitivity))
              : 2 * (1 + this.options.zoomScaleSensitivity)
            var zoomCenter = svgUtilities
              .getEventPoint(event, this.svg)
              .matrixTransform(this.svg.getScreenCTM().inverse())
            this.zoomAtPoint(zoomFactor, zoomCenter)
          }),
          (SvgPanZoom.prototype.handleMouseDown = function (
            event,
            previousEvent
          ) {
            this.options.preventMouseEventsDefault &&
              (event.preventDefault
                ? event.preventDefault()
                : (event.returnValue = !1)),
              utilities.mouseAndTouchNormalize(event, this.svg),
              this.options.dblClickZoomEnabled &&
              utilities.isDblClick(event, previousEvent)
                ? this.handleDblClick(event)
                : ((this.state = 'pan'),
                  (this.firstEventCTM = this.viewport.getCTM()),
                  (this.stateOrigin = svgUtilities
                    .getEventPoint(event, this.svg)
                    .matrixTransform(this.firstEventCTM.inverse())))
          }),
          (SvgPanZoom.prototype.handleMouseMove = function (event) {
            if (
              (this.options.preventMouseEventsDefault &&
                (event.preventDefault
                  ? event.preventDefault()
                  : (event.returnValue = !1)),
              'pan' === this.state && this.options.panEnabled)
            ) {
              // Transform the drag point with the matrix captured at pointer-down.
              var currentPointer = svgUtilities
                  .getEventPoint(event, this.svg)
                  .matrixTransform(this.firstEventCTM.inverse()),
                translatedMatrix = this.firstEventCTM.translate(
                  currentPointer.x - this.stateOrigin.x,
                  currentPointer.y - this.stateOrigin.y
                )
              this.viewport.setCTM(translatedMatrix)
            }
          }),
          (SvgPanZoom.prototype.handleMouseUp = function (event) {
            this.options.preventMouseEventsDefault &&
              (event.preventDefault
                ? event.preventDefault()
                : (event.returnValue = !1)),
              'pan' === this.state && (this.state = 'none')
          }),
          (SvgPanZoom.prototype.fit = function () {
            var viewBox = this.viewport.getViewBox(),
              fitZoom = Math.min(
                this.width / viewBox.width,
                this.height / viewBox.height
              )
            this.zoom(fitZoom, !0)
          }),
          (SvgPanZoom.prototype.contain = function () {
            var viewBox = this.viewport.getViewBox(),
              containZoom = Math.max(
                this.width / viewBox.width,
                this.height / viewBox.height
              )
            this.zoom(containZoom, !0)
          }),
          (SvgPanZoom.prototype.center = function () {
            var viewBox = this.viewport.getViewBox(),
              horizontalOffset =
                0.5 *
                (this.width -
                  (viewBox.width + 2 * viewBox.x) * this.getZoom()),
              verticalOffset =
                0.5 *
                (this.height -
                  (viewBox.height + 2 * viewBox.y) * this.getZoom())
            this.getPublicInstance().pan({
              x: horizontalOffset,
              y: verticalOffset
            })
          }),
          (SvgPanZoom.prototype.updateBBox = function () {
            this.viewport.simpleViewBoxCache()
          }),
          (SvgPanZoom.prototype.pan = function (panPosition) {
            var transformationMatrix = this.viewport.getCTM()
            ;(transformationMatrix.e = panPosition.x),
              (transformationMatrix.f = panPosition.y),
              this.viewport.setCTM(transformationMatrix)
          }),
          (SvgPanZoom.prototype.panBy = function (panOffset) {
            var transformationMatrix = this.viewport.getCTM()
            ;(transformationMatrix.e += panOffset.x),
              (transformationMatrix.f += panOffset.y),
              this.viewport.setCTM(transformationMatrix)
          }),
          (SvgPanZoom.prototype.getPan = function () {
            var viewportState = this.viewport.getState()
            return { x: viewportState.x, y: viewportState.y }
          }),
          (SvgPanZoom.prototype.resize = function () {
            var svgSize = svgUtilities.getBoundingClientRectNormalized(
              this.svg
            )
            ;(this.width = svgSize.width), (this.height = svgSize.height)
            var viewport = this.viewport
            ;(viewport.options.width = this.width),
              (viewport.options.height = this.height),
              viewport.processCTM(),
              this.options.controlIconsEnabled &&
                (this.getPublicInstance().disableControlIcons(),
                this.getPublicInstance().enableControlIcons())
          }),
          (SvgPanZoom.prototype.destroy = function () {
            var instance = this
            for (var eventName in ((this.beforeZoom = null),
            (this.onZoom = null),
            (this.beforePan = null),
            (this.onPan = null),
            (this.onUpdatedCTM = null) != this.options.customEventsHandler &&
              this.options.customEventsHandler.destroy({
                svgElement: this.svg,
                eventsListenerElement: this.options.eventsListenerElement,
                instance: this.getPublicInstance()
              }),
            this.eventListeners))
              (
                this.options.eventsListenerElement || this.svg
              ).removeEventListener(
                eventName,
                this.eventListeners[eventName],
                !this.options.preventMouseEventsDefault && passiveListenerOptions
              )
            this.disableMouseWheelZoom(),
              this.getPublicInstance().disableControlIcons(),
              this.reset(),
              (instances = instances.filter(function (entry) {
                return entry.svg !== instance.svg
              })),
              delete this.options,
              delete this.viewport,
              delete this.publicInstance,
              delete this.pi,
              (this.getPublicInstance = function () {
                return null
              })
          }),
          (SvgPanZoom.prototype.getPublicInstance = function () {
            var instance = this
            return (
              this.publicInstance ||
                (this.publicInstance = this.pi =
                  {
                    enablePan: function () {
                      return (instance.options.panEnabled = !0), instance.pi
                    },
                    disablePan: function () {
                      return (instance.options.panEnabled = !1), instance.pi
                    },
                    isPanEnabled: function () {
                      return !!instance.options.panEnabled
                    },
                    pan: function (panPosition) {
                      return instance.pan(panPosition), instance.pi
                    },
                    panBy: function (panOffset) {
                      return instance.panBy(panOffset), instance.pi
                    },
                    getPan: function () {
                      return instance.getPan()
                    },
                    setBeforePan: function (beforePanCallback) {
                      return (
                        (instance.options.beforePan =
                          null === beforePanCallback
                            ? null
                            : utilities.proxy(
                                beforePanCallback,
                                instance.publicInstance
                              )),
                        instance.pi
                      )
                    },
                    setOnPan: function (onPanCallback) {
                      return (
                        (instance.options.onPan =
                          null === onPanCallback
                            ? null
                            : utilities.proxy(
                                onPanCallback,
                                instance.publicInstance
                              )),
                        instance.pi
                      )
                    },
                    enableZoom: function () {
                      return (instance.options.zoomEnabled = !0), instance.pi
                    },
                    disableZoom: function () {
                      return (instance.options.zoomEnabled = !1), instance.pi
                    },
                    isZoomEnabled: function () {
                      return !!instance.options.zoomEnabled
                    },
                    enableControlIcons: function () {
                      return (
                        instance.options.controlIconsEnabled ||
                          ((instance.options.controlIconsEnabled = !0), controlIcons.enable(instance)),
                        instance.pi
                      )
                    },
                    disableControlIcons: function () {
                      return (
                        instance.options.controlIconsEnabled &&
                          ((instance.options.controlIconsEnabled = !1), controlIcons.disable(instance)),
                        instance.pi
                      )
                    },
                    isControlIconsEnabled: function () {
                      return !!instance.options.controlIconsEnabled
                    },
                    enableDblClickZoom: function () {
                      return (instance.options.dblClickZoomEnabled = !0), instance.pi
                    },
                    disableDblClickZoom: function () {
                      return (instance.options.dblClickZoomEnabled = !1), instance.pi
                    },
                    isDblClickZoomEnabled: function () {
                      return !!instance.options.dblClickZoomEnabled
                    },
                    enableMouseWheelZoom: function () {
                      return instance.enableMouseWheelZoom(), instance.pi
                    },
                    disableMouseWheelZoom: function () {
                      return instance.disableMouseWheelZoom(), instance.pi
                    },
                    isMouseWheelZoomEnabled: function () {
                      return !!instance.options.mouseWheelZoomEnabled
                    },
                    setZoomScaleSensitivity: function (sensitivity) {
                      return (
                        (instance.options.zoomScaleSensitivity = sensitivity),
                        instance.pi
                      )
                    },
                    setMinZoom: function (minimumZoom) {
                      return (instance.options.minZoom = minimumZoom), instance.pi
                    },
                    setMaxZoom: function (maximumZoom) {
                      return (instance.options.maxZoom = maximumZoom), instance.pi
                    },
                    setBeforeZoom: function (beforeZoomCallback) {
                      return (
                        (instance.options.beforeZoom =
                          null === beforeZoomCallback
                            ? null
                            : utilities.proxy(
                                beforeZoomCallback,
                                instance.publicInstance
                              )),
                        instance.pi
                      )
                    },
                    setOnZoom: function (onZoomCallback) {
                      return (
                        (instance.options.onZoom =
                          null === onZoomCallback
                            ? null
                            : utilities.proxy(
                                onZoomCallback,
                                instance.publicInstance
                              )),
                        instance.pi
                      )
                    },
                    zoom: function (zoomFactor) {
                      return instance.publicZoom(zoomFactor, !0), instance.pi
                    },
                    zoomBy: function (zoomFactor) {
                      return instance.publicZoom(zoomFactor, !1), instance.pi
                    },
                    zoomAtPoint: function (zoomFactor, point) {
                      return (
                        instance.publicZoomAtPoint(zoomFactor, point, !0),
                        instance.pi
                      )
                    },
                    zoomAtPointBy: function (zoomFactor, point) {
                      return (
                        instance.publicZoomAtPoint(zoomFactor, point, !1),
                        instance.pi
                      )
                    },
                    zoomIn: function () {
                      return (
                        this.zoomBy(1 + instance.options.zoomScaleSensitivity), instance.pi
                      )
                    },
                    zoomOut: function () {
                      return (
                        this.zoomBy(1 / (1 + instance.options.zoomScaleSensitivity)),
                        instance.pi
                      )
                    },
                    getZoom: function () {
                      return instance.getRelativeZoom()
                    },
                    setOnUpdatedCTM: function (onUpdatedCTMCallback) {
                      return (
                        (instance.options.onUpdatedCTM =
                          null === onUpdatedCTMCallback
                            ? null
                            : utilities.proxy(
                                onUpdatedCTMCallback,
                                instance.publicInstance
                              )),
                        instance.pi
                      )
                    },
                    resetZoom: function () {
                      return instance.resetZoom(), instance.pi
                    },
                    resetPan: function () {
                      return instance.resetPan(), instance.pi
                    },
                    reset: function () {
                      return instance.reset(), instance.pi
                    },
                    fit: function () {
                      return instance.fit(), instance.pi
                    },
                    contain: function () {
                      return instance.contain(), instance.pi
                    },
                    center: function () {
                      return instance.center(), instance.pi
                    },
                    updateBBox: function () {
                      return instance.updateBBox(), instance.pi
                    },
                    resize: function () {
                      return instance.resize(), instance.pi
                    },
                    getSizes: function () {
                      return {
                        width: instance.width,
                        height: instance.height,
                        realZoom: instance.getZoom(),
                        viewBox: instance.viewport.getViewBox()
                      }
                    },
                    destroy: function () {
                      return instance.destroy(), instance.pi
                    }
                  }),
              this.publicInstance
            )
          })
        var instances = []
        moduleRecord.exports = function (elementOrSelector, options) {
          var svgElement = utilities.getSvg(elementOrSelector)
          if (null === svgElement) return null
          for (
            var instanceIndex = instances.length - 1;
            0 <= instanceIndex;
            instanceIndex--
          )
            if (instances[instanceIndex].svg === svgElement)
              return instances[instanceIndex].instance.getPublicInstance()
          return (
            instances.push({
              svg: svgElement,
              instance: new SvgPanZoom(svgElement, options)
            }),
            instances[instances.length - 1].instance.getPublicInstance()
          )
        }
      },
      {
        './control-icons': 1,
        './shadow-viewport': 2,
        './svg-utilities': 5,
        './uniwheel': 6,
        './utilities': 7
      }
    ],
    5: [
      function (requireModule, moduleRecord, exports) {
        var utilities = requireModule('./utilities'),
          browserType = 'unknown'
        document.documentMode && (browserType = 'ie'),
          (moduleRecord.exports = {
            svgNS: 'http://www.w3.org/2000/svg',
            xmlNS: 'http://www.w3.org/XML/1998/namespace',
            xmlnsNS: 'http://www.w3.org/2000/xmlns/',
            xlinkNS: 'http://www.w3.org/1999/xlink',
            evNS: 'http://www.w3.org/2001/xml-events',
            getBoundingClientRectNormalized: function (svgElement) {
              if (svgElement.clientWidth && svgElement.clientHeight)
                return { width: svgElement.clientWidth, height: svgElement.clientHeight }
              if (svgElement.getBoundingClientRect()) return svgElement.getBoundingClientRect()
              throw new Error('Cannot get BoundingClientRect for SVG.')
            },
            getOrCreateViewport: function (svgElement, viewportSelector) {
              var viewportElement = null
              if (!(viewportElement =
                utilities.isElement(viewportSelector)
                  ? viewportSelector
                  : svgElement.querySelector(viewportSelector))) {
                var otherChildren = Array.prototype.slice
                  .call(svgElement.childNodes || svgElement.children)
                  .filter(function (child) {
                    return 'defs' !== child.nodeName && '#text' !== child.nodeName
                  })
                1 === otherChildren.length &&
                  'g' === otherChildren[0].nodeName &&
                  null === otherChildren[0].getAttribute('transform') &&
                  (viewportElement = otherChildren[0])
              }
              if (!viewportElement) {
                var viewportId =
                  'viewport-' + new Date().toISOString().replace(/\D/g, '')
                ;(viewportElement = document.createElementNS(this.svgNS, 'g')).setAttribute(
                  'id',
                  viewportId
                )
                var childNodes = svgElement.childNodes || svgElement.children
                if (childNodes && 0 < childNodes.length)
                  for (var childIndex = childNodes.length; 0 < childIndex; childIndex--)
                    'defs' !== childNodes[childNodes.length - childIndex].nodeName &&
                      viewportElement.appendChild(childNodes[childNodes.length - childIndex])
                svgElement.appendChild(viewportElement)
              }
              var viewportClasses = []
              return (
                viewportElement.getAttribute('class') &&
                  (viewportClasses = viewportElement.getAttribute('class').split(' ')),
                ~viewportClasses.indexOf('svg-pan-zoom_viewport') ||
                  (viewportClasses.push('svg-pan-zoom_viewport'),
                  viewportElement.setAttribute('class', viewportClasses.join(' '))),
                viewportElement
              )
            },
            setupSvgAttributes: function (svgElement) {
              if (
                (svgElement.setAttribute('xmlns', this.svgNS),
                svgElement.setAttributeNS(this.xmlnsNS, 'xmlns:xlink', this.xlinkNS),
                svgElement.setAttributeNS(this.xmlnsNS, 'xmlns:ev', this.evNS),
                null !== svgElement.parentNode)
              ) {
                var styleAttribute = svgElement.getAttribute('style') || ''
                ;-1 === styleAttribute.toLowerCase().indexOf('overflow') &&
                  svgElement.setAttribute('style', 'overflow: hidden; ' + styleAttribute)
              }
            },
            internetExplorerRedisplayInterval: 300,
            refreshDefsGlobal: utilities.throttle(
              function () {
                for (
                  var definitionNodes = document.querySelectorAll('defs'),
                    definitionCount = definitionNodes.length,
                    definitionIndex = 0;
                  definitionIndex < definitionCount;
                  definitionIndex++
                ) {
                  var definitionElement = definitionNodes[definitionIndex]
                  definitionElement.parentNode.insertBefore(definitionElement, definitionElement)
                }
              },
              this ? this.internetExplorerRedisplayInterval : null
            ),
            setCTM: function (viewportElement, matrix, defsElement) {
              var svgUtilities = this,
                transformString =
                  'matrix(' +
                  matrix.a +
                  ',' +
                  matrix.b +
                  ',' +
                  matrix.c +
                  ',' +
                  matrix.d +
                  ',' +
                  matrix.e +
                  ',' +
                  matrix.f +
                  ')'
              viewportElement.setAttributeNS(null, 'transform', transformString),
                'transform' in viewportElement.style
                  ? (viewportElement.style.transform = transformString)
                  : '-ms-transform' in viewportElement.style
                  ? (viewportElement.style['-ms-transform'] = transformString)
                  : '-webkit-transform' in viewportElement.style &&
                    (viewportElement.style['-webkit-transform'] = transformString),
                'ie' === browserType &&
                  defsElement &&
                  (defsElement.parentNode.insertBefore(defsElement, defsElement),
                  window.setTimeout(function () {
                    svgUtilities.refreshDefsGlobal()
                  }, svgUtilities.internetExplorerRedisplayInterval))
            },
            getEventPoint: function (event, svgElement) {
              var svgPoint = svgElement.createSVGPoint()
              return (
                utilities.mouseAndTouchNormalize(event, svgElement),
                (svgPoint.x = event.clientX),
                (svgPoint.y = event.clientY),
                svgPoint
              )
            },
            getSvgCenterPoint: function (svgElement, width, height) {
              return this.createSVGPoint(svgElement, width / 2, height / 2)
            },
            createSVGPoint: function (svgElement, x, y) {
              var svgPoint = svgElement.createSVGPoint()
              return (svgPoint.x = x), (svgPoint.y = y), svgPoint
            }
          })
      },
      { './utilities': 7 }
    ],
    // Normalizes wheel event variants and retains wrappers for clean removal.
    6: [
      function (requireModule, moduleRecord, exports) {
        function normalizeLegacyWheelEvent(element, listener) {
          function handleLegacyWheelEvent(nativeEvent) {
            nativeEvent = nativeEvent || window.event
            var normalizedEvent = {
              originalEvent: nativeEvent,
              target: nativeEvent.target || nativeEvent.srcElement,
              type: 'wheel',
              deltaMode:
                'MozMousePixelScroll' == nativeEvent.type ? 0 : 1,
              deltaX: 0,
              delatZ: 0,
              preventDefault: function () {
                nativeEvent.preventDefault
                  ? nativeEvent.preventDefault()
                  : (nativeEvent.returnValue = !1)
              }
            }
            return (
              'mousewheel' == wheelEventType
                ? ((normalizedEvent.deltaY = -0.025 * nativeEvent.wheelDelta),
                  nativeEvent.wheelDeltaX &&
                    (normalizedEvent.deltaX =
                      -0.025 * nativeEvent.wheelDeltaX))
                : (normalizedEvent.deltaY = nativeEvent.detail),
              listener(normalizedEvent)
            )
          }
          return (
            wrappedLegacyListeners.push({
              element: element,
              fn: handleLegacyWheelEvent
            }),
            handleLegacyWheelEvent
          )
        }
        function addWheelListener(element, eventName, listener, isPassive) {
          var eventListener =
            'wheel' === wheelEventType
              ? listener
              : normalizeLegacyWheelEvent(element, listener)
          element[addEventListenerMethod](
            eventNamePrefix + eventName,
            eventListener,
            isPassive ? passiveListenerOptions : activeListenerOptions
          )
        }
        function removeWheelListener(element, eventName, listener, isPassive) {
          var eventListener =
            'wheel' === wheelEventType
              ? listener
              : (function (targetElement) {
                  for (
                    var wrapperIndex = 0;
                    wrapperIndex < wrappedLegacyListeners.length;
                    wrapperIndex++
                  )
                    if (
                      wrappedLegacyListeners[wrapperIndex].element ===
                      targetElement
                    )
                      return wrappedLegacyListeners[wrapperIndex].fn
                  return function () {}
                })(element)
          element[removeEventListenerMethod](
            eventNamePrefix + eventName,
            eventListener,
            isPassive ? passiveListenerOptions : activeListenerOptions
          )
          if ('wheel' !== wheelEventType) {
            for (
              var wrapperIndex = 0;
              wrapperIndex < wrappedLegacyListeners.length;
              wrapperIndex++
            )
              if (wrappedLegacyListeners[wrapperIndex].element === element) {
                wrappedLegacyListeners.splice(wrapperIndex, 1)
                break
              }
          }
        }
        var addEventListenerMethod,
          removeEventListenerMethod,
          wheelEventType,
          eventNamePrefix,
          wrappedLegacyListeners,
          passiveListenerOptions,
          activeListenerOptions
        moduleRecord.exports =
          ((wrappedLegacyListeners = []),
          (activeListenerOptions = {
            passive: !(
              (passiveListenerOptions = {
                passive: !(eventNamePrefix = '')
              })
            )
          }),
          window.addEventListener
            ? ((addEventListenerMethod = 'addEventListener'),
              (removeEventListenerMethod = 'removeEventListener'))
            : ((addEventListenerMethod = 'attachEvent'),
              (removeEventListenerMethod = 'detachEvent'),
              (eventNamePrefix = 'on')),
          (wheelEventType =
            'onwheel' in document.createElement('div')
              ? 'wheel'
              : void 0 !== document.onmousewheel
              ? 'mousewheel'
              : 'DOMMouseScroll'),
          {
            on: function (element, listener, isPassive) {
              addWheelListener(element, wheelEventType, listener, isPassive),
                'DOMMouseScroll' == wheelEventType &&
                  addWheelListener(
                    element,
                    'MozMousePixelScroll',
                    listener,
                    isPassive
                  )
            },
            off: function (element, listener, isPassive) {
              removeWheelListener(
                element,
                wheelEventType,
                listener,
                isPassive
              ),
                'DOMMouseScroll' == wheelEventType &&
                  removeWheelListener(
                    element,
                    'MozMousePixelScroll',
                    listener,
                    isPassive
                  )
            }
          })
      },
      {}
    ],
    // Shared DOM, event, and scheduling helpers.
    7: [
      function (requireModule, moduleRecord, exports) {
        function createTimeoutScheduler(delayMilliseconds) {
          return function schedule(callback) {
            window.setTimeout(callback, delayMilliseconds)
          }
        }
        moduleRecord.exports = {
          extend: function (target, source) {
            target = target || {}
            for (var propertyName in source)
              this.isObject(source[propertyName])
                ? (target[propertyName] = this.extend(
                    target[propertyName],
                    source[propertyName]
                  ))
                : (target[propertyName] = source[propertyName])
            return target
          },
          isElement: function (value) {
            return (
              value instanceof HTMLElement ||
              value instanceof SVGElement ||
              value instanceof SVGSVGElement ||
              (value &&
                'object' == typeof value &&
                null !== value &&
                1 === value.nodeType &&
                'string' == typeof value.nodeName)
            )
          },
          isObject: function (value) {
            return '[object Object]' === Object.prototype.toString.call(value)
          },
          isNumber: function (value) {
            return !isNaN(parseFloat(value)) && isFinite(value)
          },
          getSvg: function (elementOrSelector) {
            var selectedElement, svgElement
            if (this.isElement(elementOrSelector))
              selectedElement = elementOrSelector
            else {
              if (
                !(
                  'string' == typeof elementOrSelector ||
                  elementOrSelector instanceof String
                )
              )
                throw new Error(
                  'Provided selector is not an HTML object nor String'
                )
              if (
                !(selectedElement = document.querySelector(elementOrSelector))
              )
                throw new Error(
                  'Provided selector did not find any elements. Selector: ' +
                    elementOrSelector
                )
            }
            if ('svg' === selectedElement.tagName.toLowerCase())
              svgElement = selectedElement
            else if ('object' === selectedElement.tagName.toLowerCase())
              svgElement = selectedElement.contentDocument.documentElement
            else {
              if ('embed' !== selectedElement.tagName.toLowerCase())
                throw 'img' === selectedElement.tagName.toLowerCase()
                  ? new Error(
                      'Cannot script an SVG in an "img" element. Please use an "object" element or an in-line SVG.'
                    )
                  : new Error('Cannot get SVG.')
              svgElement = selectedElement.getSVGDocument().documentElement
            }
            return svgElement
          },
          proxy: function (callback, context) {
            return function () {
              return callback.apply(context, arguments)
            }
          },
          getType: function (value) {
            return Object.prototype.toString
              .apply(value)
              .replace(/^\[object\s/, '')
              .replace(/\]$/, '')
          },
          mouseAndTouchNormalize: function (event, svgElement) {
            if (void 0 === event.clientX || null === event.clientX)
              if (
                ((event.clientX = 0),
                void (event.clientY = 0) !== event.touches &&
                  event.touches.length)
              ) {
                if (void 0 !== event.touches[0].clientX)
                  (event.clientX = event.touches[0].clientX),
                    (event.clientY = event.touches[0].clientY)
                else if (void 0 !== event.touches[0].pageX) {
                  var svgBounds = svgElement.getBoundingClientRect()
                  ;(event.clientX = event.touches[0].pageX - svgBounds.left),
                    (event.clientY = event.touches[0].pageY - svgBounds.top)
                }
              } else
                void 0 !== event.originalEvent &&
                  void 0 !== event.originalEvent.clientX &&
                  ((event.clientX = event.originalEvent.clientX),
                  (event.clientY = event.originalEvent.clientY))
          },
          isDblClick: function (event, previousEvent) {
            if (2 === event.detail) return !0
            if (null == previousEvent) return !1
            var timeBetweenEvents = event.timeStamp - previousEvent.timeStamp,
              pointerDistance = Math.sqrt(
                Math.pow(event.clientX - previousEvent.clientX, 2) +
                  Math.pow(event.clientY - previousEvent.clientY, 2)
              )
            return timeBetweenEvents < 250 && pointerDistance < 10
          },
          now:
            Date.now ||
            function () {
              return new Date().getTime()
            },
          throttle: function (callback, waitMilliseconds, options) {
            var lastThis,
              lastArguments,
              result,
              utilityContext = this,
              timeoutId = null,
              lastExecutionTime = 0
            options = options || {}
            function invokeTrailingCall() {
              ;(lastExecutionTime =
                !1 === options.leading ? 0 : utilityContext.now()),
                (timeoutId = null),
                (result = callback.apply(lastThis, lastArguments)),
                timeoutId || (lastThis = lastArguments = null)
            }
            return function throttled() {
              var currentTime = utilityContext.now()
              lastExecutionTime ||
                !1 !== options.leading ||
                (lastExecutionTime = currentTime)
              var remainingWait =
                waitMilliseconds - (currentTime - lastExecutionTime)
              return (
                (lastThis = this),
                (lastArguments = arguments),
                remainingWait <= 0 || waitMilliseconds < remainingWait
                  ? (clearTimeout(timeoutId),
                    (timeoutId = null),
                    (lastExecutionTime = currentTime),
                    (result = callback.apply(lastThis, lastArguments)),
                    timeoutId || (lastThis = lastArguments = null))
                  : timeoutId ||
                    !1 === options.trailing ||
                    (timeoutId = setTimeout(invokeTrailingCall, remainingWait)),
                result
              )
            }
          },
          createRequestAnimationFrame: function (refreshRate) {
            var delayMilliseconds = null
            return (
              'auto' !== refreshRate &&
                refreshRate < 60 &&
                1 < refreshRate &&
                (delayMilliseconds = Math.floor(1e3 / refreshRate)),
              null === delayMilliseconds
                ? window.requestAnimationFrame || createTimeoutScheduler(33)
                : createTimeoutScheduler(delayMilliseconds)
            )
          }
        }
      },
      {}
    ]
  },
  {},
  [3]
)
