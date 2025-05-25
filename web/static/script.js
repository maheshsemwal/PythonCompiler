// Initialize CodeMirror editor
const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
    mode: 'python',
    theme: 'monokai',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true,
    matchBrackets: true,
    autoCloseBrackets: true
});

// Set initial example code
editor.setValue(`def calculate():
    x = 5 + 3 * 2
    y = x - 4
    print("x =" + x + ", " +  "y =" + y)
    
    if x > 10:
        print("x is greater than 10")
    else:
        print("x is not greater than 10")
    
    return x + y

result = calculate()
print("Result"+  {result})`);

// Tree visualization variables
let astTreeData = null;
let svg = null;
let g = null;
let tree = null;
let root = null;

// Initialize tree visualization
function initializeTree() {
    const container = document.getElementById('ast-tree-container');
    
    // Clear previous tree
    d3.select('#ast-tree-container').selectAll('*').remove();
}

// Create tree visualization
function createTreeVisualization(data) {
    if (!data || data.length === 0) {
        d3.select('#ast-tree-container').html('<p class="text-muted p-3">No AST data to visualize</p>');
        return;
    }

    initializeTree();

    // Create a single root node if there are multiple top-level nodes
    let rootData;
    if (data.length === 1) {
        rootData = data[0];
    } else {
        rootData = {
            id: -1,
            name: 'Program',
            children: data
        };
    }

    root = d3.hierarchy(rootData);
    
    // Calculate tree dimensions based on the number of nodes
    const nodeCount = root.descendants().length;
    const width = Math.max(800, nodeCount * 50);
    const height = Math.max(600, nodeCount * 30);
    
    const margin = { top: 40, right: 40, bottom: 40, left: 40 };
    
    const container = document.getElementById('ast-tree-container');
    
    svg = d3.select('#ast-tree-container')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);    // Create tree layout with better spacing
    tree = d3.tree()
        .size([height, width])
        .separation((a, b) => {
            return (a.parent === b.parent ? 1.8 : 2.2);
        });

    // Initialize positions
    root.x0 = height / 2;
    root.y0 = 0;

    // Collapse nodes beyond second level initially
    function collapseAfterLevel(d, level = 0) {
        if (level > 1 && d.children) {
            d._children = d.children;
            d._children.forEach(child => collapseAfterLevel(child, level + 1));
            d.children = null;
        } else if (d.children) {
            d.children.forEach(child => collapseAfterLevel(child, level + 1));
        }
    }
    
    collapseAfterLevel(root);

    // Add zoom and pan functionality
    addZoomPan();

    update(root);
}

// Collapse function
function collapse(d) {
    if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
    }
}

