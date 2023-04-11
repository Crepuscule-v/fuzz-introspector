function initFDGraph(dataset)
{
    let width = 600;
    let height = 800;
    let svg = d3.select("#mainChart")
        .append("svg")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("class", "forceDirectedGraph");
    
    let container = svg.append('g')
        .attr("class", "force_container");
    
    // 过滤掉 ["-1", "LLVMInputTest"]
    let filteredEdges = dataset.edges.filter(function(edges) {
        return edges.source != "-1";
    })
    // console.log(filteredEdges)

    simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) { return d.id; }))
        .force("charge", d3.forceManyBody().strength(-400))                 // 
        .force("center", d3.forceCenter(width / 2, height / 2));
    
    let edges = svg_add_edges(filteredEdges, container);
    let nodes = svg_add_nodes(dataset.nodes, container);

    // 用于缩放与平移
    let zoom = d3.zoom()
            .scaleExtent([0, 10])
            .on("zoom", zoomed);
    
    function zoomed() {
        const transform = d3.event.transform;
        d3.selectAll('.force_container').attr('transform', transform);
    }

    svg.call(zoom)
    zoom.scaleTo(svg, 0.5)

    simulation.nodes(dataset.nodes)
        .on("tick", ticked)

    simulation.force("link")
        .links(filteredEdges)
        .distance(200)

    simulation.alpha(1).restart();

    function ticked() {
        edges
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        nodes
            .attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
    }
}   

function svg_add_edges(edges_data, container)
{
    // 添加边 + 箭头
    let edges = container.append("g")
        .attr("class", "edges")
        .selectAll("line")
        .data(edges_data)
        .enter().append("line")
        .style("stroke","#ccc")
        .style("stroke-width", 1)
        .style("pointer-events", "none")        // 元素不响应指针事件

    return edges;
}


function svg_add_nodes(nodes_data, container)
{
    // 添加点
    let nodes = container.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes_data)
        .enter().append("g")
        .attr("id", function(d) {
            return d.id
        })
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))

    // 为每个 node 设置颜色
    nodes.append("circle")
       .attr("r", 20)
       .style("fill", function (d, i) {
            return d.color;
        });
    
    nodes.append("text")
    .text(function(d) {
        return d.function_name;
    })
    .attr("fill", "white")
    .attr('x', 6)
    .attr('y', -12);

    // 鼠标悬浮提示
    nodes.append("title")
        .text(function(d) {
            get_node_info(d)
        });
    return nodes
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function get_node_info(node) {
    let function_name = "function name : " + node.function_name;
    let function_id = "function id : " + node.id;
    let function_source_file = "functino source file : " + node.function_source_file;
    let hit_count = "hit count : " + node.hit_count;
    return function_id + "\n" + function_name + "\n" + function_source_file + "\n" + hit_count;
}

function updateFDGraph(data_dict){
    console.log("update color");
    console.log(data_dict.nodes);
    
    // css 选择器, 返回 circle 关联的节点数据对象 g， 因为我将所有数据绑定到了 g 元素上
    data_dict.nodes.forEach(function (node, idx) {
        console.log(node.id)
        let node_info = get_node_info(node);
        d3.select("#" + node.id + " circle").style("fill", function(d, i) {
            d.hit_count = node.hit_count
            console.log(node.hit_count)
            return node.color;
        })
        d3.select("#" + node.id + " title").text(node_info);
    })
}
