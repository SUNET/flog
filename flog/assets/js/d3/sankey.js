//
// Created by Mike Bostock - http://bost.ocks.org/mike/sankey/
//
// valueThreshold added by Johan Lundberg (lundberg at nordu dot net).
//

d3.sankey = function() {
  var sankey = {},
      nodeWidth = 24,
      nodePadding = 8,
      size = [1, 1],
      nodes = [],
      links = [],
      valueThreshold = 5;

  sankey.nodeWidth = function(_) {
    if (!arguments.length) return nodeWidth;
    nodeWidth = +_;
    return sankey;
  };

  sankey.nodePadding = function(_) {
    if (!arguments.length) return nodePadding;
    nodePadding = +_;
    return sankey;
  };

  sankey.nodes = function(_) {
    if (!arguments.length) return nodes;
    nodes = _;
    return sankey;
  };

  sankey.links = function(_) {
    if (!arguments.length) return links;
    links = _;
    return sankey;
  };

  sankey.size = function(_) {
    if (!arguments.length) return size;
    size = _;
    return sankey;
  };

  sankey.valueThreshold = function(_) {
    if (!arguments.length) return valueThreshold;
    valueThreshold = _;
    return sankey;
  };

  sankey.layout = function(iterations) {
    computeNodeLinks();
    computeValueThreshold();
    computeNodeValues();
    computeNodeBreadths();
    computeNodeDepths(iterations);
    computeLinkDepths();
    return sankey;
  };

  sankey.relayout = function() {
    computeLinkDepths();
    return sankey;
  };

  sankey.link = function() {
    var curvature = 0.5;

    function link(d) {
      var x0 = d.source.x + d.source.dx,
          x1 = d.target.x,
          xi = d3.interpolateNumber(x0, x1),
          x2 = xi(curvature),
          x3 = xi(1 - curvature),
          y0 = d.source.y + d.sy + d.dy / 2,
          y1 = d.target.y + d.ty + d.dy / 2;
      return "M" + x0 + "," + y0 + "C" + x2 + "," + y0 + " " + x3 + "," + y1 + " " + x1 + "," + y1;
    }

    link.curvature = function(_) {
      if (!arguments.length) return curvature;
      curvature = +_;
      return link;
    };

    return link;
  };

  // Populate the sourceLinks and targetLinks for each node.
  function computeNodeLinks() {
    nodes.forEach(function(node) {
      node.sourceLinks = [];
      node.targetLinks = [];
    });
    links.forEach(function(link) {
      var source = link.source,
          target = link.target;
      // Hack to counter self referencing links
      if (link.source === link.target) { return false; }
      nodes.some(function(node) {
        if (node.id === source) {
            source = link.source = node;
            return true;
        }
        return false;
      });
      nodes.some(function(node) {
         if (node.id === target) {
            target = link.target = node;
            return true;
         }
         return false;
      });
      source.sourceLinks.push(link);
      target.targetLinks.push(link);
    });
  }

  // Combines any nodes with value below valueThreshold in to an "other node"
  function computeValueThreshold() {
      if (valueThreshold === 0) { return; } // Do not do anything if valueThreshold is 0

      var i;
      var j;
      var node;
      var index;
      var link;
      var nextLink;

      // Combine source nodes with values under valueThreshold
      var otherSourceNode = {
          "name": "Other <" + valueThreshold,
          sourceLinks: [],
          targetLinks: []
      };

      for (i = 0; i < nodes.length; i++) {
          node = nodes[i];
          var sourceResult = d3.sum(node.sourceLinks, value);
          if (sourceResult !== 0 && sourceResult <= valueThreshold) {
              index = nodes.indexOf(node);
              nodes.splice(index, 1);
              i--;
              otherSourceNode.sourceLinks.push.apply(otherSourceNode.sourceLinks, node.sourceLinks);
          }
      }

      otherSourceNode.sourceLinks.forEach(function(link) {
          link.source = otherSourceNode;
          var index = links.indexOf(link);
          links.splice(index, 1);
      });

      for (i = 0; i < otherSourceNode.sourceLinks.length; i++) {
          link = otherSourceNode.sourceLinks[i];
          for (j = i+1; j < otherSourceNode.sourceLinks.length; j++) {
              nextLink = otherSourceNode.sourceLinks[j];
              if (link.target === nextLink.target) {
                  link.value += nextLink.value;
                  index = otherSourceNode.sourceLinks.indexOf(nextLink);
                  otherSourceNode.sourceLinks.splice(index, 1);
                  index = nextLink.target.targetLinks.indexOf(nextLink);
                  nextLink.target.targetLinks.splice(index, 1);
                  j--;
              }
          }
      }

      links.push.apply(links, otherSourceNode.sourceLinks);
      nodes.push(otherSourceNode);

      // Combine target nodes with values under valueThreshold
      var otherTargetNode = {
          "name": "Other <" + valueThreshold,
          sourceLinks: [],
          targetLinks: []
      };

      for (i = 0; i < nodes.length; i++) {
          node = nodes[i];
          var targetResult = d3.sum(node.targetLinks, value);
          if (targetResult !== 0 && targetResult <= valueThreshold) {
              index = nodes.indexOf(node);
              nodes.splice(index, 1);
              i--;
              otherTargetNode.targetLinks.push.apply(otherTargetNode.targetLinks, node.targetLinks);
          }
      }

      otherTargetNode.targetLinks.forEach(function(link) {
          link.target = otherTargetNode;
          var index = links.indexOf(link);
          links.splice(index, 1);
      });

      for (i = 0; i < otherTargetNode.targetLinks.length; i++) {
          link = otherTargetNode.targetLinks[i];
          for (j = i+1; j < otherTargetNode.targetLinks.length; j++) {
              nextLink = otherTargetNode.targetLinks[j];
              if (link.source === nextLink.source) {
                  link.value += nextLink.value;
                  index = otherTargetNode.targetLinks.indexOf(nextLink);
                  otherTargetNode.targetLinks.splice(index, 1);
                  index = nextLink.source.sourceLinks.indexOf(nextLink);
                  nextLink.source.sourceLinks.splice(index, 1);
                  j--;
              }
          }
      }

      links.push.apply(links, otherTargetNode.targetLinks);
      nodes.push(otherTargetNode);
  }

  // Compute the value (size) of each node by summing the associated links.
  function computeNodeValues() {
    nodes.forEach(function(node) {
      node.value = Math.max(
        d3.sum(node.sourceLinks, value),
        d3.sum(node.targetLinks, value)
      );
    });
  }

  // Iteratively assign the breadth (x-position) for each node.
  // Nodes are assigned the maximum breadth of incoming neighbors plus one;
  // nodes with no incoming links are assigned breadth zero, while
  // nodes with no outgoing links are assigned the maximum breadth.
  function computeNodeBreadths() {
    var remainingNodes = nodes,
        nextNodes,
        x = 0;

    while (remainingNodes.length) {
      nextNodes = [];
      remainingNodes.forEach(function(node) {
        node.x = x;
        node.dx = nodeWidth;
        node.sourceLinks.forEach(function(link) {
          nextNodes.push(link.target);
        });
      });
      remainingNodes = nextNodes;
      ++x;
    }

    moveSinksRight(x);
    scaleNodeBreadths((size[0] - nodeWidth) / (x - 1));
  }

  function moveSourcesRight() {
    nodes.forEach(function(node) {
      if (!node.targetLinks.length) {
        node.x = d3.min(node.sourceLinks, function(d) { return d.target.x; }) - 1;
      }
    });
  }

  function moveSinksRight(x) {
    nodes.forEach(function(node) {
      if (!node.sourceLinks.length) {
        node.x = x - 1;
      }
    });
  }

  function scaleNodeBreadths(kx) {
    nodes.forEach(function(node) {
      node.x *= kx;
    });
  }

  function computeNodeDepths(iterations) {
    var nodesByBreadth = d3.nest()
        .key(function(d) { return d.x; })
        .sortKeys(d3.ascending)
        .entries(nodes)
        .map(function(d) { return d.values; });

    //
    initializeNodeDepth();
    resolveCollisions();
    for (var alpha = 1; iterations > 0; --iterations) {
      relaxRightToLeft(alpha *= 0.99);
      resolveCollisions();
      relaxLeftToRight(alpha);
      resolveCollisions();
    }

    function initializeNodeDepth() {
      var ky = d3.min(nodesByBreadth, function(nodes) {
        return (size[1] - (nodes.length - 1) * nodePadding) / d3.sum(nodes, value);
      });

      nodesByBreadth.forEach(function(nodes) {
        nodes.forEach(function(node, i) {
          node.y = i;
          node.dy = node.value * ky;
        });
      });

      links.forEach(function(link) {
        link.dy = link.value * ky;
      });
    }

    function relaxLeftToRight(alpha) {
      nodesByBreadth.forEach(function(nodes, breadth) {
        nodes.forEach(function(node) {
          if (node.targetLinks.length) {
            var y = d3.sum(node.targetLinks, weightedSource) / d3.sum(node.targetLinks, value);
            node.y += (y - center(node)) * alpha;
          }
        });
      });

      function weightedSource(link) {
        return center(link.source) * link.value;
      }
    }

    function relaxRightToLeft(alpha) {
      nodesByBreadth.slice().reverse().forEach(function(nodes) {
        nodes.forEach(function(node) {
          if (node.sourceLinks.length) {
            var y = d3.sum(node.sourceLinks, weightedTarget) / d3.sum(node.sourceLinks, value);
            node.y += (y - center(node)) * alpha;
          }
        });
      });

      function weightedTarget(link) {
        return center(link.target) * link.value;
      }
    }

    function resolveCollisions() {
      nodesByBreadth.forEach(function(nodes) {
        var node,
            dy,
            y0 = 0,
            n = nodes.length,
            i;

        // Push any overlapping nodes down.
        nodes.sort(ascendingDepth);
        for (i = 0; i < n; ++i) {
          node = nodes[i];
          dy = y0 - node.y;
          if (dy > 0) node.y += dy;
          y0 = node.y + node.dy + nodePadding;
        }

        // If the bottommost node goes outside the bounds, push it back up.
        dy = y0 - nodePadding - size[1];
        if (dy > 0) {
          y0 = node.y -= dy;

          // Push any overlapping nodes back up.
          for (i = n - 2; i >= 0; --i) {
            node = nodes[i];
            dy = node.y + node.dy + nodePadding - y0;
            if (dy > 0) node.y -= dy;
            y0 = node.y;
          }
        }
      });
    }

    function ascendingDepth(a, b) {
      return a.y - b.y;
    }
  }

  function computeLinkDepths() {
    nodes.forEach(function(node) {
      node.sourceLinks.sort(ascendingTargetDepth);
      node.targetLinks.sort(ascendingSourceDepth);
    });
    nodes.forEach(function(node) {
      var sy = 0, ty = 0;
      node.sourceLinks.forEach(function(link) {
        link.sy = sy;
        sy += link.dy;
      });
      node.targetLinks.forEach(function(link) {
        link.ty = ty;
        ty += link.dy;
      });
    });

    function ascendingSourceDepth(a, b) {
      return a.source.y - b.source.y;
    }

    function ascendingTargetDepth(a, b) {
      return a.target.y - b.target.y;
    }
  }

  function center(node) {
    return node.y + node.dy / 2;
  }

  function value(link) {
    return link.value;
  }

  return sankey;
};
