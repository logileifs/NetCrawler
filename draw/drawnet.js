
var width = 1500,
    height = 750,
    fill = d3.scale.category20();

var linkNormal = 2,
    linkBold = 4,
    nodeNormal = 5,
    nodeBold = 8,
    current;

var vis = d3.select("#network")
    .append("svg:svg")
      .attr("width", width)
      .attr("height", height)
      .attr("pointer-events", "all")
    .append('svg:g')
      .call(d3.behavior.zoom().on("zoom", redraw))
    .append('svg:g');

vis.append('svg:rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'white');

function redraw() {
  //console.log("here", d3.event.translate, d3.event.scale);
  vis.attr("transform",
      "translate(" + d3.event.translate + ")"
      + " scale(" + d3.event.scale + ")");
}

function createHTML(d){

		var ul = '<ul class="list-group">';
    var li1 = '<li class="list-group-item"><strong>Name: </strong><span id="name">'+d.name+'</span></li>';
    var li2 = '<li class="list-group-item"><strong>Serial number: </strong><span id="serial">'+d.serial+'</span></li>';
    var li3 = '<li class="list-group-item"><strong>Model number: </strong><span id="model">'+d.model+'</span></li>';
              
      var ulend= '';//'</ul>';
      var dd = '<li class="list-group-item"><div id="dd'+d.id+'" class="btn-group"><button type="button" class="btn btn-default dropdown-toggle macs" data-toggle="dropdown">MAC addresses</button><ul id="host0ul" class="dropdown-menu">';

      console.log('createHTML');
      for(var i=0; i<d.macs.length; i++)
      {
      	var limac = '<li><a href="#">'+d.macs[i]+'</a></li>';
      	dd += limac;
      	console.log(d.macs[i]);
      }
      dd += '</ul></ul>';

      return ul+li1+li2+li3+ulend+dd;
	}

function draw(json) {
  var force = d3.layout.force()
    .charge(-120)
    .linkDistance(30)
    .nodes(json.nodes)
    .links(json.links)
    .size([width, height])
    .start();

  var link = vis.selectAll("line.link")
    .data(json.links)
    .enter().append("svg:line")
    .attr("class", "link")
    .style("stroke-width", linkNormal)
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

  var node = vis.selectAll("circle.node")
    .data(json.nodes)
    .enter().append("svg:circle")
    .attr("class", "node")
    .attr("rel", "popover")
			.attr("data-original-title", function(d){return '<div class="panel-heading"><b>Host </b>'+d.id+'</div>'})
			.attr("data-content", function(d){return createHTML(d)})
		.attr("id", function(d,i){return d.id})
    .attr("cx", function(d) { return d.x; })
    .attr("cy", function(d) { return d.y; })
    .attr("r", nodeNormal)
    .style("fill", function(d) {return typeColoring(d.type, d.types);})
    .call(force.drag)
    .on('click', function(d){
      d3.select(current).style("stroke", function(d) { return typeColoring(d.type, d.types); })
      .transition().attr("r", nodeNormal)
      .duration(200);
      if(current != this) {
          current = this;
          d3.select(this).style("stroke", "black")
          .transition()
          .attr("r", nodeBold)
          .duration(200);
          $("#ip").text(d.ip);
          $("#name").text(d.name);
          $("#mac").text(d.mac);
          $("#serial").text(d.serial);
          $("#type").text(parseType(d.type, d.types));
        }
        else {
          current = null;
          $("#ip").text("");
          $("#name").text("");
          $("#mac").text("");
          $("#serial").text("");
          $("#type").text("");
        }
    });
      
  vis.style("opacity", 1e-6)
    .transition()
    .duration(1000)
    .style("opacity", 1);

  node.on('mouseover', function(d) {
    link.style('stroke-width', function(l) {
      if (d === l.source || d === l.target)
        return linkBold;
      else
        return linkNormal;
    });

    div.transition()  
       .duration(200)      
       .style("opacity", .9);      
    div.html(d.ip)  
       .style("left", (d3.event.pageX) + "px")     
       .style("top", (d3.event.pageY - 28) + "px");    
  });

  node.on('mouseout', function() {
    link.style('stroke-width', linkNormal);
    div.transition()        
    .duration(500)      
    .style("opacity", 0);

  });

  $(".node").popover({
			placement: 'top',
			html: true,
			container:'body'
		});

  link.on('mouseover', function() {
    d3.select(this).style("stroke-width", linkBold);
  });

  link.on('mouseout', function() {
    link.style("stroke-width", linkNormal);
  });

  force.on("tick", function() {
      link.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node.attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
  });

  var div = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0);
};

function parseType(type, types) {
  if(type === "end_device")
    return "end device";
  else if(type === "networking") {
    if(types.length === 1) 
      return types[0];
    else if(types.length === 2) {
      if((types[0] === "router" && types[1] === "switch") || (types[0] === "switch" && types[1] === "router"))
        return "router/switch"
      else
        return "unknown";
    }
  }
  else
    return "unknown";
}

function typeColoring(type, types) {
  if(type === "end_device") 
    return "#AA40FF";
  else if(types.length === 1) {
    if(types[0] === "router") 
      return "#1F5EA8";      
    else if(types[0] === "switch") 
      return "#39C0B3";
    else // Unknown type
    return "#EB403B";
  }
  else if(types.length === 2) {
    if((types[0] === "router" && types[1] === "switch") || (types[0] === "switch" && types[1] === "router"))
      return "#719207"
    else // Unknown type
      return "#EB403B";
  }
  else // Unknown type
    return "#EB403B";
}

$( document ).ready(function() {
    $.getJSON("net.json", function(json) {
      draw(json);
    });
});