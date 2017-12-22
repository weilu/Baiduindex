function findY(path, x) {
  var pathLength = path.getTotalLength()
  var start = 0
  var end = pathLength
  var target = (start + end) / 2

  // Ensure that x is within the range of the path
  x = Math.max(x, path.getPointAtLength(0).x)
  x = Math.min(x, path.getPointAtLength(pathLength).x)

  // Walk along the path using binary search
  // to locate the point with the supplied x value
  while (target >= start && target <= pathLength) {
    var pos = path.getPointAtLength(target)

    // use a threshold instead of strict equality 
    // to handle javascript floating point precision
    if (Math.abs(pos.x - x) < 0.001) {
      return pos.y
    } else if (pos.x > x) {
      end = target
    } else {
      start = target
    }
    target = (start + end) / 2
  }
}

var path = document.querySelector('path[stroke-opacity="1"]')
var box = path.getBBox()

var n = 300
var offset = (path.getPointAtLength(path.getTotalLength()).x - path.getPointAtLength(0).x) / (n-1)
var xs = []
for (var i=0; i<n; i++) {
  xs.push(path.getPointAtLength(0).x + i * offset)
}

var ys = xs.map(function(x) {
  return box.y + box.height - findY(path, x)
})
console.log(xs.join(','))
console.log(ys.join(','))

var intervals = 6
var max = 140
var min = 20
var unit = (max - min) / intervals
var actualMin = Math.max(min - unit, 0)
var range = max - actualMin

var plane = document.querySelector('svg > rect:nth-child(12)')
var scaledYs = ys.map(function(y) {
  return y / plane.height.baseVal.value * range + actualMin
})
console.log(scaledYs.join(','))


