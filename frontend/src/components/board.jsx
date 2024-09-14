import React, { useRef, useEffect } from 'react';
import * as PIXI from 'pixi.js';

const hexRadius = 50; // Adjust radius for hex size
const hexHeight = Math.sqrt(3) * hexRadius; // Height of the hexagon

const CatanBoard = ({ board }) => {
    const pixiContainer = useRef(null);

    useEffect(() => {
        const app = new PIXI.Application({
            view: pixiContainer.current,
            width: hexRadius * 10,
            height: hexHeight * 5,
        });

        const drawHex = (x, y, color) => {
            const hexagon = new PIXI.Graphics();
            hexagon.beginFill(color);
            hexagon.moveTo(hexRadius, 0);

            for (let i = 0; i < 6; i++) {
                hexagon.lineTo(
                    hexRadius * Math.cos((Math.PI / 3) * i),
                    hexRadius * Math.sin((Math.PI / 3) * i)
                );
            }
            hexagon.endFill();
            hexagon.x = x;
            hexagon.y = y;
            app.stage.addChild(hexagon);
        };

        const hexPositions = [
            [0, 0],
            [-1.5, 1],
            [1.5, 1],
            [-3, 2],
            [-1.5, 2],
            [0, 2],
            [1.5, 2],
            [-2.25, 3],
            [-0.75, 3],
            [0.75, 3],
            [2.25, 3],
            [-1.5, 4],
            [1.5, 4],
            [-1.5, 5],
            [1.5, 5],
            [0, 6],
            [0, 4.5],
            [0, 1.5],
            [0, 0],
        ];

        hexPositions.forEach((position, index) => {
            const { resource } = board.hexes[index];  // Get resource based on index
            const color = getColor(resource);
            const x = position[0] * hexRadius * 1.5; // Adjust for x position
            const y = position[1] * hexHeight + (position[0] % 2) * (hexHeight / 2); // Adjust for y position
            
            drawHex(x, y, color);
        });

        return () => {
            app.destroy(true, { children: true }); // Clean up the app on unmount
        };
    }, [board]);

    const getColor = (resource) => {
        const colors = {
            wood: 0x8B4513,
            brick: 0xCD5C5C,
            sheep: 0x7CFC00,
            wheat: 0xFFD700,
            ore: 0xA9A9A9,
        };
        return colors[resource] || 0xFFFFFF; // Default to white if not found
    };

    return <canvas ref={pixiContainer} />;
};

export default CatanBoard;
