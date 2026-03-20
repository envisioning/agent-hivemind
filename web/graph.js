(function () {
  function mountGraph(container, data, onSkillClick) {
    if (!container || !window.d3) {
      return { destroy: function () {} };
    }

    container.innerHTML = '';
    var width = container.clientWidth || 800;
    var height = container.clientHeight || 600;
    var accent = '#d6f249';

    var tooltip = document.createElement('div');
    tooltip.className = 'graph-tooltip';
    tooltip.style.position = 'absolute';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.opacity = '0';
    tooltip.style.transition = 'opacity 120ms ease';
    tooltip.style.background = '#121212';
    tooltip.style.color = '#e0e0e0';
    tooltip.style.border = '1px solid #2d2d2d';
    tooltip.style.borderRadius = '8px';
    tooltip.style.padding = '8px 10px';
    tooltip.style.fontSize = '12px';
    tooltip.style.zIndex = '3';
    container.appendChild(tooltip);

    var svg = d3
      .select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', [0, 0, width, height])
      .style('display', 'block');

    var g = svg.append('g');

    var nodes = data.nodes.map(function (n) {
      return {
        id: n.id,
        count: n.count,
        plays: n.plays || []
      };
    });
    var links = data.links.map(function (l) {
      return {
        source: l.source,
        target: l.target,
        weight: l.weight
      };
    });

    var maxCount = d3.max(nodes, function (d) {
      return d.count;
    }) || 1;
    var maxWeight = d3.max(links, function (d) {
      return d.weight;
    }) || 1;

    var radius = d3.scaleSqrt().domain([1, maxCount]).range([4, 26]);
    var linkWidth = d3.scaleLinear().domain([1, maxWeight]).range([0.4, 3.8]);
    var color = d3.scaleSequential(d3.interpolateViridis).domain([0, Math.log(maxCount + 1)]);

    svg.call(
      d3.zoom().scaleExtent([0.25, 6]).on('zoom', function (event) {
        g.attr('transform', event.transform);
      })
    );

    var simulation = d3
      .forceSimulation(nodes)
      .force(
        'link',
        d3
          .forceLink(links)
          .id(function (d) {
            return d.id;
          })
          .distance(function (d) {
            return Math.max(30, 105 - Math.min(d.weight * 3, 65));
          })
      )
      .force(
        'charge',
        d3.forceManyBody().strength(function (d) {
          return -60 - d.count * 2;
        })
      )
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(function (d) {
        return radius(d.count) + 3;
      }));

    var link = g
      .append('g')
      .attr('stroke', '#282828')
      .attr('stroke-opacity', 0.45)
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', function (d) {
        return linkWidth(d.weight);
      });

    var node = g
      .append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .call(
        d3
          .drag()
          .on('start', function (event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', function (event, d) {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', function (event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    node
      .append('circle')
      .attr('r', function (d) {
        return radius(d.count);
      })
      .attr('fill', function (d) {
        return d.count >= 8 ? accent : color(Math.log(d.count + 1));
      })
      .attr('stroke', function (d) {
        return d.count >= 8 ? accent : '#3a3a3a';
      })
      .attr('stroke-width', function (d) {
        return d.count >= 8 ? 1.5 : 1;
      })
      .attr('opacity', 0.9);

    node
      .filter(function (d) {
        return d.count >= 2;
      })
      .append('text')
      .text(function (d) {
        return d.id;
      })
      .attr('font-size', function (d) {
        return Math.max(8, Math.min(13, 5 + d.count * 0.35));
      })
      .attr('fill', '#b8b8b8')
      .attr('text-anchor', 'middle')
      .attr('dy', function (d) {
        return radius(d.count) + 11;
      })
      .style('pointer-events', 'none');

    function connectedSet(nodeId) {
      var set = new Set();
      links.forEach(function (l) {
        var s = typeof l.source === 'object' ? l.source.id : l.source;
        var t = typeof l.target === 'object' ? l.target.id : l.target;
        if (s === nodeId) set.add(t);
        if (t === nodeId) set.add(s);
      });
      return set;
    }

    node
      .on('mouseover', function (event, d) {
        var connected = connectedSet(d.id);
        node.select('circle').attr('opacity', function (n) {
          return n.id === d.id || connected.has(n.id) ? 1 : 0.14;
        });
        node.select('text').attr('opacity', function (n) {
          return n.id === d.id || connected.has(n.id) ? 1 : 0.15;
        });

        link
          .attr('stroke-opacity', function (l) {
            var s = typeof l.source === 'object' ? l.source.id : l.source;
            var t = typeof l.target === 'object' ? l.target.id : l.target;
            return s === d.id || t === d.id ? 0.85 : 0.03;
          })
          .attr('stroke', function (l) {
            var s = typeof l.source === 'object' ? l.source.id : l.source;
            var t = typeof l.target === 'object' ? l.target.id : l.target;
            return s === d.id || t === d.id ? accent : '#282828';
          });

        tooltip.innerHTML = '<strong style="color:' + accent + '">' + d.id + '</strong><br>' + d.count + ' plays';
        tooltip.style.left = event.offsetX + 14 + 'px';
        tooltip.style.top = event.offsetY - 8 + 'px';
        tooltip.style.opacity = '1';
      })
      .on('mousemove', function (event) {
        tooltip.style.left = event.offsetX + 14 + 'px';
        tooltip.style.top = event.offsetY - 8 + 'px';
      })
      .on('mouseout', function () {
        node.select('circle').attr('opacity', 0.9);
        node.select('text').attr('opacity', 1);
        link.attr('stroke-opacity', 0.45).attr('stroke', '#282828');
        tooltip.style.opacity = '0';
      })
      .on('click', function (_event, d) {
        if (typeof onSkillClick === 'function') {
          onSkillClick(d.id);
        }
      });

    simulation.on('tick', function () {
      link
        .attr('x1', function (d) {
          return d.source.x;
        })
        .attr('y1', function (d) {
          return d.source.y;
        })
        .attr('x2', function (d) {
          return d.target.x;
        })
        .attr('y2', function (d) {
          return d.target.y;
        });

      node.attr('transform', function (d) {
        return 'translate(' + d.x + ',' + d.y + ')';
      });
    });

    var resizeTimer = null;

    function onResize() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        width = container.clientWidth || width;
        height = container.clientHeight || height;
        svg.attr('viewBox', [0, 0, width, height]);
        simulation.force('center', d3.forceCenter(width / 2, height / 2));
        simulation.alpha(0.45).restart();
      }, 120);
    }

    window.addEventListener('resize', onResize);

    return {
      destroy: function () {
        window.removeEventListener('resize', onResize);
        simulation.stop();
        container.innerHTML = '';
      }
    };
  }

  window.HivemindGraph = {
    mount: mountGraph
  };
})();
