var width = 1000,
    height = 600;

var color = d3.scale.category20();

var linkNormal = 4,
    linkBold = 6,
    nodeNormal = 14,
    nodeBold = 16;

var force = d3.layout.force()
    .charge(-500)
    .linkDistance(250)
    .theta(0.1)
    .gravity(0.05)
    .size([width, height]);

var svg = d3.select("#network").append("svg")
    .attr("width", width)
    .attr("height", height);

d3.json("net.json", function(error, graph) {
  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

  var link = svg.selectAll(".link")
      .data(graph.links)
      .enter()
      .append("line")
      .attr("class", "link")
      .style("stroke-width", linkNormal);

  var current;

  var div = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0);

  var node = svg.selectAll(".node")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("class", "node")
      .attr("r", nodeNormal)
      .style("fill", function(d) {return typeColoring(d.type);})
      .call(force.drag)
      .on('click', function(d){
        d3.select(current).style("fill", function(d) { return typeColoring(d.type); }).attr("r", nodeNormal);
        current = this;
        d3.select(this).style("fill", "#E98931").attr("r", nodeBold);
        $("#ip").text(d.ip);
        $("#interface").text(d.interface);
        $("#name").text(d.name);
        $("#mac").text(d.mac);
      });

  var linkpaths = svg.selectAll(".linkpath")
      .data(graph.links)
      .enter()
      .append('path')
      .attr({'d': function(d) {return 'M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y},
             'class':'edgelabel',
             'fill-opacity':0,
             'stroke-opacity':0,
             'fill':'blue',
             'stroke':'red',
             'id':function(d,i) {return 'linklabel'+i}})
      .style("pointer-events", "none");

  var linklabels = svg.selectAll(".linklabel")
        .data(graph.links)
        .enter()
        .append('text')
        .style("pointer-events", "none")
        .attr('fill','transparent')
        .attr({'class':'linklabel',
               'id':function(d,i){return 'linklabel'+i},
               'dx':80,
               'dy':0,
               'font-size':14,});

  linklabels.append('textPath')
        .data(graph.links)
        .attr('xlink:href',function(d,i) {return '#linklabel'+i})
        .style("pointer-events", "none")
        .text(function(d){return d.sport + "-" + d.tport});

  

  //node.append("title")
  //    .text(function(d) { return d.name; });

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    

    linkpaths.attr('d', function(d) { var path='M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y;
                                       //console.log(d)
                                       return path});       

    /*linklabels.select("text").text(function(d){
        if (d.target.x<d.source.x){
            bbox = this.getBBox();
            rx = bbox.x+bbox.width/2;
            ry = bbox.y+bbox.height/2;
            return parseInt(d.port2) + "-" + parseInt(d.port1);
            }
        else {
            return parseInt(d.port1) + "-" + parseInt(d.port2);
            }
     });*/

    /*linklabels.attr('transform',function(d){
        if (d.target.x<d.source.x){
            bbox = this.getBBox();
            rx = bbox.x+bbox.width/2;
            ry = bbox.y+bbox.height/2;
            return 'rotate(180 '+rx+' '+ry+')';
            }
        else {
            //linklabels.text(function(d){return parseInt(d.port1) + "-" + parseInt(d.port2)});
            return 'rotate(0)';
            }
     });*/
  });

  
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

  link.on('mouseover', function() {
    d3.select(this).style("stroke-width", linkBold);
      //.append("text")
      //.text(function(d) {return d.port1;});
  });

  link.on('mouseout', function() {
    link.style("stroke-width", linkNormal);
  });

  var showPortNbrs = false;

  $('#showport').click( function() {
    if(!showPortNbrs) {
      linklabels.attr('fill', '#000');
      showPortNbrs = true;
    }
    else {
      linklabels.attr('fill', 'transparent');
      showPortNbrs = false;
    }
  });

  function typeColoring(type) {
    if(type === "router") 
      return "#274389" 
    else if(type === "switch") 
      return "#39C0B3"
    else if(type === "end_device") 
      return "#6C2A6A"
    else // Unknown type
      return "#EB403B"
/*  
#E98931
#EB403B
#B32E37
#6C2A6A
#5C4399
#274389
#1F5EA8
#227FB0
#2AB0C5
#39C0B3
*/
  }

});