// Update tree visualization
function update(source) {
    // Compute the new tree layout
    const treeData = tree(root);
    const nodes = treeData.descendants();
    const links = treeData.descendants().slice(1);    // Normalize for fixed-depth with better spacing
    nodes.forEach(d => d.y = d.depth * 220);

    // Update nodes
    const node = g.selectAll('g.node')
        .data(nodes, d => d.id || (d.id = ++i));

    // Enter new nodes at the parent's previous position
    const nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr('transform', d => `translate(${source.y0},${source.x0})`)
        .on('click', click);    // Add circles for nodes
    nodeEnter.append('circle')
        .attr('r', 1e-6)
        .style('fill', d => d._children ? '#3498db' : '#fff');

    // Add background rectangles for node values to improve readability
    nodeEnter.append('rect')
        .attr('class', 'value-background')
        .attr('x', -40)
        .attr('y', 14)
        .attr('width', 80)
        .attr('height', 12)
        .attr('rx', 2)
        .attr('ry', 2)
        .style('fill', 'rgba(248, 249, 250, 0.95)')
        .style('stroke', 'rgba(108, 117, 125, 0.2)')
        .style('stroke-width', 0.5)
        .style('opacity', d => d.data.value ? 1e-6 : 0);// Add labels for nodes with better positioning
    nodeEnter.append('text')
        .attr('class', 'node-label')
        .attr('dy', '-1.5em')
        .attr('text-anchor', 'middle')
        .text(d => {
            // Truncate long node names but keep them readable
            const name = d.data.name;
            return name.length > 18 ? name.substring(0, 15) + '...' : name;
        })
        .style('fill-opacity', 1e-6);

    // Add values for nodes (if available) with better positioning and styling
    nodeEnter.append('text')
        .attr('class', 'node-value')
        .attr('dy', '2.2em')
        .attr('text-anchor', 'middle')
        .text(d => {
            if (d.data.value) {
                const value = d.data.value.toString();
                // Better truncation for values
                if (value.length > 25) {
                    return value.substring(0, 22) + '...';
                }
                return value;
            }
            return '';
        })
        .style('fill-opacity', 1e-6);

    // Add tooltips with full information
    nodeEnter.append('title')
        .text(d => {
            let tooltip = `Type: ${d.data.name}`;
            if (d.data.value) {
                tooltip += `\nValue: ${d.data.value}`;
            }
            if (d._children) {
                tooltip += `\nChildren: ${d._children.length} (click to expand)`;
            } else if (d.children) {
                tooltip += `\nChildren: ${d.children.length} (click to collapse)`;
            }
            return tooltip;
        });

    // Transition nodes to their new position
    const nodeUpdate = nodeEnter.merge(node);    nodeUpdate.transition()
        .duration(600)
        .attr('transform', d => `translate(${d.y},${d.x})`);

    nodeUpdate.select('circle')
        .attr('r', 10)
        .style('fill', d => d._children ? '#3498db' : '#fff')
        .style('stroke', d => d._children ? '#2980b9' : '#3498db')
        .attr('cursor', 'pointer');

    // Update background rectangles
    nodeUpdate.select('.label-background')
        .style('opacity', 0.8);

    nodeUpdate.select('.value-background')
        .style('opacity', d => d.data.value ? 0.8 : 0);

    nodeUpdate.selectAll('text')
        .style('fill-opacity', 1);    // Transition exiting nodes to the parent's new position
    const nodeExit = node.exit().transition()
        .duration(600)
        .attr('transform', d => `translate(${source.y},${source.x})`)
        .remove();

    nodeExit.select('circle')
        .attr('r', 1e-6);

    nodeExit.selectAll('rect')
        .style('opacity', 1e-6);

    nodeExit.selectAll('text')
        .style('fill-opacity', 1e-6);

    // Update links
    const link = g.selectAll('path.link')
        .data(links, d => d.id);

    // Enter new links at the parent's previous position
    const linkEnter = link.enter().insert('path', 'g')
        .attr('class', 'link')
        .attr('d', d => {
            const o = { x: source.x0, y: source.y0 };
            return diagonal(o, o);
        });

    // Transition links to their new position
    const linkUpdate = linkEnter.merge(link);

    linkUpdate.transition()
        .duration(600)
        .attr('d', d => diagonal(d, d.parent));

    // Transition exiting links to the parent's new position
    const linkExit = link.exit().transition()
        .duration(600)
        .attr('d', d => {
            const o = { x: source.x, y: source.y };
            return diagonal(o, o);
        })
        .remove();

    // Store old positions for transition
    nodes.forEach(d => {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

// Create diagonal path
function diagonal(s, d) {
    return `M ${s.y} ${s.x}
            C ${(s.y + d.y) / 2} ${s.x},
              ${(s.y + d.y) / 2} ${d.x},
              ${d.y} ${d.x}`;
}

// Click event handler
function click(event, d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    update(d);
}

// Global variable for node IDs
let i = 0;

// View toggle functionality
document.getElementById('tree-view').addEventListener('change', function() {
    if (this.checked) {
        document.getElementById('ast-tree-container').style.display = 'block';
        document.getElementById('ast-text-output').style.display = 'none';
    }
});

document.getElementById('text-view').addEventListener('change', function() {
    if (this.checked) {
        document.getElementById('ast-tree-container').style.display = 'none';
        document.getElementById('ast-text-output').style.display = 'block';
    }
});

// Handle analyze button click
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const code = editor.getValue();
    const astTextOutput = document.getElementById('ast-text-output');
    const irOutput = document.getElementById('ir-output');
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    const errorMessage = document.getElementById('error-message');

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });

        const result = await response.json();

        if (result.success) {
            // Update AST text output
            astTextOutput.textContent = result.ast_text.join('\n');
            
            // Update AST tree visualization
            astTreeData = result.ast_tree;
            createTreeVisualization(astTreeData);
            addZoomPan(); // Add this line
            
            // Update IR output
            irOutput.textContent = result.ir.join('\n');
        } else {
            // Show error in modal
            errorMessage.textContent = result.error;
            errorModal.show();
        }
    } catch (error) {
        // Show error in modal
        errorMessage.textContent = 'An error occurred while processing the code.';
        errorModal.show();
    }
});

