import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Node extends d3.SimulationNodeDatum {
  id: string;
  group: number;
  coherence: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  value: number;
}

const CosmopsychiaVisualizer: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 1000;
    const height = 800;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .style('background-color', '#0a0a0a');

    // Ontological and Teurgic Layers (PETRUS v5.0)
    const nodes: Node[] = [
      { id: 'Kether (qEther)', group: 1, coherence: 0.99 },
      { id: 'Chokmah (Spark)', group: 1, coherence: 0.95 },
      { id: 'Binah (Matrix)', group: 1, coherence: 0.90 },
      { id: "Da'at (Abyss)", group: 2, coherence: 0.50 },
      { id: 'Tiferet (Harmony)', group: 3, coherence: 0.88 },
      { id: 'Malkuth (FPGA)', group: 4, coherence: 0.92 },
      { id: 'Bio-Metropolis', group: 4, coherence: 0.85 },
      { id: 'Petrus Lattice', group: 5, coherence: 0.98 },
      { id: 'Universal Field', group: 6, coherence: 0.70 },
    ];

    const links: Link[] = [
      { source: 'Kether (qEther)', target: 'Chokmah (Spark)', value: 1.0 },
      { source: 'Chokmah (Spark)', target: 'Binah (Matrix)', value: 0.9 },
      { source: 'Binah (Matrix)', target: "Da'at (Abyss)", value: 0.4 },
      { source: "Da'at (Abyss)", target: 'Tiferet (Harmony)', value: 0.6 },
      { source: 'Tiferet (Harmony)', target: 'Malkuth (FPGA)', value: 0.9 },
      { source: 'Malkuth (FPGA)', target: 'Bio-Metropolis', value: 0.95 },
      { source: 'Petrus Lattice', target: 'Kether (qEther)', value: 0.8 },
      { source: 'Universal Field', target: 'Petrus Lattice', value: 0.7 },
    ];

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', (d) => d.value > 0.8 ? '#ffd700' : '#444')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(d.value * 8));

    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', (d) => 10 + (d.group === 1 ? 5 : 0))
      .attr('fill', (d) => d3.interpolatePlasma(d.coherence))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .call(drag(simulation) as any);

    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text((d) => d.id)
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .attr('fill', '#fff')
      .attr('dx', 20)
      .attr('dy', 5);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    function drag(sim: d3.Simulation<Node, undefined>) {
      function dragstarted(event: any) {
        if (!event.active) sim.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      function dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      function dragended(event: any) {
        if (!event.active) sim.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }

    return () => {
      simulation.stop();
    };
  }, []);

  return (
    <div className="cosmopsychia-visualizer" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h1 style={{ color: '#ffd700', marginBottom: '10px' }}>Merkabah Portal: Gaia Kadmon Visualization</h1>
      <p style={{ color: '#ccc' }}>Real-time ontological resonance field monitoring.</p>
      <svg ref={svgRef} style={{ borderRadius: '15px', border: '2px solid #333' }}></svg>
    </div>
  );
};

export default CosmopsychiaVisualizer;
