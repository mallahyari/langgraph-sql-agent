import React, { useEffect, useRef } from 'react';
import embed from 'vega-embed';

interface VisualizationRendererProps {
    spec: any;
}

export const VisualizationRenderer: React.FC<VisualizationRendererProps> = ({ spec }) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current && spec) {
            embed(containerRef.current, spec, { actions: false }).catch(console.error);
        }
    }, [spec]);

    if (!spec) return null;

    return (
        <div className="w-full h-64 md:h-96 mt-4 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div ref={containerRef} className="w-full h-full" />
        </div>
    );
};