// Expand all nodes
function expandAll(d) {
    if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    if (d.children) {
        d.children.forEach(expandAll);
    }
}

// Collapse all nodes except root
function collapseAll(d, level = 0) {
    if (level > 0 && d.children) {
        d._children = d.children;
        d.children = null;
        d._children.forEach(child => collapseAll(child, level + 1));
    } else if (d.children) {
        d.children.forEach(child => collapseAll(child, level + 1));
    }
}

// Add event listeners for expand/collapse buttons
document.getElementById('expand-all-btn').addEventListener('click', function() {
    if (root) {
        expandAll(root);
        update(root);
    }
});

document.getElementById('collapse-all-btn').addEventListener('click', function() {
    if (root) {
        collapseAll(root);
        update(root);
    }
});

// Add keyboard shortcut (Ctrl+Enter) to analyze code
editor.setOption('extraKeys', {
    'Ctrl-Enter': () => {
        document.getElementById('analyze-btn').click();
    }
});

// Initialize with empty tree
document.addEventListener('DOMContentLoaded', function() {
    initializeTree();
});

// Add zoom and pan functionality
function addZoomPan() {
    const zoom = d3.zoom()
        .scaleExtent([0.3, 3])
        .on('zoom', function(event) {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);
    
    // Add reset zoom button
    const resetButton = d3.select('#ast-tree-container')
        .append('button')
        .attr('class', 'btn btn-sm btn-outline-secondary')
        .style('position', 'absolute')
        .style('top', '10px')
        .style('right', '10px')
        .style('z-index', '1000')
        .text('Reset Zoom')
        .on('click', function() {
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        });
}

// --- Resizable Gutters for Flex Panels ---
(function() {
    const container = document.getElementById('main-flex-container');
    if (!container) return;
    const panels = [
        document.getElementById('code-panel'),
        document.getElementById('ast-panel'),
        document.getElementById('ir-panel')
    ];
    const gutters = Array.from(container.getElementsByClassName('gutter'));
    let isDragging = false;
    let startX = 0;
    let startWidths = [];
    let activeGutter = null;
    
    gutters.forEach((gutter, i) => {
        gutter.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startWidths = panels.map(panel => panel.getBoundingClientRect().width);
            activeGutter = i;
            document.body.style.cursor = 'col-resize';
            e.preventDefault();
        });
    });
    window.addEventListener('mousemove', (e) => {
        if (!isDragging || activeGutter === null) return;
        const dx = e.clientX - startX;
        // Adjust the width of the panels to the left and right of the gutter
        const leftPanel = panels[activeGutter];
        const rightPanel = panels[activeGutter + 1];
        const minWidth = 120;
        let newLeft = Math.max(minWidth, startWidths[activeGutter] + dx);
        let newRight = Math.max(minWidth, startWidths[activeGutter + 1] - dx);
        leftPanel.style.flex = `none`;
        rightPanel.style.flex = `none`;
        leftPanel.style.width = newLeft + 'px';
        rightPanel.style.width = newRight + 'px';
    });
    window.addEventListener('mouseup', () => {
        if (isDragging) {
            isDragging = false;
            activeGutter = null;
            document.body.style.cursor = '';
        }
    });
})();